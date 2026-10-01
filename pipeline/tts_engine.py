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

from pipeline.config import DIR_AUDIO, TTS_VOICE, DIR_KICH_BAN

async def _synthesize_async(text: str, output_path: Path, voice: str):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # Chuẩn hóa khoảng trắng và dòng
    clean_text = " ".join(text.split())
    communicate = edge_tts.Communicate(clean_text, voice)
    await communicate.save(str(output_path))

def synthesize_speech(text_content: str, output_path: Path, voice: str = None) -> bool:
    """
    Chuyển văn bản thành file âm thanh mp3 bằng edge-tts trực tiếp qua Python.
    """
    if not voice:
        voice = TTS_VOICE

    try:
        asyncio.run(_synthesize_async(text_content, output_path, voice))
        return True
    except Exception as e:
        print(f"[X] Lỗi khi tạo audio TTS: {str(e)}")
        return False

def generate_audio_for_date(date_str: str = None, voice: str = None) -> Path | None:
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
    print(f"[*] Đang xuất giọng đọc AI ({selected_voice}) -> {target_audio_file.name}...")

    ok = synthesize_speech(text, target_audio_file, selected_voice)
    if ok and target_audio_file.exists():
        size_kb = round(target_audio_file.stat().st_size / 1024, 1)
        print(f"[OK] Đã tạo thành công file audio: {target_audio_file} ({size_kb} KB)")
        return target_audio_file
    return None

if __name__ == "__main__":
    d = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")
    generate_audio_for_date(d)
