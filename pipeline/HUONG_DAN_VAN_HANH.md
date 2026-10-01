# HƯỚNG DẪN VẬN HÀNH PIPELINE TỰ ĐỘNG HÓA KÊNH BĐS & QUY HOẠCH

Hệ thống được thiết kế theo đúng mô hình trong [sop_ban_giao_kenh_bds.md](../sop_ban_giao_kenh_bds.md) và [CLAUDE.md](../CLAUDE.md): **AI tự động hóa 80% khâu cào tin, soạn kịch bản, chuẩn hóa từ ngữ, xuất giọng đọc AI; Người kiểm soát 20% khâu chọn đề tài, kiểm chứng dữ kiện và chụp ảnh bản đồ 3D.**

---

## 1. CẤU TRÚC HỆ THỐNG PIPELINE

```
C:\BĐS\
├── 01_Radar_Tin_Tuc\             # Báo cáo tin nóng quét tự động mỗi sáng
├── 02_Kich_Ban_Bai_Viet\         # Bộ 4 file: Fact Sheet, Kịch bản video, Bài Fanpage, TTS
│   └── 2026-10-01\
├── 03_Anh_Tu_Lieu\               # Danh sách góc chụp Google Earth Pro & ảnh lưu trữ
│   └── 2026-10-01\
├── 04_Audio\                     # File giọng đọc AI thành phẩm (.mp3)
│   └── 2026-10-01\voice_doc_ai.mp3
│
├── pipeline\                     # Bộ mã nguồn tự động hóa
│   ├── config.py                 # Cấu hình nguồn tin, API Key, Voice
│   ├── scraper.py                # Cào nội dung bài báo chi tiết
│   ├── radar.py                  # Quét RSS lọc tin nóng, chấm điểm Hot
│   ├── generator.py              # AI sinh trọn bộ kịch bản tuân thủ CLAUDE.md
│   ├── tts_engine.py             # Xuất giọng đọc AI tốc độ cao (Edge-TTS)
│   ├── telegram_notifier.py      # Bắn tin thông báo vào nhóm chat
│   └── run_pipeline.py           # Điểm điều khiển trung tâm (CLI)
│
└── scripts\
    ├── run_morning_radar.bat     # File kích hoạt quét tin sáng 1-click
    └── setup_windows_scheduler.ps1 # Script hẹn giờ tự động trên Windows
```

---

## 2. CÁC LỆNH VẬN HÀNH HÀNG NGÀY

### Lệnh 1: Quét tin nóng buổi sáng (Radar)
Chạy lúc **6h30 sáng** để máy tự quét 5 kênh báo lớn (VnExpress, Tuổi Trẻ, CafeF, Báo Xây Dựng, Báo Đầu Tư) và chọn ra các tin tức có từ khóa quy hoạch/hạ tầng:
```powershell
python -m pipeline.run_pipeline --radar
```
*Kết quả:* Tạo báo cáo tại `01_Radar_Tin_Tuc/[YYYY-MM-DD]_Radar_Tin_Nong.md` và in Top 3 đề tài nổi bật nhất.

---

### Lệnh 2: Sản xuất trọn bộ nội dung từ 1 Link bài báo
Sau khi 3 anh em chốt 1 đề tài lúc 9h00, chỉ cần dán đường link bài báo vào lệnh sau:
```powershell
python -m pipeline.run_pipeline --url "https://tuoitre.vn/..."
```
*Hệ thống sẽ tự động thực hiện 3 bước:*
1. **BƯỚC 1:** Tải toàn bộ nội dung, thời gian đăng, tác giả bài viết.
2. **BƯỚC 2:** Gọi AI phân tích và tự động sinh 5 file:
   - `01_Bang_Du_Kien.md` (Fact Sheet phân loại mức tin cậy A/B/C)
   - `02_Kich_Ban_Video.md` (Kịch bản 5 cột chuẩn Hook - Proof - Insight - CTA)
   - `03_Bai_Fanpage.md` (Bài viết phân tích chuyên sâu 600-800 từ)
   - `04_Loi_Doc_TTS.txt` (Lời đọc chuẩn hóa số thành chữ cho AI)
   - `Danh_Sach_Anh_Can_Chup.md` (Danh sách 3-5 góc Google Earth 3D với vạch Đỏ/Vàng)
3. **BƯỚC 3:** Tự động chuyển `04_Loi_Doc_TTS.txt` thành file âm thanh `04_Audio/[ngày]/voice_doc_ai.mp3`.

---

### Lệnh 3: Xuất lại riêng file âm thanh (TTS) khi chỉnh sửa lời đọc
Nếu Bạn A hoặc Bạn B chỉnh sửa câu từ trong `04_Loi_Doc_TTS.txt` và muốn xuất lại file MP3:
```powershell
python -m pipeline.run_pipeline --tts --date "2026-10-01"
```

---

## 3. CÁCH TỰ ĐỘNG HÓA THEO KHUNG GIỜ CỐ ĐỊNH TRONG NGÀY

### Cách 1: Dùng Windows Task Scheduler (Khuyến nghị - Tự động 100% không cần mở Terminal)
Windows có sẵn trình lập lịch tác vụ hệ thống cực kỳ ổn định. Bạn có thể đăng ký tác vụ tự động chạy lúc **06:30 sáng** mỗi ngày bằng 1 lệnh PowerShell:

1. Mở PowerShell với quyền **Administrator** (Run as Administrator).
2. Chạy lệnh:
   ```powershell
   powershell -ExecutionPolicy Bypass -File C:\BĐS\scripts\setup_windows_scheduler.ps1
   ```
*Tác vụ `BDS_Radar_Morning_6h30` sẽ được tạo trong Windows Task Scheduler. Mỗi sáng đúng 6h30, máy sẽ tự động chạy quét tin và lưu sẵn báo cáo vào thư mục `01_Radar_Tin_Tuc/`.*

*(Nếu muốn mở giao diện đồ họa để chỉnh sửa giờ: Bấm phím `Windows + R`, gõ `taskschd.msc` rồi Enter, tìm task `BDS_Radar_Morning_6h30`).*

---

### Cách 2: Chạy chế độ Scheduler Daemon (Nếu máy tính luôn bật)
Bạn có thể mở một cửa sổ PowerShell riêng và để lệnh này chạy nền:
```powershell
python -m pipeline.run_pipeline --scheduler --time "06:30"
```
Cứ đúng **06:30 sáng**, tiến trình sẽ tự động đánh thức và kích hoạt Radar quét tin nóng.

---

## 4. TÍCH HỢP BÁO VỀ ĐIỆN THOẠI (TELEGRAM BOT - TÙY CHỌN)
Để tin nóng tự động "ting ting" về điện thoại của cả 3 anh em lúc 6h30 sáng:
1. Mở Telegram, chat với `@BotFather` để tạo bot và lấy `TOKEN`.
2. Lập 1 Group Telegram gồm 3 anh em và thêm bot vào group.
3. Lấy `CHAT_ID` của group.
4. Mở file [pipeline/config.py](file:///C:/B%C4%90S/pipeline/config.py) và điền:
   ```python
   TELEGRAM_BOT_TOKEN = "your_bot_token"
   TELEGRAM_CHAT_ID = "-100xxxxxxxxx"
   ```
*Khi đó, mỗi sáng sau khi máy quét xong, Bot sẽ tự động đẩy Top 3 đề tài kèm link bài viết vào nhóm chat.*
