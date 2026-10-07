import os
from pathlib import Path

# Thư mục gốc của dự án
BASE_DIR = Path(__file__).resolve().parent.parent

# Các thư mục lưu trữ sản phẩm
DIR_RADAR = BASE_DIR / "01_Radar_Tin_Tuc"
DIR_KICH_BAN = BASE_DIR / "02_Kich_Ban_Bai_Viet"
DIR_ANH_TU_LIEU = BASE_DIR / "03_Anh_Tu_Lieu"
DIR_AUDIO = BASE_DIR / "04_Audio"

for d in [DIR_RADAR, DIR_KICH_BAN, DIR_ANH_TU_LIEU, DIR_AUDIO]:
    d.mkdir(parents=True, exist_ok=True)

# Cấu hình AI Model (ưu tiên GEMINI_API_KEY đã có sẵn trong môi trường)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-flash-latest")

# Cấu hình giọng đọc TTS Edge (miễn phí, chất lượng cao)
# Nam: vi-VN-NamMinhNeural | Nữ: vi-VN-HoaiMyNeural
TTS_VOICE = os.environ.get("TTS_VOICE", "vi-VN-NamMinhNeural")

# Tốc độ đọc giọng AI:
# "+0%": Bình thường (~2.2 từ/giây)
# "+15%": Chuẩn video ngắn TikTok/Reels cuốn hút, dứt khoát (~2.7 từ/giây theo CLAUDE.md)
# "+20%": Đọc nhanh, dồn dập
TTS_RATE = os.environ.get("TTS_RATE", "+15%")

# Cấu hình Telegram thông báo (tùy chọn)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# Danh sách nguồn RSS uy tín để Radar quét tin mỗi sáng
RSS_SOURCES = [
    {
        "name": "VnExpress BĐS",
        "url": "https://vnexpress.net/rss/bat-dong-san.rss",
        "category": "Thị trường"
    },
    {
        "name": "Tuổi Trẻ Kinh Doanh",
        "url": "https://tuoitre.vn/rss/kinh-doanh.rss",
        "category": "Hạ tầng & Vĩ mô"
    },
    {
        "name": "CafeF BĐS",
        "url": "https://cafef.vn/bat-dong-san.rss",
        "category": "Thị trường & Doanh nghiệp"
    },
    {
        "name": "Báo Xây Dựng",
        "url": "https://baoxaydung.com.vn/rss/bat-dong-san.rss",
        "category": "Quy hoạch & Pháp lý"
    },
    {
        "name": "Báo Đầu Tư",
        "url": "https://baodautu.vn/bat-dong-san.rss",
        "category": "Dự án & Hạ tầng"
    }
]

# Từ khóa ưu tiên lọc tin nóng BĐS & Hạ tầng
PRIORITY_KEYWORDS = [
    "khởi công", "thông xe", "quy hoạch", "vành đai", "cao tốc",
    "bảng giá đất", "luật đất đai", "thu hồi đất", "giải phóng mặt bằng",
    "metro", "sân bay", "cầu", "bồi thường", "tái định cư", "sáp nhập",
    "phê duyệt", "chủ trương đầu tư", "nút giao"
]
