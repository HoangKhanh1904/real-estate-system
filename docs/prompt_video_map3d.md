# Phân tích video mẫu & Prompt chuẩn dựng video "Map 3D" (BẢN NHÁP, v2)

> Video tham chiếu: https://www.tiktok.com/@trinhnguyenv/video/7692952933880679688
> Phân tích ngày 2026-10-06 (tải video, cắt khung 2s/lần, chép lời bằng faster-whisper).
> Mục đích: học **format**, không sao chép nội dung, hình hay thương hiệu của kênh khác.

---

## 1. Thông số video mẫu

| Hạng mục | Giá trị |
|---|---|
| Tiêu đề | "Vành đai 3 bao giờ xong? #vanhdai3 #viral" |
| Đăng | 2026-10-04 · sau ~2 ngày: 102.000 view, 1.487 like, 98 bình luận, 180 share |
| Định dạng | 1080×1920 (9:16), 30 fps, dài **2 phút 17 giây** |
| Âm thanh | Chỉ có giọng đọc (âm thanh gốc), không nhạc nền nổi bật |
| Lời đọc | ~446 tiếng / 137s ≈ **3,3 tiếng/giây**, nghỉ 0,5–1s giữa các câu |
| Cắt cảnh cứng | Chỉ ~7 lần. Phần còn lại là **camera bay liên tục** trên một bản đồ duy nhất |
| Nguồn dữ liệu | Một nguồn chính duy nhất: "Báo cáo Chính phủ gửi Quốc hội (Dân trí 3/10/2026)", ghi ở chân mọi khung hình |

## 2. Cấu trúc kịch bản (timeline thật)

| Giây | Phần | Nội dung | Kỹ thuật |
|---|---|---|---|
| 0–6 | **Hook** | Bong bóng "Trả lời bình luận: Vành đai 3 bao giờ xong ạ?" + chữ đỏ lớn "4 LẦN LỠ HẸN" + 4 ngày bị gạch | Câu hỏi của khán giả + con số gây sốc, nhưng là **dữ kiện thật** |
| 6–10 | Giữ chân | "Xem tới cuối nhé" · toàn vòng hơn 90 km | Hứa sẽ có câu trả lời ở cuối |
| 10–20 | Tổng quan | Thẻ KPI hiện lần lượt: 76,34 km · 75.300 tỷ · ~81% | Thẻ số liệu trồi lên từng ô, đồng bộ với lời đọc |
| 20–24 | Chuyển | "Mình đi một vòng, xem đoạn nào xong trước" | Tuyến đổi từ trắng sang màu theo trạng thái |
| 24–99 | **Thân: 8 đoạn × ~9s** | Đoạn 1/8 → 8/8: tên đoạn, điểm đầu→cuối, km, %, trạng thái | Camera bay theo tuyến, có icon xe chạy dọc đường, thẻ đoạn đổi ở góc trên |
| 44–56 | Cao trào giữa video | 4 ngày hẹn bị gạch lần lượt → "4 LẦN LỠ HẸN" → "MỐC MỚI (DỰ KIẾN) THÁNG 11/2026" | Lặp lại hook để trả lời |
| 100–121 | **Trả lời** | Timeline 3 mốc: 11/2026 · trong năm 2026 · Quý I/2027 → hộp đỏ "CHƯA CÓ NGÀY THÔNG XE TOÀN TUYẾN" | Thu camera về toàn cảnh |
| 121–126 | Ý nghĩa | Nối cao tốc Bến Lức – Long Thành tại Mỹ Yên và Nhơn Trạch | Tô sáng tuyến kết nối |
| 126–137 | CTA | "Bạn chờ đoạn nào nhất? Bình luận…" + "Theo dõi [kênh]" | CTA hỏi ý kiến → kéo bình luận |

**Vì sao video này hiệu quả:**
1. Hook là **câu hỏi thật của khán giả** + **con số kiểm chứng được** (4 lần lỡ hẹn). Không cần giật tít.
2. Có một "lời hứa trả lời" ở giây 0, và chỉ trả lời ở giây 100 → người xem ở lại hết video.
3. Cấu trúc "1/8 … 8/8" có tiến độ rõ ràng, người xem biết mình đang ở đâu và còn bao nhiêu.
4. **Một bản đồ, một bảng màu xuyên suốt**: chú thích không đổi, người xem đọc màu là hiểu ngay.
5. Phân biệt rõ "đã xảy ra" và "dự kiến": nhãn `DỰ KIẾN`, câu "các mốc tương lai là dự kiến" ở chân khung hình, badge `MÔ PHỎNG`.
6. Giải thích được một điểm gây tranh cãi (92 km hay 76 km) → tạo giá trị "lần đầu hiểu ra".

