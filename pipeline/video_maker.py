import os
import sys
import math
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import imageio_ffmpeg

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

W, H = 1080, 1920
FPS = 24

def get_font(size, bold=False):
    font_name = "segoeuib.ttf" if bold else "segoeui.ttf"
    try:
        return ImageFont.truetype(f"C:/Windows/Fonts/{font_name}", size)
    except:
        font_name = "arialbd.ttf" if bold else "arial.ttf"
        return ImageFont.truetype(f"C:/Windows/Fonts/{font_name}", size)

def get_fill_background(img, cx_ratio=0.5, cy_ratio=0.5, zoom=1.0):
    """High-speed crop-then-resize: guarantees 100% full-bleed coverage."""
    iw, ih = img.size
    target_aspect = W / H  # 1080/1920 = 0.5625
    
    max_crop_h = min(ih, iw / target_aspect)
    max_crop_w = max_crop_h * target_aspect
    
    crop_w = max_crop_w / max(1.0, zoom)
    crop_h = max_crop_h / max(1.0, zoom)
    
    center_x = iw * cx_ratio
    center_y = ih * cy_ratio
    
    x1 = max(0, min(iw - crop_w, center_x - crop_w / 2))
    y1 = max(0, min(ih - crop_h, center_y - crop_h / 2))
    
    cropped = img.crop((int(x1), int(y1), int(x1 + crop_w), int(y1 + crop_h)))
    return cropped.resize((W, H), Image.Resampling.BILINEAR)

def draw_watermark(draw, brand_name="Dữ Liệu BĐS"):
    wm_y = 1845
    draw.text((60, wm_y), brand_name, font=get_font(26, bold=True), fill=(255, 255, 255, 240))
    pill_x = 60 + int(draw.textbbox((0, 0), brand_name, font=get_font(26, bold=True))[2]) + 15
    draw.rounded_rectangle([pill_x, wm_y - 2, pill_x + 135, wm_y + 32], radius=16, fill=(247, 200, 21, 240))
    draw.text((pill_x + 14, wm_y + 3), "MÔ PHỎNG", font=get_font(18, bold=True), fill=(10, 10, 10, 255))
    draw.text((60, wm_y + 36), "Ảnh vệ tinh © Esri, Maxar • Bản đồ © OpenStreetMap", font=get_font(16), fill=(160, 170, 180, 200))

def draw_legend(draw, items, footnote="Tiến độ theo báo cáo UBND tỉnh Đồng Nai & TP.HCM • các mốc là dự kiến"):
    leg_w = 980
    leg_h = 68
    leg_x = (W - leg_w) // 2
    leg_y = 1590
    draw.rounded_rectangle([leg_x, leg_y, leg_x + leg_w, leg_y + leg_h], radius=18, fill=(12, 18, 28, 235), outline=(40, 55, 80, 180), width=2)
    
    step = leg_w / len(items)
    for i, (label, col) in enumerate(items):
        item_cx = leg_x + i * step + step / 2
        draw.rounded_rectangle([item_cx - 95, leg_y + 24, item_cx - 55, leg_y + 44], radius=10, fill=col)
        draw.text((item_cx - 45, leg_y + 21), label, font=get_font(20, bold=True), fill=(240, 240, 240, 240))
    
    draw.text((leg_x + 15, leg_y + 78), footnote, font=get_font(17), fill=(170, 185, 205, 210))

