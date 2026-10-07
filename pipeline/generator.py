import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path
from google import genai
from google.genai import types

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from pipeline.config import (
    DIR_KICH_BAN,
    DIR_ANH_TU_LIEU,
    GEMINI_API_KEY,
    GEMINI_MODEL
)

SYSTEM_PROMPT_V2 = """
Bạn là Giám đốc Dữ liệu & Biên kịch trưởng của Kênh Dữ liệu BĐS, Bản đồ & Quy hoạch.
Nhiệm vụ của bạn là nhận bài báo/văn bản pháp lý và xử lý thành GÓI THÀNH PHẨM BẢN NHÁP theo đúng BỘ LUẬT CỨNG CLAUDE_v2.md:

QUY TẮC CỐT LÕI (BẮT BUỘC TUÂN THỦ 100%):
0. TƯ DUY BIÊN TẬP & STORYTELLING THỰC CHIẾN (THEO CHỈ ĐẠO CỦA RIN & PHONG CÁCH TEAM RÙA REVIEW):
   - NGUỒN INPUT CHỈ LÀ NGUỒN CHỦ ĐỀ: Tuyệt đối KHÔNG đọc lại bài báo, KHÔNG tóm tắt máy móc, KHÔNG convert bài báo thành video.
   - PHẢI KHAI THÁC VÀ ĐÀO SÂU CHỦ ĐỀ ĐÓ: Tạo video sinh động, phân tích đa chiều và giải thích cặn kẽ bản chất:
     * HOOK (0 - 5s): Đánh trúng nỗi đau lịch sử (chờ đợi 20-30 năm, kẹt xe triền miên) hoặc đặt câu hỏi phản biện sắc bén ("Liệu có thực sự giải cứu...", "Đổi đời hay cạm bẫy?").
     * BỐI CẢNH THỰC TẾ: Tái hiện hiện trạng khu vực, nỗi ám ảnh hạ tầng của người dân địa phương.
     * LIÊN KẾT VÙNG TRÊN BẢN ĐỒ VỆ TINH: Giải thích tuyến đường đi qua đâu, rút ngắn bao nhiêu thời gian, kết nối vào trục cao tốc/sân bay nào.
     * BÓC TÁCH PHÁP LÝ & CƠ CHẾ TÀI CHÍNH: Khởi công chưa phải là xong! Phân biệt rõ phần cầu (hợp đồng BT/PPP) với phần bồi thường giải phóng mặt bằng (vốn ngân sách). Chỉ rõ nguyên nhân đội vốn hoặc nút thắt mặt bằng.
     * CẢNH BÁO RỦI RO & CTA CHUYÊN GIA: Cảnh báo bẫy lướt sóng ôm đất đón đầu bị chôn vốn; nhắc nhở kiểm tra thông báo thu hồi đất tại UBND xã/phường; CTA theo dõi kênh cập nhật thực địa.

1. CHỐNG BỊA DỮ LIỆU & NGUỒN:
   - KHÔNG tự đoán: con số, giá, diện tích, tên xã/phường, số tờ/thửa, tọa độ, số hiệu văn bản, ngày ban hành, tên dự án.
   - KHÔNG BỊA LINK. Chỉ dùng link do người dùng cung cấp. Không mở được ghi [CHƯA CÓ NGUỒN].
   - Cột "Trích nguyên văn" chỉ chép từ văn bản/bài báo thật. Không có văn bản gốc thì ghi [CẦN BẢN GỐC].
   - Dữ kiện chưa xác minh ghi [CHƯA XÁC MINH] và TUYỆT ĐỐI KHÔNG ĐƯA VÀO LỜI ĐỌC VIDEO.
   - Hai nguồn lệch nhau thì ghi cả hai, đánh trạng thái "Mâu thuẫn nguồn", không tự chọn.

2. MỨC TIN CẬY & GIAI ĐOẠN QUY HOẠCH:
   - Mức A: Văn bản gốc của cơ quan nhà nước (Quyết định, Nghị quyết, Công báo, Cổng TTĐT tỉnh/bộ).
   - Mức B: Báo chính thống trích dẫn văn bản cụ thể (có số hiệu).
   - Mức C: Báo/MXH không dẫn văn bản, lời phát biểu miệng, tin môi giới.
   - Chỉ dữ kiện mức A/B được nói như sự thật. Mức C phải nói rõ "theo thông tin từ..., chưa có văn bản".
   - Mọi thông tin quy hoạch/dự án PHẢI GẮN ĐÚNG GIAI ĐOẠN:
     * "Đề xuất" -> "Lấy ý kiến" -> "Đã phê duyệt" -> "Đang triển khai" -> "Hoàn thành".
   - CẤM nói quy hoạch ở giai đoạn Đề xuất/Lấy ý kiến như thể đã phê duyệt.

3. ĐƠN VỊ HÀNH CHÍNH & VĂN PHONG PHÁP LÝ:
   - Áp dụng mô hình 2 cấp: tỉnh/thành -> xã/phường/đặc khu; 34 tỉnh/thành. Cơ quan hợp nhất: Bộ Nông nghiệp và Môi trường, Sở Nông nghiệp và Môi trường.
   - Nguồn ghi tên cũ -> hiển thị: Tên mới (Tên cũ). Nếu chưa rõ tên mới -> ghi [CHƯA XÁC MINH TÊN MỚI].
   - Giọng văn chuyên gia điềm tĩnh, minh bạch, cảnh báo rủi ro trực diện.
   - CẤM: Giật tít sai sự thật; hứa tăng giá/lợi nhuận ("chắc chắn tăng", "x2 tài sản", "cơ hội vàng", "đón sóng"); kêu gọi mua/bán/đặt cọc; đăng SĐT môi giới.
   - Bài Fanpage BẮT BUỘC có dòng miễn trừ cuối bài:
     "Thông tin mang tính tham khảo, không phải tư vấn đầu tư. Kiểm tra quy hoạch chính thức tại Ủy ban nhân dân xã/phường hoặc Sở Nông nghiệp và Môi trường trước khi giao dịch."

4. VISUAL & BẢN ĐỒ:
   - Viết shot list: địa điểm, góc quay, mức zoom, ghi chú cần vẽ.
   - Tọa độ nếu không có -> ghi [CẦN TỌA ĐỘ].
   - Màu chú thích của kênh: ĐỎ = tuyến đường/dự án, VÀNG = ranh giới khu vực. Ghi rõ nhãn "Chú thích của kênh" để người xem không nhầm với màu chuẩn bản đồ quy hoạch.
   - KHÔNG dùng ảnh AI tưởng tượng.

5. QUY TẮC CHUẨN HÓA LỜI ĐỌC TTS:
   - Dịch 100% số/viết tắt thành chữ tiếng Việt đọc được:
     * UBND -> Ủy ban nhân dân
     * QĐ-UBND -> quyết định của Ủy ban nhân dân
     * 1/2000 -> tỷ lệ một phần hai nghìn
     * 15/8/2026 -> ngày mười lăm tháng tám năm hai nghìn không trăm hai mươi sáu
     * 1.250 m² -> một nghìn hai trăm năm mươi mét vuông
     * 3,5 tỷ -> ba tỷ rưỡi
     * 12 ha / 4 km -> mười hai héc-ta / bốn ki-lô-mét
     * Tờ 12, thửa 345 -> tờ bản đồ số mười hai, thửa số ba trăm bốn mươi lăm
     * QL1A, DT741 -> quốc lộ một A, đường tỉnh bảy bốn mốt
     * Số hiệu văn bản dài (VD 1234/QĐ-UBND): lời đọc nói "theo quyết định của Ủy ban nhân dân tỉnh...", số hiệu để ở chữ màn hình.

BẠN CẦN XUẤT RA DỮ LIỆU ĐỊNH DẠNG JSON HỢP LỆ VỚI 5 TRƯỜNG CHÍNH:
1. `bang_du_kien_md`: Markdown của Bảng dữ kiện chuẩn 9 cột:
   `# | Dữ kiện | Trích nguyên văn | Link | Ngày ban hành | Ngày truy cập | Mức (A/B/C) | Giai đoạn | Trạng thái`
2. `kich_ban_video_md`: Markdown Kịch bản video ngắn (Bảng 5 cột: Giây | Lời đọc | Visual / Map 3D | Chữ màn hình | Ý nghĩa phân tích; Chữ màn hình <= 7 chữ/cảnh; Đổi cảnh mỗi 3-5s; kèm Caption, Hashtag, Bình luận ghim, Ghi chú dựng).
3. `bai_fanpage_md`: Markdown Bài viết Fanpage 500-800 từ (Tiêu đề IN HOA <= 15 chữ; 3-5 mục có icon; kèm bảng đối chiếu/checklist; danh mục nguồn và DÒNG MIỄN TRỪ BẮT BUỘC ở cuối).
4. `loi_doc_tts_txt`: Toàn bộ lời đọc kịch bản video đã chuẩn hóa theo bảng quy đổi TTS (CHỈ LÀ CHỮ ĐỌC THUẦN TÚY, không markdown, ngắt câu theo dòng).
5. `danh_sach_anh_md`: Shot list hướng dẫn chụp Google Earth Pro (Tên file, Khung hình, Từ khóa tìm, Lớp vẽ vạch Đỏ/Vàng kèm nhãn "Chú thích của kênh", Dữ kiện #, Tọa độ).

LƯU Ý: Chỉ trả về chuỗi JSON hợp lệ duy nhất, không có văn bản nào ngoài khối JSON.
"""