## 3. Hệ thống hình ảnh

### 3.1. Bố cục cố định (khung 1080×1920)
```
┌──────────────────────────────┐
│ [Thẻ đoạn] 1/8 · TÊN ĐOẠN    │  y≈ 70–180    Thẻ đoạn + chip (km, %, trạng thái)
│ (~11 km)(78,8%)(DỰ KIẾN 2026)│  y≈ 190–230
│ [Hộp thông tin phụ khi cần]  │  y≈ 200–420   Ngày bị gạch, KPI, timeline
│                              │
│      BẢN ĐỒ VỆ TINH 3D       │  Tuyến ở khoảng giữa, nghiêng ~45°
│      tuyến + xe chạy + pin   │
│                              │
│ [Chú thích 5 màu]            │  y≈ 960–1020
│ Nguồn · các mốc là dự kiến   │  y≈ 1040
│   Phụ đề trắng 1–2 dòng      │  y≈ 1070–1130 (không hộp, có viền tối)
│                              │
│ Tên kênh [MÔ PHỎNG]          │  y≈ 1230
│ Ảnh vệ tinh © … · Bản đồ © … │  y≈ 1260
└──────────────────────────────┘
```

### 3.2. Bản đồ & camera
- Nền: ảnh vệ tinh tối, bão hòa thấp (đã giảm sáng ~30–40%) để tuyến màu nổi lên.
- **Góc nghiêng (pitch) ~40–50°**, xoay (bearing) theo hướng tuyến → cảm giác 3D/flycam.
- Camera **bay liên tục** từ đoạn này sang đoạn kế (ease in-out ~2–3s), zoom vào đoạn đang nói, cuối video thu về toàn cảnh.
- Icon xe (vòng tròn trắng có xe) chạy dọc tuyến, có quầng sáng.
- Pin điểm mốc: chấm tròn + nhãn hộp tối viền màu, 2 dòng (tên đậm + mô tả nhỏ).
- Khu đô thị/công trình làm mốc: tô viền xanh nhạt (VD Vinhomes Grand Park).
- Tuyến liên quan (cao tốc khác): vàng mảnh hơn, tô đậm khi lời đọc nhắc tới.

### 3.3. Mã màu trạng thái (video mẫu)
| Màu | Ý nghĩa |
|---|---|
| Xanh lá | Đang cho xe chạy |
| Xám/trắng | Đường có sẵn (không thuộc dự án) |
| Vàng | Dự kiến 11/2026 |
| Cam | Dự kiến cuối 2026 |
| Đỏ | Một phần lùi sang Quý I/2027 |