subtitles = [
    (0.00, 2.20, "Chờ đợi gần 30 năm,"),
    (2.20, 5.10, "cây cầu Cát Lái hơn 24.000 tỷ chính thức khởi công!"),
    (5.30, 7.80, "Nhưng liệu có thực sự giải cứu"),
    (7.80, 10.30, "vùng đất Nhơn Trạch như nhiều lời đồn thổi?"),
    (10.50, 12.80, "Lần này không chỉ có Cát Lái dài 11,6 km,"),
    (12.80, 15.20, "mà cầu Long Hưng cũng đồng loạt bấm nút,"),
    (15.20, 18.00, "mở toang 2 cửa ngõ về sân bay Long Thành."),
    (18.20, 21.00, "Từ bến phà Cát Lái vượt sông sang xã Đại Phước,"),
    (21.00, 24.00, "tuyến đường dẫn đâm thẳng vào cao tốc Bến Lức - Long Thành,"),
    (24.00, 26.80, "rút ngắn thời gian di chuyển chỉ còn 15 phút."),
    (27.00, 29.50, "Thế nhưng, khởi công mới chỉ là vạch xuất phát!"),
    (29.70, 32.20, "Phần cầu chính làm hợp đồng BT,"),
    (32.20, 35.00, "còn giải phóng mặt bằng lại dùng vốn ngân sách."),
    (35.20, 38.50, "Vốn đã đội hơn 3.300 tỷ chỉ vì tiền đền bù đất."),
    (38.80, 41.50, "Bài học từ các đại dự án trước cho thấy:"),
    (41.50, 44.00, "nếu vướng mặt bằng, công trình có thể kéo dài nhiều năm."),
    (44.00, 47.40, "Ai vội vàng ôm đất lướt sóng rất dễ bị chôn vốn!"),
    (47.70, 50.20, "Trước khi xuống tiền, hãy tra cứu kỹ pháp lý"),
    (50.20, 52.60, "và thông báo thu hồi đất tại UBND xã."),
    (52.80, 56.23, "Nhấn theo dõi kênh để cập nhật tiến độ công trường!")
]

