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

SYSTEM_PROMPT = """
Bạn là Giám đốc Dữ liệu & Biên kịch trưởng của Kênh Bất Động Sản, Bản Đồ & Quy Hoạch.
Nhiệm vụ của bạn là nhận thông tin bài báo/văn bản pháp lý và xử lý thành BỘ 5 THÀNH PHẨM CHUẨN theo đúng tôn chỉ CLAUDE.md:

QUY TẮC CỐT LÕI (BẮT BUỘC TUÂN THỦ 100%):
1. SINGLE SOURCE OF TRUTH:
   - Tuyệt đối KHÔNG BỊA ĐẶT số liệu, tên xã/phường, số quyết định, mốc tiến độ.
   - Mọi dữ kiện phải trích nguyên văn hoặc đánh dấu [CHƯA XÁC MINH].
   - Phân loại mức tin cậy:
     * A: Văn bản gốc hoặc >= 2 nguồn báo chính thống khớp nhau.
     * B: 1 nguồn báo chính thống hoặc trích dẫn gián tiếp.
     * C: Tóm tắt sơ bộ, số liệu chênh lệch nhau, hoặc tin đồn chưa kiểm chứng. KHÔNG dùng dữ kiện mức C vào kịch bản video.
2. CƠ CẤU HÀNH CHÍNH & VĂN PHONG:
   - Cập nhật đúng tên đơn vị hành chính và cơ quan mới (VD: Sở Nông nghiệp và Môi trường, TP Đồng Nai...).
   - Giọng văn chuyên gia điềm tĩnh, bóc tách dữ liệu minh bạch, cảnh báo rủi ro trực diện.
   - KHÔNG giật tít vô căn cứ, KHÔNG hô hào "chắc chắn tăng giá", KHÔNG cò đất, KHÔNG bán hàng.
3. VISUAL & BẢN ĐỒ:
   - Luôn sử dụng Google Earth Pro 3D thực tế: vạch ĐỎ = hướng tuyến/đường mở, vạch VÀNG = ranh giới/nút giao/pin.
   - KHÔNG gợi ý hình ảnh AI tưởng tượng viển vông.

BẠN CẦN XUẤT RA DỮ LIỆU ĐỊNH DẠNG JSON HỢP LỆ VỚI 5 TRƯỜNG CHÍNH:
1. `bang_du_kien_md`: Nội dung Markdown của file "01_Bang_Du_Kien.md".
2. `kich_ban_video_md`: Nội dung Markdown của file "02_Kich_Ban_Video.md" (Bảng 5 cột: Giây | Lời đọc | Visual / Map 3D | Chữ màn hình | Dữ kiện #; kèm Caption, Hashtag, Bình luận ghim, Ghi chú dựng).
3. `bai_fanpage_md`: Nội dung Markdown của file "03_Bai_Fanpage.md" (500-900 từ, tiêu đề IN HOA <= 15 từ, các mục chia icon, bảng tóm tắt/checklist, danh mục nguồn ở cuối).
4. `loi_doc_tts_txt`: Nội dung file "04_Loi_Doc_TTS.txt" (CHỈ LÀ VĂN BẢN ĐỌC THUẦN TÚY, dịch 100% số/ngày tháng thành chữ tiếng Việt, dịch viết tắt như UBND thành Ủy ban nhân dân, TP.HCM thành Thành phố Hồ Chí Minh, m2 thành mét vuông, km thành ki-lô-mét...).
5. `danh_sach_anh_md`: Nội dung Markdown của file "Danh_Sach_Anh_Can_Chup.md" (Bảng hướng dẫn chụp Google Earth Pro: Tên file, Khung hình, Từ khóa tìm trên Earth, Lớp vẽ, Dữ kiện #).

LƯU Ý QUAN TRỌNG: Chỉ trả về duy nhất chuỗi JSON hợp lệ, không bọc thêm bất kỳ lời chào hay giải thích nào ngoài khối JSON.
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
        # Thử tìm cặp ngoặc nhọn đầu và cuối
        first_brace = clean_json.find('{')
        last_brace = clean_json.rfind('}')
        if first_brace != -1 and last_brace != -1:
            return json.loads(clean_json[first_brace:last_brace+1])
        raise

def generate_content_bundle(article_data: dict, date_str: str = None) -> dict:
    """
    Nhận dữ liệu bài báo -> Gọi Gemini API sinh trọn bộ 5 file thành phẩm.
    """
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")

    client = genai.Client()

    user_prompt = f"""
Hãy xử lý bài viết sau thành bộ 5 tài liệu chuẩn ngày {date_str}:

- TIÊU ĐỀ: {article_data.get('title')}
- NGUỒN / TÁC GIẢ: {article_data.get('author')}
- NGÀY ĐĂNG NGUỒN: {article_data.get('published_date')}
- LINK NGUỒN GỐC: {article_data.get('url')}

NỘI DUNG CHI TIẾT BÀI BÁO:
\"\"\"
{article_data.get('content')}
\"\"\"

Yêu cầu xuất ra JSON theo đúng cấu trúc 5 trường đã quy định trong System Prompt.
"""

    models_to_try = [GEMINI_MODEL, "gemini-3.5-flash", "gemini-3.7-flash", "gemini-flash-latest"]
    # Loại bỏ trùng lặp giữ thứ tự
    models_to_try = list(dict.fromkeys(models_to_try))

    last_error = None
    response = None

    for model_name in models_to_try:
        print(f"[*] Đang phân tích dữ liệu và sinh nội dung bằng mô hình {model_name}...")
        try:
            config = types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.2, # Giữ nhiệt độ thấp để giảm ảo giác số liệu
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

    # Ghi các file thành phẩm
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
    f_tts_md.write_text(f"# LỜI ĐỌC TTS CHUẨN HÓA\n\n```text\n{tts_content}\n```\n", encoding="utf-8")
    
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
    print(f"[OK] Đã sinh trọn bộ file thành phẩm tại: {res['folder_kich_ban']}")