### 3.4. Chữ & thẻ
- Font sans-serif đậm kiểu SF Pro/Inter (máy Windows: Segoe UI Bold hoặc Be Vietnam Pro).
- Thẻ đoạn: nền navy gần đen (~#12141F, 90% đục), vạch màu trạng thái ở cạnh trái, huy hiệu tròn "n/8" cùng màu.
- Chip: viền trắng/xám cho số liệu; nền màu cho trạng thái.
- Tiêu đề cảnh báo: chữ đỏ in hoa cỡ lớn, viền tối. Ngày đã lỡ: hộp viền trắng + **gạch đỏ chéo** + chữ "Lỡ" đỏ.
- Phụ đề: chữ trắng đậm ~36px, tối đa 2 dòng, không có hộp nền, hiện theo từng câu.
- Hiệu ứng: thẻ/chip **fade + trượt lên** 0,3s; số liệu hiện lần lượt; ngày bị gạch theo nhịp lời đọc.

## 4. Đối chiếu với luật kênh (CLAUDE.md), cần chủ dự án quyết

| # | Điểm lệch | Video mẫu | Luật kênh | Đề xuất |
|---|---|---|---|---|
| 1 | Màu | 5 màu theo **trạng thái** | Đỏ = tuyến/dự án, vàng = ranh giới | **Cần chủ dự án quyết**: (a) giữ luật cũ, chỉ dùng độ đậm/nét đứt; hoặc (b) bổ sung luật "bảng màu trạng thái" + ghi "Chú thích của kênh" trên legend |
| 2 | Thời lượng | 137s | Mặc định 45–75s, không ép cứng | Đề tài nhiều đoạn → cho phép 90–140s; đề tài thường giữ 60s |
| 3 | Tên hành chính | "Long An cũ", "Bình Dương cũ" | `Tên mới (Tên cũ)` | Viết theo luật kênh, VD "Tây Ninh (trước là Long An)" |
| 4 | Nguồn | Chỉ một báo (mức B) | Mức A/B mới được nói như sự thật | Phù hợp nếu báo dẫn đúng văn bản; nên kèm số hiệu báo cáo gốc |
| 5 | Tọa độ tuyến | Vẽ từ OpenStreetMap | Tọa độ chỉ lấy từ người dùng hoặc nguồn A/B | **Cần quyết**: OSM chỉ dùng để *vẽ minh họa* (có badge MÔ PHỎNG), không dùng làm căn cứ ranh giới? |
| 6 | Kỹ thuật | Bản đồ 3D bay camera | `pipeline/video_maker.py` chỉ ghép ảnh tĩnh bằng PIL + zoom | Cần thêm bước render bản đồ (MapLibre GL + Playwright quay từng khung → ffmpeg) |

---

## 5. PROMPT CHUẨN (v2, dùng cho mọi dự án)

> Cách dùng: copy toàn bộ khối dưới, chỉ điền các dòng có dấu `*` trong phần "NGƯỜI DÙNG ĐIỀN".
> Claude tự tra cứu phần còn lại.
> Ví dụ đã điền: `02_Kich_Ban_Bai_Viet/2026-09-30/00_prompt_map3d.md` (cầu Cát Lái, cầu Long Hưng).

### 5.1. Việc chủ dự án cần quyết (prompt đang dùng mặc định trong ngoặc)

| # | Câu hỏi | Mặc định cho tới khi quyết |
|---|---|---|
| 1 | Bảng màu: giữ luật kênh, hay thêm bảng màu theo trạng thái? | Luật kênh: đỏ = tuyến/dự án, vàng = ranh giới; phân biệt trạng thái bằng nét liền/đứt |
| 2 | Có được dùng OpenStreetMap để vẽ minh họa hình tuyến (kèm nhãn MÔ PHỎNG) không? | **ĐÃ DUYỆT (theo người dùng báo, 2026-10-06):** dùng được để MINH HỌA, mức C. Thứ tự ưu tiên: KML do người dùng vẽ theo văn bản → nguồn A/B → OSM. Khi dùng phải: ghi way id + ngày truy vấn vào `source`, lưu GeoJSON vào `01_Du_Lieu_Nguon/`, ghi "© OpenStreetMap contributors (minh họa)" ở chân khung, không đọc số đo từ OSM trong lời đọc |
| 3 | Thời lượng tối đa cho đề tài nhiều đoạn? | 75–90s; đề tài thường 45–75s |
| 4 | Luật "≤ 7 chữ/cảnh" áp cho cả thẻ đoạn và chip, hay chỉ cho tiêu đề nổi? | Chỉ áp cho tiêu đề nổi; thẻ đoạn ≤ 12 chữ |
| 5 | Tên file: CLAUDE.md mục 4 ghi `1_data_sheet.md`…`4_loi_doc_tts.txt`, còn `pipeline/tts_engine.py` đọc `04_Loi_Doc_TTS.txt` | Theo CLAUDE.md, kèm thêm một bản `04_Loi_Doc_TTS.txt` để pipeline chạy được |

### 5.2. Prompt

```text
# VAI TRÒ
Bạn là biên tập viên dữ liệu kiêm kỹ sư dựng video của kênh "Dữ Liệu BĐS".
Đọc và tuân thủ CLAUDE.md trước mọi việc. Nếu prompt này mâu thuẫn CLAUDE.md thì làm theo CLAUDE.md
và báo lại chỗ mâu thuẫn. Mọi kết quả là BẢN NHÁP chờ chủ dự án duyệt.
Format video: "MAP 3D đi qua từng phần của dự án" (phân tích ở docs/prompt_video_map3d.md, mục 2–3).

# NGƯỜI DÙNG ĐIỀN (bắt buộc: dòng có *)
* Đề tài: {…}
* Nguồn đầu vào (link báo / văn bản / ghi chú): {…}
* Loại đối tượng: {TUYẾN: đường, cầu, cao tốc, vành đai, metro, kênh
                   | KHU: khu đô thị, phân khu quy hoạch, khu công nghiệp, vùng thu hồi đất
                   | ĐIỂM: sân bay, nút giao, công trình đơn lẻ}
- Ngày làm (YYYY-MM-DD) + slug: {… | để trống → tự đặt theo CLAUDE.md mục 4}
- Bình luận thật của khán giả (nguyên văn + link): {… | không có}
- Dữ liệu bản đồ có sẵn (KML / GeoJSON / tọa độ, ghi nguồn): {… | không có}
- Góc muốn khai thác: {… | để Claude đề xuất}
- Thời lượng mục tiêu: {… | mặc định theo mục 5.1}
- Bảng màu: {mặc định theo mục 5.1 | bảng màu đã được duyệt}
- Giọng đọc: {mặc định theo pipeline/config.py}

# GIAI ĐOẠN 1: TRA CỨU (tự làm, không hỏi lại những gì tra được)
1. Mở nguồn đầu vào, chép nguyên văn mọi con số, địa danh, mốc thời gian, tên văn bản.
2. Lần ngược chuỗi văn bản của dự án (bỏ mục không áp dụng):
   quy hoạch liên quan → chủ trương đầu tư → điều chỉnh chủ trương → phương án/tách dự án thành phần
   → phê duyệt dự án / báo cáo nghiên cứu khả thi → lựa chọn nhà đầu tư, nhà thầu
   → bồi thường, giải phóng mặt bằng → khởi công → thông xe / hoàn thành.
3. Thứ tự ưu tiên nguồn:
   a. Công báo tỉnh/thành (congbao.<tỉnh>.gov.vn, ô tìm kiếm: /vi/vanban/search/?q=<tên dự án>),
      cổng HĐND, cổng UBND, cổng các Sở; Cổng Thông tin điện tử Chính phủ, vbpl.vn.
   b. Báo chính thống có dẫn số hiệu văn bản.
   c. Trang thứ cấp (thư viện pháp luật, trang BĐS): CHỈ dùng để tìm số hiệu, rồi quay lại (a) lấy bản gốc.
4. Mỗi văn bản tìm được:
   - tải về 01_Du_Lieu_Nguon/<ngày>_<slug>/, đặt tên <LOẠI>_<số-hiệu>_<YYYY-MM-DD>_<nội dung>;
   - đọc số hiệu và ngày ban hành TỪ CHÍNH VĂN BẢN. Bản để trống số hoặc ngày (dự thảo) không được
     dùng làm căn cứ số hiệu;
   - chép nguyên văn câu chứa dữ kiện vào cột "Trích nguyên văn".
5. Không mở được trang → ghi [CHƯA CÓ NGUỒN] kèm link đã thử. Không dùng bản tóm tắt của công cụ
   tìm kiếm hay công cụ đọc web làm "trích nguyên văn".
6. Tên hành chính: đối chiếu docs/danh_muc_hanh_chinh.csv. Nếu file thiếu hoặc không có tên đó →
   dùng tên ghi trong văn bản mức A ban hành sau 01/07/2025. Vẫn không có → [CHƯA XÁC MINH TÊN MỚI].
7. Hai nguồn lệch nhau → ghi cả hai, đánh "Mâu thuẫn nguồn". Nếu lệch vì khác giai đoạn (chủ trương,
   điều chỉnh, phê duyệt dự án) → ghi rõ giai đoạn của từng con số, không tự chọn.
8. Phân mức đúng CLAUDE.md 2.2: A = văn bản gốc; B = báo dẫn văn bản có số hiệu;
   C = báo không dẫn số hiệu, lời phát biểu, mạng xã hội.

# DỮ KIỆN CẦN THU
Bắt buộc (thiếu bất kỳ mục nào → dừng ở Step 1):
 [ ] Tên dự án chính thức + văn bản phê duyệt gần nhất (số hiệu, ngày, cơ quan ban hành)
 [ ] Giai đoạn hiện tại: Đề xuất / Lấy ý kiến / Đã phê duyệt / Đang triển khai / Hoàn thành
 [ ] Phạm vi: điểm đầu → điểm cuối (TUYẾN) | ranh giới + diện tích (KHU) | vị trí (ĐIỂM)
 [ ] Đơn vị hành chính liên quan (tên mới)
 [ ] Quy mô chính: chiều dài / diện tích / số làn / công suất
 [ ] Tổng vốn + nguồn vốn / hình thức đầu tư
 [ ] Mốc thời gian: đã xảy ra (có ngày) và dự kiến (ghi "dự kiến")
Nên có:
 [ ] Chia dự án thành phần / đoạn, vốn từng phần, ai làm phần nào
 [ ] Lịch sử điều chỉnh (vốn, quy mô, tiến độ) + lý do theo văn bản
 [ ] Chi phí bồi thường, diện tích thu hồi
 [ ] % tiến độ, % giải phóng mặt bằng (chỉ khi nguồn có ghi ngày số liệu)
 [ ] Vướng mắc nêu trong văn bản hoặc báo cáo chính thức
 [ ] Kết nối với dự án khác (chỉ khi văn bản nêu)
Bản đồ (thiếu không chặn Step 1–4, nhưng chặn bước dựng camera bay):
 [ ] Hình học từng đoạn / khu (GeoJSON, KML): chỉ từ người dùng hoặc nguồn A/B
 [ ] 5–15 điểm mốc có tọa độ (nút giao, cầu, công trình): như trên
 Không có → [CẦN TỌA ĐỘ] và mô tả bằng mốc. KHÔNG tự đoán, KHÔNG lấy tọa độ từ trí nhớ.

# ĐIỂM DỪNG
Dừng sau Step 1, báo người dùng, CHƯA viết Step 2–4 nếu:
 - thiếu bất kỳ mục "Bắt buộc";
 - dữ kiện định dùng làm hook là mức C hoặc CHƯA XÁC MINH;
 - con số định đưa vào lời đọc đang "Mâu thuẫn nguồn".

# GIAI ĐOẠN 2: THIẾT KẾ CÂU CHUYỆN
Hook: chọn MỘT kiểu mà dữ kiện mức A/B đủ chống đỡ:
 - "Lỡ hẹn": các mốc đã hẹn rồi bị trễ (mỗi mốc phải có nguồn)
 - "Thứ khởi công là phần nào": dự án chia nhiều thành phần / nguồn vốn / chủ thể
 - "Con số thay đổi": vốn hoặc quy mô điều chỉnh từ X lên Y (cần 2 văn bản)
 - "Bao giờ xong": mốc chính thức gần nhất + phần còn lại
 - "Hai con số khác nhau": giải thích vì sao các nguồn ghi khác nhau
 - "Trả lời bình luận": CHỈ khi có bình luận thật
Khung: Hook (0–6s, kèm lời hứa sẽ trả lời) → "xem tới cuối" → KPI tổng quan (2–4 số)
 → đi lần lượt từng phần "n/N" → trả lời hook bằng timeline các mốc
 → rủi ro / điều cần theo dõi (chỉ điều văn bản nêu) → CTA.
Chia phần: N = 3–8. Ưu tiên chia theo: (1) dự án thành phần / nguồn vốn, (2) địa lý liên tục
 từ đầu đến cuối, (3) trạng thái. Mỗi phần ~7–10s, gồm: tên, phạm vi, 1–3 chip số liệu, trạng thái, nguồn.
 KHU: mỗi phần là một phân khu hoặc lô. ĐIỂM: các phần là hạng mục hoặc giai đoạn của công trình.
Thời lượng: đo bằng tiếng, ~3,3 tiếng/giây, chỉnh theo TTS thực tế. Ước tính ≈ N × 8s + 20s.
 Vượt mục tiêu → gộp phần, KHÔNG tăng tốc độ đọc.

# YÊU CẦU ĐẦU RA
Ghi vào 02_Kich_Ban_Bai_Viet/<ngày>_<slug>/ theo tên file ở CLAUDE.md mục 4 (xem mục 5.1 #5), cộng thêm scene_spec.json:
1. Bảng dữ kiện (CLAUDE.md Step 1), kèm 3 mục: "Văn bản đã tải", "Còn thiếu", "Mâu thuẫn nguồn".
2. Kịch bản (Step 2), bảng: Giây | Lời đọc | Visual / Map 3D | Chữ màn hình | Dữ kiện #.
   Cột Visual ghi: camera (mốc tâm hoặc tọa độ có nguồn, zoom, pitch, bearing), phần nào sáng màu,
   pin nào hiện, thẻ và chip nào hiện, hiệu ứng.
3. Bài Fanpage + caption + 5–8 hashtag (Step 3).
4. Lời đọc TTS chuẩn hóa (Step 4).
5. scene_spec.json (bộ dựng pipeline/map3d_maker.py đọc trực tiếp file này;
   ví dụ thật: 02_Kich_Ban_Bai_Viet/2026-09-30/thu_nghiem_map3d/scene_spec.json):
{
  "meta": {"date": "YYYY-MM-DD", "slug": "", "output": "video_map3d.mp4",
           "voice": "vi-VN-NamMinhNeural", "rate": "+15%", "object_type": "TUYEN|KHU|DIEM",
           "palette": "kenh|trang_thai", "bbox": null, "zoom": 15,
           "brand": "Dữ Liệu BĐS", "source_line": "Nguồn: <số hiệu văn bản> • mốc tương lai là dự kiến",
           "map_credit": "Ảnh vệ tinh: <nguồn ảnh nền thực dùng>",
           "legend": [{"label": "", "color": "red|yellow|green|gray|orange", "shape": "dot|line|dashed"}]},
  "geometry": {
    "parts": [{"id": "p1", "label": "NHÃN TRÊN TUYẾN",
               "file": "tuyen.kml", "feature": "<tên Placemark trong KML / properties.name trong GeoJSON>",
               "coords": null, "kind": "line|polygon",
               "line": "solid|dashed", "status": "dang_khai_thac|co_san|dang_thi_cong|du_kien|cham_lui",
               "color": null, "label_at": 0.5,
               "source": "<BẮT BUỘC: ai cung cấp / văn bản nào, ngày>"}],
    "pins":  [{"id": "m1", "label": "", "sub": "", "coord": [lon, lat], "label_side": "right|left",
               "coord_source": "<BẮT BUỘC nếu có coord>"}]
  },
  "scenes": [{
    "id": "s1",
    "camera": {"target": "pin:<id>|part:<id>|fit:<id>,<id>", "m": null, "pitch": 45, "bearing": 0,
               "ease_s": 2.5, "rotate": 4, "drift": 0.06, "offset_px": [0, 0]},
    "pins": ["m1"], "parts": ["p1"], "highlight": ["p1"], "dim_others": true,
    "draw": {"parts": ["p1"], "at_line": 0, "duration_s": 3.0},
    "vehicle": {"part": "p1", "at_line": 0, "duration_s": 6.0, "reverse": false},
    "card": {"badge": "1/N", "accent": "red", "kicker": "", "title": "", "subtitle": "",
             "chips": [{"text": "", "style": "neutral|ok|warn|status|danger"}]},
    "overlays": [{"type": "title|kpi|parts|compare|callout|timeline|cta", "y": null, "...": "..."}],
    "lines": [{"sub": "<phụ đề, chữ số>", "tts": "<lời đọc chuẩn hóa Step 4>", "fact": "<Dữ kiện #, mức>"}]
  }]
}
   Quy tắc:
   - Thời điểm từng cảnh KHÔNG ghi tay. Bộ dựng tự tính từ độ dài giọng đọc của các câu trong "lines".
   - "camera.m" = số pixel ảnh nền trên 1 pixel màn hình (to = xa). Bỏ trống thì bộ dựng tự canh khung
     theo target. Cận cảnh: khoảng 0,9; toàn cảnh: 2,5–3,5.
   - "draw": tuyến tự vẽ dần ra khi lời đọc tới câu at_line. "vehicle": chấm xe chạy dọc tuyến.
   - Mỗi phần tuyến và mỗi ghim BẮT BUỘC có "source" / "coord_source". Thiếu là bộ dựng dừng
     (CLAUDE.md 2.5). Không có tọa độ thì KHÔNG tạo phần đó; mô tả bằng mốc trong kịch bản.
   - Mặc định bảng màu "kenh": tuyến = đỏ, khu = vàng. "trang_thai" chỉ dùng khi đã duyệt (mục 5.1 #1).
   - Mục trong overlay: "at_line" = câu thứ mấy thì mục đó sáng lên.
     kpi: items[{name, rows[[giá trị, nhãn]]}]; parts: items[{tag, title, sub, style}];
     compare: items[{label, from, to, note}]; timeline: items[{date, text, color}];
     callout: {text}; title: {kicker, lines[], sub}; cta: {question, sub, follow{text}}.
   Chạy: python pipeline/map3d_maker.py <spec> --preview 3,20,45   (xem ảnh tĩnh trước)
         python pipeline/map3d_maker.py <spec>                     (xuất video)
6. Danh sách việc còn lại cho người: tọa độ, số hiệu còn thiếu, ảnh cần chụp, quyết định cần duyệt.

# LUẬT HÌNH ẢNH
- Bố cục 1080×1920, từ trên xuống: thẻ phần (y 70–230) → hộp phụ (đến y 420) → bản đồ
  → legend (y ~960) → dòng nguồn → phụ đề (y ~1080, tối đa 2 dòng)
  → tên kênh + badge MÔ PHỎNG + credit ảnh nền.
- Nền vệ tinh giảm sáng 30–40%, pitch 40–50°. Camera bay liên tục giữa các phần (ease 2–3s),
  mở đầu và kết thúc ở toàn cảnh.
- Màu theo "Bảng màu". Legend cố định suốt video, có dòng "Chú thích của kênh".
- Mốc tương lai luôn có chữ "DỰ KIẾN". Mốc đã lỡ: gạch đỏ + chữ "Lỡ" (chỉ khi có nguồn).
- Chân khung luôn có: số hiệu văn bản nguồn, "các mốc tương lai là dự kiến", badge MÔ PHỎNG,
  credit đúng nguồn ảnh nền thực dùng.
- Không dùng tên, logo, hình của kênh khác. Không dùng ảnh AI như ảnh thật. Không đưa ảnh sổ đỏ
  hoặc tên chủ đất.

# LUẬT LỜI ĐỌC
- Mức A/B: nói như sự thật, kèm "theo nghị quyết / quyết định của …".
  Mức C: "theo báo …, chưa có văn bản". CHƯA XÁC MINH: không đọc.
- Mọi thông tin quy hoạch gắn đúng giai đoạn. Không nói Đề xuất / Lấy ý kiến như thể đã duyệt.
- Không suy diễn: không tự kết luận "sẽ chậm", "tăng giá", "hưởng lợi". Chỉ nói điều văn bản nêu.
- Cấm: hứa tăng giá / lợi nhuận, "cơ hội vàng", "đón sóng", "x2 tài sản", "sắp lên thành phố",
  kêu gọi mua / bán / đặt cọc, số điện thoại môi giới.
- CTA chỉ: bình luận câu hỏi, lưu video, theo dõi kênh, tự tra cứu tại Ủy ban nhân dân xã/phường
  hoặc Sở Nông nghiệp và Môi trường.
- Mọi con số trong lời đọc phải có trong bảng dữ kiện. Không dùng lại câu chữ của video hoặc kịch bản
  cũ nếu câu đó không có trong bảng.

# TỰ KIỂM TRƯỚC KHI TRẢ
[ ] Mọi số trong lời đọc và chữ màn hình đều trỏ về Dữ kiện #, mức A/B (hoặc C có ghi "theo báo")
[ ] Không có tọa độ, số hiệu, tên xã/phường, tên dự án nào do tự đoán
[ ] Mọi mốc tương lai có chữ "dự kiến"; mọi thông tin quy hoạch có giai đoạn
[ ] Tên hành chính đúng mô hình 2 cấp (tỉnh/thành → xã/phường/đặc khu)
[ ] Bài Fanpage có danh mục nguồn + dòng miễn trừ CLAUDE.md 2.4
[ ] Thời lượng tính theo tiếng khớp mục tiêu ±10%
[ ] Không chứa từ cấm
Báo cáo cuối: đã làm gì, còn thiếu gì, điểm nào cần chủ dự án quyết.
```

---

## 6. Cần bao nhiêu dữ kiện để dựng được video tương tự

Đếm từ chính video mẫu (Vành đai 3, 8 đoạn):

| Nhóm | Video mẫu dùng | Ghi chú |
|---|---|---|
| A. Tổng quan tuyến | **6** | Tổng chiều dài cả vòng, chiều dài phần dự án, tổng vốn, % tiến độ, văn bản phê duyệt (số hiệu), nguồn + ngày báo cáo |
| B. Thông tin từng đoạn | **~30** (8 đoạn × 3–5) | Mỗi đoạn tối thiểu: điểm đầu→cuối, chiều dài, % **hoặc** trạng thái, mốc dự kiến; thêm 1 vướng mắc nếu có |
| C. Lịch sử mốc hẹn | **5** | 4 ngày đã hẹn + 1 mốc mới |
| D. Kết luận / trả lời hook | **5** | 3 mốc timeline + "chưa có ngày thông xe toàn tuyến" + điểm kết nối |
| **Tổng dữ kiện nội dung** | **≈ 45** | Trong đó ~25 là con số cứng (km, tỷ, %, ngày) |
| E. Hình học bản đồ | 8 đường tuyến + ~12 điểm mốc | GeoJSON/KML từng đoạn + tọa độ nút giao, cầu, khu đô thị |
| F. Kỹ thuật | 4 | Giọng đọc (file hoặc TTS), tên kênh, bảng màu đã duyệt, thời lượng |

**Mức tối thiểu cho một video ~60s đúng luật kênh** (tuyến 3–4 đoạn):
- **15–20 dữ kiện nội dung** (đều có nguồn mức A/B): 4–5 tổng quan, 3 cho mỗi đoạn, 3–4 cho kết luận
- **3–4 đường tuyến + 5–6 điểm mốc** có tọa độ
- **1 câu hook** gắn với một con số thật

Thiếu nhóm E thì vẫn viết được Step 1–4 nhưng **không dựng được bản đồ bay camera**. Khi đó chỉ quay lại cách làm cũ là ảnh tĩnh Google Earth + vẽ tay theo shot list.

---

## 7. Cách lấy đường tuyến bằng Google Earth (KML) cho bộ dựng

Bộ dựng **không tự vẽ tuyến**. Tuyến phải đến từ người dùng hoặc nguồn mức A/B (CLAUDE.md 2.5).

1. Mở **Google Earth Pro** (máy tính) hoặc earth.google.com.
2. Đặt bản đồ quy hoạch / sơ đồ hướng tuyến trong văn bản gốc (thường là phụ lục bản vẽ của quyết định phê duyệt) lên màn hình để đối chiếu.
   Google Earth Pro có thể chồng ảnh sơ đồ lên bản đồ bằng *Add → Image Overlay*.
3. Vẽ từng phần dự án bằng *Add Path* (tuyến) hoặc *Add Polygon* (khu). **Mỗi phần một Placemark, đặt tên không dấu.**
   Ví dụ: `CL_CAU_CHINH`, `CL_PHIA_DONG_NAI`, `CL_PHIA_HCM`.
4. Chuột phải vào thư mục chứa các Placemark → *Save Place As…* → chọn **KML** (không chọn KMZ).
   Lưu vào `01_Du_Lieu_Nguon/<ngày>_<slug>/`.
5. Ghi rõ nguồn khi gửi cho Claude. Ví dụ: "vẽ theo sơ đồ phụ lục Quyết định số …, người vẽ: B, ngày …".
   Nguồn này được điền vào trường `"source"` của từng phần.

Trong `scene_spec.json`:

```json
{"id": "cl_cau", "file": "../../../01_Du_Lieu_Nguon/<ngày>_<slug>/tuyen.kml", "feature": "CL_CAU_CHINH",
 "label": "CẦU CHÍNH", "source": "B vẽ theo phụ lục QĐ …, 2026-10-07"}
```

Lưu ý:
- Đường tự vẽ chỉ là **minh họa**. Video luôn giữ badge MÔ PHỎNG và dòng "Chú thích của kênh".
- Lời đọc không được mô tả vị trí chi tiết hơn những gì văn bản ghi.