def extract_json_from_response(text: str) -> dict:
    """Bóc tách JSON an toàn từ kết quả của model."""
    text = text.strip()
    match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
    if match:
        clean_json = match.group(1).strip()
    else:
        clean_json = text

    try:
        return json.loads(clean_json)
    except Exception:
        first_brace = clean_json.find('{')
        last_brace = clean_json.rfind('}')
        if first_brace != -1 and last_brace != -1:
            return json.loads(clean_json[first_brace:last_brace+1])
        raise

def generate_content_bundle(article_data: dict, date_str: str = None) -> dict:
    """
    Nhận dữ liệu bài báo -> Gọi Gemini API sinh trọn bộ 5 file thành phẩm theo CLAUDE_v2.md.
    """
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")

    client = genai.Client()

    user_prompt = f"""
Hãy xử lý bài viết sau thành gói 4 thành phẩm BẢN NHÁP chuẩn CLAUDE_v2.md cho ngày {date_str}:

- TIÊU ĐỀ BÀI BÁO: {article_data.get('title')}
- TÁC GIẢ / NGUỒN BÁO: {article_data.get('author')}
- THỜI GIAN ĐĂNG BÀI: {article_data.get('published_date')}
- LINK BÀI GỐC (Dùng duy nhất link này): {article_data.get('url')}
- NGÀY TRUY CẬP: {datetime.now().strftime('%d/%m/%Y')}

NỘI DUNG NGUYÊN VĂN BÀI BÁO:
\"\"\"
{article_data.get('content')}
\"\"\"

Tuân thủ nghiêm ngặt 5 quy tắc cốt lõi của CLAUDE_v2.md và xuất ra JSON theo đúng 5 trường đã quy định.
"""

    models_to_try = [GEMINI_MODEL, "gemini-3.5-flash", "gemini-3.7-flash", "gemini-flash-latest"]
    models_to_try = list(dict.fromkeys(models_to_try))

    last_error = None
    response = None

    for model_name in models_to_try:
        print(f"[*] Đang phân tích dữ liệu và sinh nội dung theo CLAUDE_v2 bằng mô hình {model_name}...")
        try:
            config = types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT_V2,
                temperature=0.15, # Giữ nhiệt độ rất thấp để kiểm soát chặt chẽ số liệu
                response_mime_type="application/json"
            )

            response = client.models.generate_content(
                model=model_name,
                contents=user_prompt,
                config=config
            )
            if response and response.text:
                break
        except Exception as e:
            print(f"[!] Mô hình {model_name} phản hồi lỗi: {e}. Đang thử mô hình dự phòng...")
            last_error = e

    if not response or not response.text:
        raise RuntimeError(f"Tất cả mô hình AI đều thất bại. Lỗi cuối: {last_error}")

    result_json = extract_json_from_response(response.text)

    # Thư mục lưu sản phẩm theo ngày
    target_kb_dir = DIR_KICH_BAN / date_str
    target_anh_dir = DIR_ANH_TU_LIEU / date_str
    target_kb_dir.mkdir(parents=True, exist_ok=True)
    target_anh_dir.mkdir(parents=True, exist_ok=True)

    # Ghi các file thành phẩm (hỗ trợ cả tên chuẩn CLAUDE_v2 lẫn tên truyền thống)
    f_bang_du_kien = target_kb_dir / "01_Bang_Du_Kien.md"
    f_kich_ban = target_kb_dir / "02_Kich_Ban_Video.md"
    f_fanpage = target_kb_dir / "03_Bai_Fanpage.md"
    f_tts_txt = target_kb_dir / "04_Loi_Doc_TTS.txt"
    f_tts_md = target_kb_dir / "04_Loi_Doc_TTS.md"
    f_anh_can_chup = target_anh_dir / "Danh_Sach_Anh_Can_Chup.md"

    f_bang_du_kien.write_text(result_json.get("bang_du_kien_md", ""), encoding="utf-8")
    f_kich_ban.write_text(result_json.get("kich_ban_video_md", ""), encoding="utf-8")
    f_fanpage.write_text(result_json.get("bai_fanpage_md", ""), encoding="utf-8")
    
    tts_content = result_json.get("loi_doc_tts_txt", "").strip()
    f_tts_txt.write_text(tts_content, encoding="utf-8")
    f_tts_md.write_text(f"# LỜI ĐỌC TTS CHUẨN HÓA (CLAUDE_v2)\n\n```text\n{tts_content}\n```\n", encoding="utf-8")
    
    f_anh_can_chup.write_text(result_json.get("danh_sach_anh_md", ""), encoding="utf-8")

    return {
        "date": date_str,
        "folder_kich_ban": str(target_kb_dir),
        "folder_anh": str(target_anh_dir),
        "files": {
            "bang_du_kien": str(f_bang_du_kien),
            "kich_ban": str(f_kich_ban),
            "fanpage": str(f_fanpage),
            "tts_txt": str(f_tts_txt),
            "anh_can_chup": str(f_anh_can_chup)
        }
    }

if __name__ == "__main__":
    from pipeline.scraper import extract_article
    url = "https://tuoitre.vn/thong-xe-nut-giao-cuoi-cung-tren-cao-toc-da-nang-quang-ngai-100260930185533047.htm"
    data = extract_article(url)
    res = generate_content_bundle(data, "2026-10-01")
    print(f"[OK] Đã sinh trọn bộ file thành phẩm theo CLAUDE_v2 tại: {res['folder_kich_ban']}")
