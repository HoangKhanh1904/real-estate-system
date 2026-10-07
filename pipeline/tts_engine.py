import os
import sys
import asyncio
from pathlib import Path
from datetime import datetime
import edge_tts

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from pipeline.config import DIR_AUDIO, TTS_VOICE, TTS_RATE, DIR_KICH_BAN

async def _synthesize_async(text: str, output_path: Path, voice: str, rate: str):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # Chuẩn hóa khoảng trắng và dòng
    clean_text = " ".join(text.split())
    communicate = edge_tts.Communicate(clean_text, voice, rate=rate)
    await communicate.save(str(output_path))

def synthesize_speech(text_content: str, output_path: Path, voice: str = None, rate: str = None, max_retries: int = 3) -> bool:
    """
    Chuyển văn bản thành file âm thanh mp3 bằng edge-tts trực tiếp qua Python.
    Hỗ trợ chỉnh tốc độ đọc qua rate (VD: "+10%", "+15%", "+20%").
    Tự động retry nếu mạng hoặc websocket chập chờn.
    """
    if not voice:
        voice = TTS_VOICE
    if not rate:
        rate = TTS_RATE

    import time
    for attempt in range(1, max_retries + 1):
        try:
            asyncio.run(_synthesize_async(text_content, output_path, voice, rate))
            if output_path.exists() and output_path.stat().st_size > 0:
                return True
        except Exception as e:
            if attempt < max_retries:
                time.sleep(1.5)
            else:
                print(f"[X] Lỗi khi tạo audio TTS sau {max_retries} lần thử: {str(e)}")
                return False
    return False

def generate_audio_for_date(date_str: str = None, voice: str = None, rate: str = None) -> Path | None:
    """
    Tự động tìm file 04_Loi_Doc_TTS.txt của ngày và xuất file mp3 vào 04_Audio/[ngày]/
    """
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")

    tts_txt_file = DIR_KICH_BAN / date_str / "04_Loi_Doc_TTS.txt"

    if not tts_txt_file.exists():
        print(f"[!] Không tìm thấy file {tts_txt_file}")
        return None

    text = tts_txt_file.read_text(encoding="utf-8").strip()
    if not text:
        print("[!] File lời đọc TTS rỗng!")
        return None

    target_audio_file = DIR_AUDIO / date_str / "voice_doc_ai.mp3"
    selected_voice = voice or TTS_VOICE
    selected_rate = rate or TTS_RATE
    print(f"[*] Đang xuất giọng đọc AI ({selected_voice} | Tốc độ: {selected_rate}) -> {target_audio_file.name}...")

    ok = synthesize_speech(text, target_audio_file, selected_voice, selected_rate)
    if ok and target_audio_file.exists():
        size_kb = round(target_audio_file.stat().st_size / 1024, 1)
        print(f"[OK] Đã tạo thành công file audio: {target_audio_file} ({size_kb} KB)")
        return target_audio_file
    return None

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Xuất giọng đọc TTS")
    parser.add_argument("date", nargs="?", default=datetime.now().strftime("%Y-%m-%d"), help="Ngày (YYYY-MM-DD)")
    parser.add_argument("--voice", type=str, default=None, help="Giọng đọc")
    parser.add_argument("--rate", type=str, default=None, help="Tốc độ (VD: +15%%, +20%%)")
    args = parser.parse_args()
    generate_audio_for_date(args.date, args.voice, args.rate)