def draw_subtitle(draw, t):
    curr_sub = ""
    for s_start, s_end, text in subtitles:
        if s_start <= t < s_end:
            curr_sub = text
            break
    if not curr_sub:
        return
    
    font = get_font(36, bold=True)
    if len(curr_sub) > 36:
        words = curr_sub.split()
        mid = len(words) // 2
        line1 = " ".join(words[:mid])
        line2 = " ".join(words[mid:])
        lines = [line1, line2]
    else:
        lines = [curr_sub]
    
    line_bboxes = [draw.textbbox((0, 0), l, font=font) for l in lines]
    max_w = max(b[2] - b[0] for b in line_bboxes)
    total_h = sum(b[3] - b[1] + 8 for b in line_bboxes)
    
    sub_y = 1430
    pad_x = 30
    pad_y = 12
    draw.rounded_rectangle([(W - max_w) // 2 - pad_x, sub_y - pad_y, (W + max_w) // 2 + pad_x, sub_y + total_h + pad_y], radius=18, fill=(10, 15, 25, 220), outline=(40, 55, 80, 160), width=1)
    
    cur_y = sub_y
    for l, b in zip(lines, line_bboxes):
        lw = b[2] - b[0]
        lh = b[3] - b[1]
        draw.text(((W - lw) // 2, cur_y), l, font=font, fill=(255, 255, 255, 255))
        cur_y += lh + 8

def build_cat_lai_video(date_str: str = "2026-09-30") -> Path:
    """Dựng video hoàn chỉnh phong cách Trịnh Nguyễn (Map 3D + Infographic Cards + Subtitles)."""
    base_dir = Path(__file__).resolve().parent.parent
    assets_dir = base_dir / "03_Anh_Tu_Lieu" / date_str
    audio_path = base_dir / "04_Audio" / date_str / "voice_doc_ai.mp3"
    output_video_path = base_dir / "02_Kich_Ban_Bai_Viet" / date_str / "video_tiktok_9_16.mp4"

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    img_hcmc_map = Image.open(assets_dir / "00_hcmc_satellite_map_wide.jpg").convert("RGB")
    img_closeup_map = Image.open(assets_dir / "00_cat_lai_closeup_map.jpg").convert("RGB")
    img_flycam = Image.open(assets_dir / "04_flycam_pha_cat_lai_thuc_te.jpg").convert("RGB")
    img_bridge_3d = Image.open(assets_dir / "02_phoi_canh_cau_cat_lai.jpg").convert("RGB")
    img_4bridges = Image.open(assets_dir / "01_so_do_ban_do_chinh_thuc.jpg").convert("RGB")

    # Crop 9:16 static background centered around river crossing
    cx, cy = 810, 500
    cw = int(1280 * W / H)  # 720
    ch = 1280
    x1 = cx - cw // 2       # 450
    y1 = 0
    x2 = x1 + cw            # 1170
    y2 = ch                 # 1280
    static_bg = img_closeup_map.crop((x1, y1, x2, y2)).resize((W, H), Image.Resampling.LANCZOS)

    # Stationary bridge coordinates
    PT_HCM = (412, 630)
    PT_DN = (667, 817)

    def draw_stationary_bridge(draw, show_continuation=False):
        if show_continuation:
            # Route continues towards Ben Luc - Long Thanh
            pts = [PT_DN, (700, 950), (740, 1100), (770, 1280)]
            for i in range(len(pts)-1):
                draw.line([pts[i], pts[i+1]], fill=(255, 140, 20), width=8)
            draw.rounded_rectangle([630, 1030, 970, 1075], radius=10, fill=(15, 22, 35, 240), outline=(255, 140, 20, 230), width=2)
            draw.text((645, 1040), "HƯỚNG CAO TỐC BẾN LỨC - LT", font=get_font(18, bold=True), fill=(255, 255, 255, 255))

        # Bridge Line (Red neon)
        draw.line([PT_HCM, PT_DN], fill=(255, 40, 70), width=12)
        
        # 2 Stationary Points (Gold with white rim)
        draw.ellipse([PT_HCM[0]-16, PT_HCM[1]-16, PT_HCM[0]+16, PT_HCM[1]+16], fill=(247, 200, 21), outline=(255, 255, 255), width=3)
        draw.ellipse([PT_DN[0]-16, PT_DN[1]-16, PT_DN[0]+16, PT_DN[1]+16], fill=(247, 200, 21), outline=(255, 255, 255), width=3)
        
        # Pin Labels (Dark translucent rounded pill)
        # HCM pin
        draw.rounded_rectangle([PT_HCM[0] - 220, PT_HCM[1] - 65, PT_HCM[0] + 25, PT_HCM[1] - 20], radius=10, fill=(15, 22, 35, 240), outline=(247, 200, 21, 230), width=2)
        draw.text((PT_HCM[0] - 205, PT_HCM[1] - 56), "BỜ CÁT LÁI (TP.HCM)", font=get_font(18, bold=True), fill=(255, 255, 255, 255))
        draw.line([(PT_HCM[0] - 40, PT_HCM[1] - 20), (PT_HCM[0], PT_HCM[1])], fill=(247, 200, 21, 230), width=2)
        
        # Dong Nai pin
        draw.rounded_rectangle([PT_DN[0] - 10, PT_DN[1] + 28, PT_DN[0] + 280, PT_DN[1] + 73], radius=10, fill=(15, 22, 35, 240), outline=(247, 200, 21, 230), width=2)
        draw.text((PT_DN[0] + 10, PT_DN[1] + 38), "BỜ ĐẠI PHƯỚC (ĐỒNG NAI)", font=get_font(18, bold=True), fill=(255, 255, 255, 255))
        draw.line([(PT_DN[0], PT_DN[1]), (PT_DN[0] + 50, PT_DN[1] + 28)], fill=(247, 200, 21, 230), width=2)
        
        # Route name in middle of bridge
        mx, my = (PT_HCM[0] + PT_DN[0]) // 2, (PT_HCM[1] + PT_DN[1]) // 2
        draw.rounded_rectangle([mx - 120, my - 24, mx + 120, my + 24], radius=12, fill=(200, 25, 45, 245))
        draw.text((mx - 105, my - 13), "CẦU CÁT LÁI (11,6 KM)", font=get_font(18, bold=True), fill=(255, 255, 255, 255))

    def render_frame(t):
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # SCENE 1: HOOK (0 - 5.2s)
        if t < 5.2:
            bg = static_bg.copy()
            
            box_x, box_y, box_w, box_h = 60, 110, 960, 160
            draw.rounded_rectangle([box_x, box_y, box_x + box_w, box_y + box_h], radius=32, fill=(255, 255, 255, 252))
            draw.polygon([(box_x + 70, box_y + box_h), (box_x + 70, box_y + box_h + 24), (box_x + 95, box_y + box_h)], fill=(255, 255, 255, 252))
            
            av_cx, av_cy, av_r = box_x + 65, box_y + box_h // 2, 40
            draw.ellipse([av_cx - av_r, av_cy - av_r, av_cx + av_r, av_cy + av_r], fill=(247, 200, 21, 255))
            draw.text((av_cx - 13, av_cy - 27), "?", font=get_font(42, bold=True), fill=(10, 10, 10, 255))
            
            draw.text((box_x + 130, box_y + 26), "Trả lời bình luận", font=get_font(22), fill=(110, 115, 125, 255))
            draw.text((box_x + 130, box_y + 64), "Dự án cầu Cát Lái khi nào xong?", font=get_font(38, bold=True), fill=(15, 20, 25, 255))
            
            card_y = 330
            draw.text((360, card_y), "DỰ ÁN NỐI TP.HCM - ĐỒNG NAI", font=get_font(26, bold=True), fill=(255, 255, 255, 240))
            
            title_text = "CHỜ ĐỢI GẦN 30 NĂM"
            f_big = get_font(64, bold=True)
            tb = draw.textbbox((0, 0), title_text, font=f_big)
            tw = tb[2] - tb[0]
            draw.text(((W - tw) // 2, card_y + 45), title_text, font=f_big, fill=(255, 45, 65, 255), stroke_width=6, stroke_fill=(10, 15, 25, 255))
            
            badges = [("2020", True), ("2023", True), ("2025", True), ("29/9/2026", False)]
            bx_start = 120
            bw = 180
            for idx, (yr, is_lo) in enumerate(badges):
                bx = bx_start + idx * (bw + 25)
                by = card_y + 140
                if is_lo:
                    draw.rounded_rectangle([bx, by, bx + bw, by + 58], radius=14, fill=(15, 20, 30, 230), outline=(255, 70, 70, 220), width=2)
                    draw.text((bx + 18, by + 12), yr, font=get_font(26, bold=True), fill=(255, 255, 255, 240))
                    draw.text((bx + 105, by + 14), "LỠ", font=get_font(22, bold=True), fill=(255, 60, 60, 255))
                    draw.line([(bx + 12, by + 40), (bx + 95, by + 18)], fill=(255, 50, 50, 255), width=3)
                else:
                    draw.rounded_rectangle([bx, by, bx + bw + 20, by + 58], radius=14, fill=(20, 45, 30, 240), outline=(40, 200, 100, 240), width=2)
                    draw.text((bx + 12, by + 13), "29/9/2026", font=get_font(23, bold=True), fill=(60, 240, 120, 255))
                    draw.text((bx + 125, by + 14), "BẤM NÚT", font=get_font(17, bold=True), fill=(255, 255, 255, 240))
            
            draw_stationary_bridge(draw, show_continuation=False)
            draw_legend(draw, [("Đã khởi công", (40, 200, 100)), ("Cầu Cát Lái", (255, 40, 70)), ("Phà hiện hữu", (80, 160, 255))])

        # SCENE 2: PHÀ CÁT LÁI (5.2 - 10.5s)
        elif t < 10.5:
            prog = (t - 5.2) / (10.5 - 5.2)
            bg = get_fill_background(img_flycam, cx_ratio=0.5, cy_ratio=0.62, zoom=1.05 + 0.08 * prog)
            
            card_x, card_y, card_w, card_h = 70, 120, 940, 260
            draw.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=26, fill=(15, 22, 34, 242), outline=(247, 200, 21, 220), width=2)
            draw.rounded_rectangle([card_x + 30, card_y + 20, card_x + 320, card_y + 60], radius=12, fill=(220, 40, 40, 255))
            draw.text((card_x + 45, card_y + 26), "ĐIỂM NGHẼN GIAO THÔNG", font=get_font(20, bold=True), fill=(255, 255, 255, 255))
            
            draw.text((card_x + 30, card_y + 80), "GIẢI CỨU NHƠN TRẠCH?", font=get_font(52, bold=True), fill=(247, 200, 21, 255))
            draw.text((card_x + 30, card_y + 155), "• Bến phà Cát Lái quá tải 50.000 - 90.000 lượt khách/ngày", font=get_font(23, bold=True), fill=(240, 240, 240, 255))
            draw.text((card_x + 30, card_y + 195), "• Nỗi ám ảnh kẹt xe xếp hàng nhiều giờ mỗi dịp lễ tết", font=get_font(22), fill=(200, 215, 230, 240))
            
            draw.rounded_rectangle([180, 850, 900, 930], radius=18, fill=(15, 20, 30, 235), outline=(255, 60, 60, 220), width=2)
            draw.text((210, 872), "PHÀ CÁT LÁI HIỆN TẠI: QUÁ TẢI NGHIÊM TRỌNG", font=get_font(24, bold=True), fill=(255, 80, 80, 255))

        # SCENE 3: 3 KPI CARDS (10.5 - 18.2s)
        elif t < 18.2:
            prog = (t - 10.5) / (18.2 - 10.5)
            bg = get_fill_background(img_4bridges, cx_ratio=0.52, cy_ratio=0.5, zoom=1.0 + 0.05 * prog)
            
            card_x, card_y, card_w, card_h = 50, 110, 980, 250
            draw.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=28, fill=(15, 22, 34, 242), outline=(45, 60, 85, 220), width=2)
            draw.text((card_x + 230, card_y + 24), "2 ĐẠI DỰ ÁN CỬA NGÕ ĐỒNG LOẠT KHỞI CÔNG", font=get_font(24, bold=True), fill=(247, 200, 21, 255))
            
            col_w = card_w / 3
            draw.text((card_x + 45, card_y + 75), "11,6 km", font=get_font(56, bold=True), fill=(255, 255, 255, 255))
            draw.text((card_x + 75, card_y + 155), "Cầu Cát Lái", font=get_font(24), fill=(180, 195, 215, 255))
            draw.text((card_x + 55, card_y + 190), "Thủ Đức - Nhơn Trạch", font=get_font(18), fill=(140, 155, 175, 230))
            draw.line([(card_x + col_w, card_y + 80), (card_x + col_w, card_y + 210)], fill=(45, 60, 85, 200), width=2)
            
            draw.text((card_x + col_w + 35, card_y + 75), "24.000 tỷ", font=get_font(56, bold=True), fill=(255, 255, 255, 255))
            draw.text((card_x + col_w + 65, card_y + 155), "Tổng mức vốn", font=get_font(24), fill=(180, 195, 215, 255))
            draw.text((card_x + col_w + 45, card_y + 190), "Hợp đồng BT & Ngân sách", font=get_font(18), fill=(140, 155, 175, 230))
            draw.line([(card_x + col_w * 2, card_y + 80), (card_x + col_w * 2, card_y + 210)], fill=(45, 60, 85, 200), width=2)
            
            draw.text((card_x + col_w * 2 + 35, card_y + 75), "12.700 tỷ", font=get_font(56, bold=True), fill=(255, 255, 255, 255))
            draw.text((card_x + col_w * 2 + 65, card_y + 155), "Cầu Long Hưng", font=get_font(24), fill=(180, 195, 215, 255))
            draw.text((card_x + col_w * 2 + 55, card_y + 190), "Nối Biên Hòa - Sân Bay", font=get_font(18), fill=(140, 155, 175, 230))
            
            draw_legend(draw, [("Cầu Cát Lái", (255, 50, 70)), ("Cầu Long Hưng", (247, 200, 21)), ("Cầu Long Thành (CT)", (60, 140, 255))])

        # SCENE 4: CLOSEUP MAP (18.2 - 27.0s)
        elif t < 27.0:
            bg = static_bg.copy()
            
            card_x, card_y, card_w, card_h = 50, 110, 980, 220
            draw.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=26, fill=(15, 22, 34, 240), outline=(45, 60, 85, 220), width=2)
            
            badge_r = 38
            draw.ellipse([card_x + 35, card_y + 35, card_x + 35 + badge_r * 2, card_y + 35 + badge_r * 2], fill=(247, 200, 21, 255))
            draw.text((card_x + 52, card_y + 55), "1/2", font=get_font(32, bold=True), fill=(10, 15, 25, 255))
            
            draw.text((card_x + 130, card_y + 35), "KẾT NỐI LIÊN VÙNG • TP.HCM - ĐỒNG NAI", font=get_font(21, bold=True), fill=(247, 200, 21, 255))
            draw.text((card_x + 130, card_y + 70), "RÚT NGẮN CÒN 15 PHÚT", font=get_font(46, bold=True), fill=(255, 255, 255, 255))
            draw.text((card_x + 130, card_y + 135), "Từ Phà Cát Lái -> Xã Đại Phước -> Cao tốc Bến Lức - Long Thành", font=get_font(22), fill=(180, 200, 225, 240))
            
            draw_stationary_bridge(draw, show_continuation=True)
            draw_legend(draw, [("Cầu Cát Lái", (255, 40, 70)), ("Cao tốc Bến Lức - LT", (247, 200, 21)), ("Khu đô thị SwanBay", (60, 200, 120))])

        # SCENE 5: COMPARISON BT vs GPMB (27.0 - 38.8s)
        elif t < 38.8:
            prog = (t - 27.0) / (38.8 - 27.0)
            bg = get_fill_background(img_bridge_3d, cx_ratio=0.45, cy_ratio=0.5, zoom=1.05 + 0.06 * prog)
            
            draw.rounded_rectangle([250, 100, 830, 158], radius=20, fill=(15, 22, 34, 240), outline=(255, 60, 60, 220), width=2)
            draw.text((285, 112), "BÓC TÁCH BÀI TOÁN PHÁP LÝ & TIẾN ĐỘ", font=get_font(24, bold=True), fill=(255, 255, 255, 255))
            
            title_text = "KHỞI CÔNG ≠ CÓ CẦU NGAY"
            f_big = get_font(56, bold=True)
            tb = draw.textbbox((0, 0), title_text, font=f_big)
            tw = tb[2] - tb[0]
            draw.text(((W - tw) // 2, 180), title_text, font=f_big, fill=(255, 60, 60, 255), stroke_width=6, stroke_fill=(10, 15, 25, 255))
            
            c_y, c_w, c_h = 265, 465, 240
            draw.rounded_rectangle([60, c_y, 60 + c_w, c_y + c_h], radius=22, fill=(18, 28, 48, 240), outline=(60, 140, 255, 220), width=2)
            draw.rounded_rectangle([80, c_y + 18, 80 + 220, c_y + 55], radius=10, fill=(40, 100, 220, 255))
            draw.text((95, c_y + 24), "CẦU CHÍNH (PPP)", font=get_font(20, bold=True), fill=(255, 255, 255, 255))
            draw.text((80, c_y + 75), "Hợp đồng BT (Xây dựng - Chuyển giao)", font=get_font(21, bold=True), fill=(240, 245, 255, 255))
            draw.text((80, c_y + 120), "• Doanh nghiệp tự lo vốn xây lắp\n• Tiến độ phụ thuộc mặt bằng sạch", font=get_font(20), fill=(180, 200, 225, 240))
            
            draw.rounded_rectangle([555, c_y, 555 + c_w, c_y + c_h], radius=22, fill=(35, 28, 18, 240), outline=(247, 180, 21, 220), width=2)
            draw.rounded_rectangle([575, c_y + 18, 575 + 230, c_y + 55], radius=10, fill=(210, 140, 15, 255))
            draw.text((590, c_y + 24), "MẶT BẰNG (ĐẦU TƯ CÔNG)", font=get_font(20, bold=True), fill=(255, 255, 255, 255))
            draw.text((575, c_y + 75), "Dự án độc lập dùng vốn Ngân sách", font=get_font(21, bold=True), fill=(255, 235, 200, 255))
            draw.text((575, c_y + 120), "• TP.HCM & Đồng Nai tự chi trả\n• Nút thắt đền bù luôn phức tạp", font=get_font(20), fill=(225, 210, 180, 240))
            
            draw.rounded_rectangle([110, c_y + c_h + 25, 970, c_y + c_h + 95], radius=18, fill=(35, 15, 20, 245), outline=(255, 60, 60, 230), width=2)
            tx, ty = 145, c_y + c_h + 60
            draw.polygon([(tx, ty - 16), (tx - 14, ty + 12), (tx + 14, ty + 12)], fill=(255, 60, 60, 255))
            draw.text((tx - 3, ty - 10), "!", font=get_font(18, bold=True), fill=(10, 10, 10, 255))
            draw.text((175, c_y + c_h + 40), "VỐN ĐỘI HƠN +3.389 TỶ ĐỒNG CHỦ YẾU DO TIỀN ĐỀN BÙ ĐẤT", font=get_font(21, bold=True), fill=(255, 120, 120, 255))

        # SCENE 6: BẪY CHÔN VỐN (38.8 - 47.7s)
        elif t < 47.7:
            prog = (t - 38.8) / (47.7 - 38.8)
            bg = get_fill_background(img_closeup_map, cx_ratio=0.60, cy_ratio=0.60, zoom=1.10 + 0.05 * prog)
            dark_dim = Image.new("RGB", (W, H), (10, 12, 18))
            bg = Image.blend(bg, dark_dim, 0.40)
            
            card_x, card_y, card_w, card_h = 70, 150, 940, 360
            draw.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=28, fill=(20, 15, 20, 245), outline=(255, 50, 50, 230), width=3)
            
            draw.text((card_x + 40, card_y + 30), "BÀI HỌC TỪ CÁC ĐẠI DỰ ÁN HẠ TẦNG TRƯỚC ĐÂY", font=get_font(22, bold=True), fill=(255, 90, 90, 255))
            draw.text((card_x + 40, card_y + 70), "CẢNH BÁO BẪY CHÔN VỐN!", font=get_font(52, bold=True), fill=(255, 50, 50, 255))
            
            draw.text((card_x + 40, card_y + 155), "• Vướng giải phóng mặt bằng có thể kéo dài nhiều năm", font=get_font(24, bold=True), fill=(245, 245, 245, 255))
            draw.text((card_x + 40, card_y + 205), "• Giá đất thường bị thổi phồng trước ngày khởi công", font=get_font(24, bold=True), fill=(245, 245, 245, 255))
            draw.text((card_x + 40, card_y + 255), "• Rủi ro đọng vốn nặng nếu lướt sóng ngắn hạn theo tin đồn", font=get_font(24, bold=True), fill=(255, 180, 180, 255))
            draw.text((card_x + 40, card_y + 305), "• Tiến độ thực tế phụ thuộc tốc độ bàn giao mặt bằng", font=get_font(22), fill=(180, 190, 205, 230))

        # SCENE 7: CTA BANNER (47.7 - 56.23s)
        else:
            prog = (t - 47.7) / (56.23 - 47.7)
            bg = get_fill_background(img_hcmc_map, cx_ratio=0.55, cy_ratio=0.58, zoom=1.20 - 0.08 * prog)
            
            rc_x, rc_y, rc_w, rc_h = 70, 150, 940, 250
            draw.rounded_rectangle([rc_x, rc_y, rc_x + rc_w, rc_y + rc_h], radius=24, fill=(15, 22, 34, 242), outline=(40, 180, 100, 220), width=2)
            draw.text((rc_x + 35, rc_y + 25), "LỜI KHUYÊN CHO NHÀ ĐẦU TƯ TRƯỚC KHI XUỐNG TIỀN", font=get_font(24, bold=True), fill=(40, 210, 120, 255))
            draw.text((rc_x + 35, rc_y + 75), "• Tra cứu kỹ thông báo thu hồi đất tại UBND xã / phường", font=get_font(23, bold=True), fill=(240, 240, 240, 255))
            draw.text((rc_x + 35, rc_y + 125), "• Kiểm tra quy hoạch chi tiết 1/500 & mốc lộ giới giao thông", font=get_font(23, bold=True), fill=(240, 240, 240, 255))
            draw.text((rc_x + 35, rc_y + 175), "• Tuyệt đối không mua đất nông nghiệp chưa rõ hành lang pháp lý", font=get_font(22), fill=(255, 180, 180, 255))
            
            cta_x, cta_y, cta_w, cta_h = 70, 450, 940, 260
            draw.rounded_rectangle([cta_x, cta_y, cta_x + cta_w, cta_y + cta_h], radius=32, fill=(247, 200, 21, 255), outline=(255, 225, 60, 255), width=3)
            
            title_cta = "BẠN CHỜ CẦU NÀO NHẤT?"
            f_cta = get_font(54, bold=True)
            tb = draw.textbbox((0, 0), title_cta, font=f_cta)
            draw.text((cta_x + (cta_w - (tb[2] - tb[0])) // 2, cta_y + 35), title_cta, font=f_cta, fill=(15, 20, 25, 255))
            
            sub_cta = "Cầu Cát Lái hay Cầu Long Hưng? Bình luận cho mình biết nhé!"
            f_sub = get_font(28, bold=True)
            tb2 = draw.textbbox((0, 0), sub_cta, font=f_sub)
            draw.text((cta_x + (cta_w - (tb2[2] - tb2[0])) // 2, cta_y + 115), sub_cta, font=f_sub, fill=(45, 50, 55, 255))
            
            badge_cta = "● Nhấn THEO DÕI KÊNH để cập nhật thực địa công trường!"
            f_b = get_font(25, bold=True)
            tb3 = draw.textbbox((0, 0), badge_cta, font=f_b)
            draw.text((cta_x + (cta_w - (tb3[2] - tb3[0])) // 2, cta_y + 185), badge_cta, font=f_b, fill=(180, 30, 30, 255))

        draw_subtitle(draw, t)
        draw_watermark(draw)
        
        return Image.alpha_composite(bg.convert("RGBA"), overlay).convert("RGB")

    total_frames = int(56.23 * FPS)
    print(f"\n🎬 ĐANG XUẤT BẢN VIDEO CHUẨN PHONG CÁCH TRỊNH NGUYỄN ({total_frames} frames)...")
    
    cmd = [
        ffmpeg_exe, "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{W}x{H}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "pipe:0",
        "-i", str(audio_path),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "44100",
        "-ac", "2",
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        str(output_video_path)
    ]
    
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for frame_idx in range(total_frames):
        t = frame_idx / FPS
        if frame_idx % 120 == 0:
            print(f"[*] Rendering frame {frame_idx}/{total_frames} ({t:.1f}s)...")
        frame_img = render_frame(t)
        proc.stdin.write(frame_img.tobytes())
        
    proc.stdin.close()
    proc.wait()
    
    backup_path = base_dir / "02_Kich_Ban_Bai_Viet" / date_str / "video_tiktok_trinh_nguyen_style.mp4"
    import shutil
    shutil.copy2(output_video_path, backup_path)

    print("\n" + "="*60)
    print(f"🎉 XUẤT VIDEO THÀNH CÔNG: {output_video_path}")
    print(f"📊 Dung lượng: {round(output_video_path.stat().st_size / (1024*1024), 2)} MB")
    print("="*60)
    return output_video_path

if __name__ == "__main__":
    build_cat_lai_video("2026-09-30")
