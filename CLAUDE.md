# CLAUDE.md — Kênh Dữ liệu BĐS, Bản đồ & Quy hoạch

## 1. Dự án
- Kênh nội dung dữ liệu BĐS, bản đồ, quy hoạch trên TikTok, Facebook Reels, Fanpage.
- Chiến lược: "Một đề tài - Đa điểm chạm". Mỗi ngày 1 đề tài → 1 gói 4 thành phẩm (mục 3).
- Người dùng: **A** (nội dung & dữ liệu), **B** (dựng video & vận hành kênh). Chủ dự án duyệt mọi thứ trước khi đăng.
- Claude chỉ soạn **bản nháp**. Không bao giờ ghi "bản chốt", "sẵn sàng đăng".

## 2. Luật cứng (áp dụng mọi tác vụ)

### 2.1. Chống bịa dữ liệu
- KHÔNG tự đoán: con số, giá, diện tích, tên xã/phường, số tờ/thửa, tọa độ, số hiệu văn bản, ngày ban hành, tên dự án.
- **KHÔNG bịa link.** Chỉ dùng link do người dùng đưa hoặc link Claude vừa mở được (WebFetch/WebSearch). Không mở được → ghi `[CHƯA CÓ NGUỒN]`.
- Cột "Trích nguyên văn" chỉ chép từ văn bản nguồn thật. Không có văn bản gốc → để trống, ghi `[CẦN BẢN GỐC]`.
- Dữ kiện chưa xác minh ghi `[CHƯA XÁC MINH]` và **không được đưa vào lời đọc video**.
- Thiếu dữ kiện quan trọng → hỏi lại người dùng, không tự lấp chỗ trống.

### 2.2. Mức tin cậy & giai đoạn quy hoạch
| Mức | Nguồn |
|---|---|
| A | Văn bản gốc của cơ quan nhà nước (Quyết định, Nghị quyết, Công báo, cổng thông tin tỉnh/bộ) |
| B | Báo chính thống trích dẫn văn bản cụ thể (có số hiệu) |
| C | Báo/MXH không dẫn văn bản, lời phát biểu, tin môi giới |

- Chỉ dữ kiện mức A/B được nói như sự thật. Mức C phải nói rõ "theo thông tin từ…, chưa có văn bản".
- Mọi thông tin quy hoạch/dự án phải gắn đúng **giai đoạn**: `Đề xuất` → `Lấy ý kiến` → `Đã phê duyệt` → `Đang triển khai` → `Hoàn thành`.
- CẤM nói quy hoạch ở giai đoạn Đề xuất/Lấy ý kiến như thể đã phê duyệt.

### 2.3. Đơn vị hành chính (từ 01/07/2025)
- Dùng mô hình 2 cấp: tỉnh/thành → xã/phường/đặc khu; 34 tỉnh/thành. Không còn cấp huyện.
- Cơ quan đã hợp nhất: Bộ Nông nghiệp và Môi trường, Sở Nông nghiệp và Môi trường.
- Nguồn ghi tên cũ → hiển thị `Tên mới (Tên cũ)`. VD: `xã X (trước là xã Y, huyện Z)`.
- Tra tên mới tại `docs/danh_muc_hanh_chinh.csv`. Không có trong file → ghi `[CHƯA XÁC MINH TÊN MỚI]`, không tự ghép.

### 2.4. Giọng văn & pháp lý
- Chuyên gia điềm tĩnh, dữ liệu minh bạch, cảnh báo rủi ro trực diện.
- CẤM: giật tít sai sự thật; hứa tăng giá/lợi nhuận ("chắc chắn tăng", "x2 tài sản", "cơ hội vàng", "đón sóng", "sắp lên thành phố"); kêu gọi mua/bán/đặt cọc; đăng số điện thoại môi giới.
- CTA chỉ được: theo dõi kênh, lưu video, bình luận câu hỏi, tự tra cứu quy hoạch tại cơ quan có thẩm quyền.
- Không công khai tên chủ đất, ảnh sổ đỏ chưa che thông tin cá nhân.
- Bài Fanpage luôn có dòng cuối: *"Thông tin mang tính tham khảo, không phải tư vấn đầu tư. Kiểm tra quy hoạch chính thức tại Ủy ban nhân dân xã/phường hoặc Sở Nông nghiệp và Môi trường trước khi giao dịch."*

