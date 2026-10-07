# KỊCH BẢN THỬ NGHIỆM MAP 3D: CẦU CÁT LÁI & CẦU LONG HƯNG (BẢN NHÁP)

> Video thử để kiểm tra format, **chưa phải gói chính thức** (gói chính thức chờ duyệt bảng dữ kiện, xem `../00_prompt_map3d.md` mục 1.4).
> Dựng bằng `pipeline/map3d_maker.py` từ `scene_spec.json`. Thời lượng: 92,6s, giọng vi-VN-NamMinhNeural, tốc độ +15%.

## Giới hạn của bản thử

- **Hướng tuyến lấy từ OpenStreetMap** (truy vấn 2026-10-06, way 1561336244 cho Cát Lái; 1565182952/54/50, 1565182943, 1565182948 cho Long Hưng). File lưu tại `01_Du_Lieu_Nguon/2026-09-30_cau_cat_lai_long_hung/OSM_huong_tuyen_cau_Cat_Lai_Long_Hung_2026-10-06.geojson`.
  - Đây là nguồn **mức C**, chỉ dùng **minh họa**; chủ dự án đã duyệt (theo người dùng).
  - Số đo trên OSM khác nghị quyết: Cát Lái ~11,35 km so với 11,642 km; đoạn gắn thẻ cầu của Long Hưng ~3,83 km so với "khoảng 3,5 km". Lời đọc chỉ dùng số trong nghị quyết.
  - OSM không đánh dấu phần cầu của tuyến Cát Lái, nên tuyến Cát Lái vẽ liền một đường, không tách 3 phần trên bản đồ.
  - Nhãn "PHÍA TP.HCM" và "PHÍA ĐỒNG NAI" của Long Hưng đặt theo bờ sông trên ảnh. Không khẳng định đoạn đó trùng ranh dự án thành phần.
- Quyết định 2985/QĐ-UBND (05/12/2025) đã đọc, **không có tọa độ** (bản vẽ không đính kèm trong file Công báo). Văn bản có 2 dữ kiện mức A chưa đưa vào video: tuyến nắn để tránh Khu di tích "Địa điểm vụ thảm sát Giồng Sắn"; đường kết nối dài "khoảng 9,7 km".
- 2 ghim tọa độ người dùng gửi đã ẩn. Ghim Long Hưng lệch ~400 m về phía bắc so với tuyến cầu trên OSM.
- Đoạn người dùng dán có 4 chỗ **không dùng**:
  - tên hành chính cũ (TP. Thủ Đức, huyện Nhơn Trạch, tỉnh Đồng Nai);
  - "phường Long Hưng" (NQ 22 ghi xã An Phước và phường Tam Phước);
  - "cách nút Mỹ Thủy 400 m" (không có nguồn);
  - "kết nối ra Quốc lộ 51" (không có nguồn).
- Ảnh nền là Esri World Imagery. Trước khi đăng công khai cần kiểm tra điều khoản sử dụng thương mại, hoặc thay bằng ảnh Google Earth Studio có giấy phép.

## Kịch bản

| Giây | Lời đọc (phụ đề) | Visual / Map 3D | Chữ màn hình | Dữ kiện |
|---|---|---|---|---|
| 0,4–14,6 | Theo báo Tuổi Trẻ, ngày 29/9, cầu Cát Lái và cầu Long Hưng đã khởi công. / Nhưng mỗi cây cầu thật ra gồm ba phần, do hai thành phố cùng làm. / Phần nào đã khởi công? Mình đi qua từng cầu nhé. | Toàn cảnh 2 ghim, pitch 38°, xoay chậm | KHỞI CÔNG PHẦN NÀO? | Tuổi Trẻ 29/9/2026 (C); NQ 21, 22 (A) |
| 14,6–38,0 | Cầu Cát Lái dài hơn 11,6 km, nối phường Cát Lái với xã Đại Phước. / Phần khởi công là cầu chính và cầu dẫn, khoảng 14.927 tỷ, theo hợp đồng BT. / Phía Đồng Nai, đường kết nối và bồi thường là dự án thành phần 1, khoảng 9.077 tỷ. / Còn mở rộng đường Nguyễn Thị Định phía TP.HCM là dự án riêng, vốn TP.HCM. | Bay vào ghim Cát Lái, pitch 50°; thẻ 1/2; 3 phần sáng lần lượt theo lời đọc | Cát Lái ↔ Đại Phước | NQ 08 (A): 11,642 km, 14.927,153 tỷ, 9.076,591 tỷ; NQ 21 (A); khởi công: Tuổi Trẻ (C) |
| 38,0–59,4 | Cầu Long Hưng dài khoảng 9,8 km, nối phường Long Phước với xã An Phước. / Cầu chính và cầu dẫn khoảng 8.458 tỷ, cũng theo hợp đồng BT. / Phía Đồng Nai, dự án thành phần 1 khoảng 4.290 tỷ, vốn đầu tư công. / Phía TP.HCM, đường nối từ nút giao Gò Công là dự án riêng của TP.HCM. | Bay sang ghim Long Hưng; thẻ 2/2; 3 phần hiện mờ rồi sáng dần | Long Phước ↔ An Phước | NQ 07 (A): 9,8 km, 8.457,515 tỷ, 4.290,475 tỷ; NQ 22 (A) |
| 59,4–74,0 | Điều cần theo dõi: chi phí bồi thường Cát Lái tăng từ 2.985 lên 4.465 tỷ, Long Hưng từ 776 lên 1.516 tỷ. / Các nghị quyết đều yêu cầu đẩy nhanh bồi thường, giải phóng mặt bằng. | Thu về toàn cảnh; bảng so sánh; hộp cảnh báo đỏ | CHI PHÍ BỒI THƯỜNG… | NQ 54 → NQ 08; NQ 55 → NQ 07, bảng chi phí (A); Điều 2 NQ 07, 08 (A) |
| 74,0–81,7 | Qua ba đợt nghị quyết, thời gian xây dựng là 2026 – 2029, đây là mốc dự kiến. | Dòng thời gian 5 mốc | CÁC MỐC | NQ 54, 55 / 07, 08 / 21, 22 (A); 29/9: Tuổi Trẻ (C) |
| 81,7–92,6 | Bạn chờ cây cầu nào hơn? Bình luận và theo dõi kênh để cập nhật nhé. / Trước khi giao dịch, hãy kiểm tra quy hoạch tại Ủy ban nhân dân xã, phường. | Toàn cảnh; hộp vàng CTA + nút "Theo dõi" | BẠN CHỜ CẦU NÀO HƠN? | CTA đúng CLAUDE.md 2.4 |

Số làm tròn trong lời đọc đều lấy từ số gốc trong nghị quyết:
- 14.927,153 → 14.927 tỷ
- 9.076,591 → 9.077 tỷ
- 8.457,515 → 8.458 tỷ
- 4.290,475 → 4.290 tỷ
- 4.464,751 → 4.465 tỷ
- 1.515,86 → 1.516 tỷ
- 24.003,744 → "hơn 24.000 tỷ"
- 12.747,99 → khoảng 12.748 tỷ
