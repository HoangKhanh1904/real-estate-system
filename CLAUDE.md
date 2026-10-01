# AGENT SYSTEM RULES & WORKFLOW GUIDELINES

## 1. PROJECT OVERVIEW
Dự án phát triển kênh nội dung Dữ liệu BĐS, Bản đồ & Quy hoạch đa nền tảng (TikTok, Facebook Reels, Fanpage). 
Chiến lược cốt lõi: "Một đề tài - Đa điểm chạm".

## 2. CORE RULES (TỰ ĐỘNG TUÂN THỦ TẤT CẢ TÁC VỤ)
1. **SINGLE SOURCE OF TRUTH (Nguồn sự thật duy nhất):** 
   - KHÔNG ĐƯỢC TỰ SUY ĐOÁN hay bịa đặt con số, tên xã/phường, số tờ/thửa, số hiệu văn bản pháp lý.
   - Mọi dữ liệu phải trích dẫn kèm Link nguồn và ngày ban hành.
   - Nếu thông tin chưa xác minh, ghi rõ `[CHƯA XÁC MINH]`.

2. **CƠ CẤU HÀNH CHÍNH HIỆN HÀNH (Áp dụng từ 2025):**
   - Bắt buộc dùng tên đơn vị hành chính 2 cấp (tỉnh - xã, 34 tỉnh/thành).
   - Tên cơ quan đã hợp nhất (Bộ Nông nghiệp và Môi trường, Sở Nông nghiệp và Môi trường).
   - Nếu nguồn ghi tên cũ, hiển thị: `Tên mới (Tên cũ)`.

3. **GIỌNG VĂN & ĐỊNH VỊ KÊNH:**
   - Chuyên gia điềm tĩnh, phân tích dữ liệu minh bạch, cảnh báo rủi ro trực diện.
   - KHÔNG giật tít sai sự thật, KHÔNG hứa hẹn tăng giá/lợi nhuận ("chắc chắn tăng", "x2 tài sản"), KHÔNG kêu gọi mua bán.

4. **VISUAL & BẢN ĐỒ:**
   - Ưu tiên mô tả tọa độ, lớp màu quy hoạch (đỏ = tuyến đường, vàng = ranh giới) và bản đồ 3D thực tế thay vì ảnh AI tưởng tượng.
   - Luôn ghi nguồn: "Nguồn: Google Earth / [Văn bản gốc]".

## 3. WORKFLOW & SẢN PHẨM ĐẦU RA

Khi nhận đề tài hoặc link báo chí, luôn xử lý thành bộ 4 thành phẩm theo chuẩn SOP:

### Step 1: Bảng Dữ Kiện (Data Sheet)
Lập bảng dạng Markdown: `# | Dữ kiện | Trích nguyên văn | Link | Ngày | Mức tin cậy (A/B/C) | Trạng thái`.

### Step 2: Kịch Bản Video Ngắn (TikTok / Reels)
- Định dạng bảng 5 cột: `Giây | Lời đọc | Visual / Map 3D | Chữ màn hình | Dữ kiện #`.
- Cấu trúc: Hook (0-3s) -> Context & Proof -> Insight/Rủi ro -> CTA.
- Tốc độ đọc: ~2.7 từ/giây. Chuyển cảnh visual mỗi 2-3s.

### Step 3: Bài Viết Fanpage Chuyên Sâu (500 - 1000 từ)
- Tiêu đề IN HOA <= 15 chữ.
- 3-5 mục ngắn có icon, kèm checklist hướng dẫn hoặc bảng đối chiếu.
- Mục danh mục nguồn tham khảo ở cuối bài.

### Step 4: Chuẩn Hóa Lời Đọc Cho Giọng AI (TTS)
- Viết hoa/viết tắt phải dịch thành chữ đọc (VD: `UBND` -> `Ủy ban nhân dân`).
- Chuyển số/ngày tháng thành chữ (VD: `1/2000` -> `tỷ lệ một phần hai nghìn`).

## 4. BÀN GIAO & LƯU TRỮ GOOGLE DRIVE
- Cấu trúc thư mục tương ứng:
  - `02_Kich_Ban_Bai_Viet/[ngày]/`
  - `03_Anh_Tu_Lieu/[ngày]/`
  - `04_Audio/[ngày]/`