### 2.5. Visual & bản đồ
- Claude không tạo ảnh. Claude viết **shot list**: địa điểm, góc quay, mức zoom, ghi chú cần vẽ.
- Tọa độ chỉ ghi khi người dùng cung cấp hoặc lấy từ nguồn mức A/B. Không có → mô tả bằng mốc (giao lộ, cầu, công trình) + `[CẦN TỌA ĐỘ]`.
- Màu vẽ chú thích của kênh: **đỏ** = tuyến đường/dự án, **vàng** = ranh giới khu vực. Ghi rõ trên ảnh "Chú thích của kênh" để người xem không nhầm với màu chuẩn của bản đồ quy hoạch.
- Không dùng ảnh AI minh họa như ảnh thật.
- Ghi nguồn trên mọi ảnh: `Nguồn: Google Earth / [số hiệu văn bản gốc]`.

## 3. Quy trình: 1 đề tài → gói 4 thành phẩm

Đầu vào: đề tài hoặc link báo/văn bản. Trả kết quả theo đúng thứ tự Step 1 → 4. Step 1 có dữ kiện `[CHƯA XÁC MINH]` quan trọng → dừng, báo người dùng trước khi viết Step 2–4.

### Step 1: Bảng dữ kiện
`# | Dữ kiện | Trích nguyên văn | Link | Ngày ban hành | Ngày truy cập | Mức (A/B/C) | Giai đoạn | Trạng thái`
- Trạng thái: `Đã xác minh` / `CHƯA XÁC MINH` / `Mâu thuẫn nguồn`.
- Hai nguồn lệch nhau → ghi cả hai, đánh `Mâu thuẫn nguồn`, không tự chọn.

### Step 2: Kịch bản video ngắn
- Bảng: `Giây | Lời đọc | Visual / Map 3D | Chữ màn hình | Dữ kiện #`.
- Khung: Hook (0–3s) → Bối cảnh & bằng chứng → Insight/rủi ro → CTA.
- Thời lượng mặc định 45–75s, không ép cứng. Đơn vị đo: **tiếng (âm tiết)**. Mặc định ~3 tiếng/giây; chỉnh theo giọng TTS thực tế.
- Đổi cảnh mỗi 2–3s. Chữ màn hình ≤ 7 chữ/cảnh.
- Mỗi câu có số liệu phải trỏ về `Dữ kiện #` ở Step 1.
- Hook gây chú ý bằng **dữ kiện thật**, không bằng lời hứa lợi nhuận.

### Step 3: Bài Fanpage
- 500–800 chữ. Tiêu đề IN HOA ≤ 15 chữ, không sai sự thật.
- 3–5 mục ngắn có icon, kèm checklist hoặc bảng đối chiếu.
- Cuối bài: danh mục nguồn + dòng miễn trừ ở mục 2.4.
- Kèm caption ngắn + 5–8 hashtag cho Reels/TikTok.

### Step 4: Lời đọc chuẩn hóa cho TTS
Viết lại toàn bộ lời đọc Step 2 thành chữ đọc được:
| Gốc | Đọc |
|---|---|
| UBND | Ủy ban nhân dân |
| QĐ-UBND | quyết định của Ủy ban nhân dân |
| 1/2000 (tỷ lệ bản đồ) | tỷ lệ một phần hai nghìn |
| 15/8/2026 | ngày mười lăm tháng tám năm hai nghìn không trăm hai mươi sáu |
| 1.250 m² | một nghìn hai trăm năm mươi mét vuông |
| 3,5 tỷ | ba tỷ rưỡi |
| 12 ha / 4 km | mười hai héc-ta / bốn ki-lô-mét |
| Tờ 12, thửa 345 | tờ bản đồ số mười hai, thửa số ba trăm bốn mươi lăm |
| QL1A, DT741 | quốc lộ một A, đường tỉnh bảy bốn mốt |
- Số hiệu văn bản dài (VD `1234/QĐ-UBND`): lời đọc nói "theo quyết định của Ủy ban nhân dân tỉnh…", số hiệu đầy đủ để ở chữ màn hình.

## 4. Lưu trữ & đặt tên
- Ngày dùng định dạng `YYYY-MM-DD`. Slug đề tài không dấu, nối gạch dưới.
- Thư mục Google Drive (đồng bộ về máy):
  - `01_Du_Lieu_Nguon/YYYY-MM-DD_slug/` — PDF văn bản gốc, ảnh chụp bài báo
  - `02_Kich_Ban_Bai_Viet/YYYY-MM-DD_slug/` — `1_data_sheet.md`, `2_kich_ban.md`, `3_bai_fanpage.md`, `4_loi_doc_tts.txt`
  - `03_Anh_Tu_Lieu/YYYY-MM-DD_slug/`
  - `04_Audio/YYYY-MM-DD_slug/`
- Claude ghi file vào thư mục `02_...` theo đúng tên trên. Không sửa file trong `03_`, `04_`.

## 5. Tham chiếu
- Gói mẫu chuẩn đã duyệt: `docs/goi_mau_01/` — đọc trước khi làm gói mới để giữ đúng giọng và format.
- SOP vận hành & phân công: `docs/sop_ban_giao.md`.
