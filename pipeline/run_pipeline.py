import argparse
import sys
from datetime import datetime
from pathlib import Path

# Đảm bảo in tiếng Việt chuẩn trên terminal Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from pipeline.config import BASE_DIR, DIR_RADAR, DIR_KICH_BAN, DIR_AUDIO, DIR_ANH_TU_LIEU
from pipeline.radar import scan_radar, save_radar_report
from pipeline.scraper import extract_article
from pipeline.generator import generate_content_bundle
from pipeline.tts_engine import generate_audio_for_date
from pipeline.telegram_notifier import send_telegram_message

def run_radar_flow(date_str: str = None):
    """Quy trình 1: Quét tin buổi sáng và gửi báo cáo."""
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")

    print("\n" + "="*60)
    print(f"🛰️  CHẠY RADAR SĂN TIN NÓNG BĐS & QUY HOẠCH ({date_str})")
    print("="*60)

    items = scan_radar()
    if not items:
        print("[!] Không tìm thấy tin tức mới nào thỏa mãn từ khóa.")
        return

    report_path = save_radar_report(items, date_str)
    print(f"\n[OK] Đã quét xong! Tổng số: {len(items)} tin.")
    print(f"📄 Báo cáo chi tiết: {report_path}")

    # Soạn tin nhắn tóm tắt Top 3
    top_items = items[:3]
    msg_lines = [
        f"🎯 *RADAR BĐS SÁNG {date_str} - TOP 3 ĐỀ TÀI NÓNG*",
        f"Máy vừa quét {len(items)} tin tức quy hoạch/hạ tầng mới nhất:\n"
    ]

    for idx, it in enumerate(top_items, 1):
        msg_lines.append(f"*{idx}. {it['title']}*")
        msg_lines.append(f"• Nguồn: {it['source']} | Điểm: {it['score']}")
        msg_lines.append(f"• Link: {it['link']}")
        msg_lines.append(f"• Tóm tắt: {it['description']}\n")

    msg_lines.append("👉 *Anh em thảo luận và chốt 1 đề tài trước 9h00 nhé!*")
    full_msg = "\n".join(msg_lines)

    # In ra terminal
    print("\n" + full_msg)

    # Gửi qua Telegram nếu có cấu hình
    if send_telegram_message(full_msg):
        print("\n[OK] Đã gửi thông báo đến nhóm Telegram thành công!")

def run_production_flow(url: str, date_str: str = None):
    """Quy trình 2: Sản xuất trọn bộ nội dung từ 1 link bài báo."""
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")

    print("\n" + "="*60)
    print(f"🚀 BẮT ĐẦU SẢN XUẤT TRỌN BỘ NỘI DUNG (NGÀY {date_str})")
    print(f"🔗 Nguồn đề tài: {url}")
    print("="*60)

    # 1. Cào nội dung bài báo
    print("\n[BƯỚC 1/3] Cào nội dung bài viết gốc...")
    article = extract_article(url)
    if not article.get("success"):
        print(f"[X] Thất bại khi cào bài báo: {article.get('error')}")
        return

    print(f"✓ Tiêu đề: {article['title']}")
    print(f"✓ Nguồn: {article['author']} ({article['published_date']})")
    print(f"✓ Thu thập thành công {len(article['content'])} ký tự.")

    # 2. Sinh trọn bộ kịch bản và bảng dữ kiện
    print("\n[BƯỚC 2/3] Gọi AI phân tích và tạo bộ 5 tài liệu chuẩn CLAUDE.md...")
    try:
        bundle = generate_content_bundle(article, date_str)
        print("✓ Đã sinh thành công các file:")
        for k, path in bundle["files"].items():
            print(f"   • {k}: {path}")
    except Exception as e:
        print(f"[X] Lỗi khi sinh kịch bản: {e}")
        return

    # 3. Xuất file âm thanh TTS
    print("\n[BƯỚC 3/3] Tự động chuyển lời đọc thành âm thanh MP3...")
    audio_path = generate_audio_for_date(date_str)
    if audio_path:
        print(f"✓ Audio đã hoàn thành: {audio_path}")

    # Hoàn tất
    print("\n" + "="*60)
    print(f"🎉 HOÀN THÀNH QUY TRÌNH SẢN XUẤT CHO NGÀY {date_str}!")
    print(f"📂 Thư mục kịch bản: {DIR_KICH_BAN / date_str}")
    print(f"📂 Thư mục ảnh chụp:  {DIR_ANH_TU_LIEU / date_str}")
    print(f"📂 Thư mục âm thanh: {DIR_AUDIO / date_str}")
    print("="*60)

    # Gửi thông báo hoàn thành nếu có Telegram
    done_msg = (
        f"✅ *ĐÃ XUẤT XONG GÓI NỘI DUNG {date_str}*\n\n"
        f"📌 *Đề tài:* {article['title']}\n"
        f"📁 Đã tạo đủ: Bảng dữ kiện, Kịch bản video, Bài Fanpage, Lời đọc TTS & Danh sách ảnh Google Earth.\n"
        f"🎙️ Đã tạo xong file Voice MP3.\n\n"
        f"👉 *Bạn A* mở `Danh_Sach_Anh_Can_Chup.md` để chụp bản đồ.\n"
        f"👉 *Bạn B* mở CapCut thả audio + ảnh vào dựng video!"
    )
    send_telegram_message(done_msg)

def run_scheduler_daemon(target_time: str = "06:30"):
    """Chạy vòng lặp nền kiểm tra và kích hoạt lúc target_time hàng ngày."""
    import time
    print("\n" + "="*60)
    print(f"⏰ ĐANG KHỞI CHẠY TIẾN TRÌNH LỊCH NỀN (HẸN GIỜ: {target_time} HÀNG NGÀY)")
    print("   Nhấn Ctrl + C để dừng.")
    print("="*60)

    last_run_date = ""

    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        today = now.strftime("%Y-%m-%d")

        if current_time == target_time and last_run_date != today:
            print(f"\n[🔔 BÁO THỨC] Đúng {target_time}! Tự động kích hoạt Radar tin sáng...")
            try:
                run_radar_flow(today)
                last_run_date = today
            except Exception as e:
                print(f"[X] Lỗi khi chạy tự động: {e}")

        # Nghỉ 30 giây kiểm tra lại một lần
        time.sleep(30)

def main():
    parser = argparse.ArgumentParser(
        description="Pipeline Tự Động Hóa Kênh BĐS, Bản Đồ & Quy Hoạch"
    )
    parser.add_argument("--radar", action="store_true", help="Quét tin nóng RSS và đề xuất Top đề tài")
    parser.add_argument("--url", type=str, help="Link bài báo để sản xuất trọn bộ nội dung")
    parser.add_argument("--date", type=str, default=datetime.now().strftime("%Y-%m-%d"), help="Ngày xử lý (YYYY-MM-DD)")
    parser.add_argument("--tts", action="store_true", help="Chỉ chạy riêng khâu tạo file audio TTS")
    parser.add_argument("--scheduler", action="store_true", help="Chạy tiến trình nền tự động quét tin lúc 06:30 sáng")
    parser.add_argument("--time", type=str, default="06:30", help="Giờ hẹn chạy cho --scheduler (VD: 06:30)")

    args = parser.parse_args()

    if args.scheduler:
        run_scheduler_daemon(args.time)
    elif args.radar:
        run_radar_flow(args.date)
    elif args.url:
        run_production_flow(args.url, args.date)
    elif args.tts:
        generate_audio_for_date(args.date)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
