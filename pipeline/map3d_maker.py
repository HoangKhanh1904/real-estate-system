"""Dựng video "Map 3D" (ảnh vệ tinh nghiêng + camera bay + thẻ thông tin) từ scene_spec.json.

Cách chạy:
    python pipeline/map3d_maker.py <đường-dẫn-scene_spec.json>                 # xuất video
    python pipeline/map3d_maker.py <spec> --preview 3,20,45                    # chỉ xuất ảnh tĩnh tại các giây

Spec: xem docs/prompt_video_map3d.md mục 5.2. Mọi tọa độ trong spec phải có nguồn (người dùng / mức A-B).
"""
import argparse
import asyncio
import hashlib
import json
import math
import subprocess
import sys
import tempfile
import time
import urllib.request
import wave
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import edge_tts
import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFont

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

W, H, FPS = 1080, 1920, 30
FOCAL = (H / 2) / math.tan(math.radians(20))  # FOV dọc ~40°
TILE_URL = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
CACHE = Path(tempfile.gettempdir()) / "kenh_bds_map3d_cache"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

# Bảng màu kênh (CLAUDE.md 2.5): đỏ = tuyến/dự án, vàng = ranh giới
COL = {
    "panel": (14, 17, 27), "red": (232, 48, 64), "yellow": (247, 200, 21), "green": (46, 204, 113),
    "gray": (170, 180, 195), "white": (255, 255, 255), "muted": (175, 186, 204), "blue": (90, 160, 255),
    "orange": (255, 150, 40),
}
CHIP_STYLE = {"neutral": ("white", None), "ok": ("green", "green"), "warn": ("orange", "orange"),
              "status": ("yellow", "yellow"), "danger": ("red", "red")}

_font_cache = {}


def font(size, bold=True):
    key = (size, bold)
    if key not in _font_cache:
        name = "segoeuib.ttf" if bold else "segoeui.ttf"
        try:
            _font_cache[key] = ImageFont.truetype(f"C:/Windows/Fonts/{name}", size)
        except OSError:
            _font_cache[key] = ImageFont.truetype("arialbd.ttf" if bold else "arial.ttf", size)
    return _font_cache[key]


def rgba(name_or_rgb, a=1.0):
    rgb = COL[name_or_rgb] if isinstance(name_or_rgb, str) else tuple(name_or_rgb)
    return (*rgb, int(255 * max(0.0, min(1.0, a))))


def mixc(name_or_rgb, ia, a):
    """Màu hiện dần trên panel: trộn RGB từ màu panel sang màu đích, giữ alpha của cảnh."""
    c = COL[name_or_rgb] if isinstance(name_or_rgb, str) else tuple(name_or_rgb)
    p = COL["panel"]
    k = max(0.0, min(1.0, ia))
    return (*(int(p[i] + (c[i] - p[i]) * k) for i in range(3)), int(255 * max(0.0, min(1.0, a))))


def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


# ---------------------------------------------------------------- Ảnh vệ tinh

def lonlat_to_px(lon, lat, z):
    n = 256 * 2 ** z
    x = (lon + 180) / 360 * n
    y = (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n
    return x, y


def _fetch_tile(z, x, y):
    path = CACHE / "tiles" / str(z) / f"{x}_{y}.jpg"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(TILE_URL.format(z=z, x=x, y=y), headers={"User-Agent": "Mozilla/5.0"})
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=30) as r:
                    path.write_bytes(r.read())
                break
            except Exception:
                if attempt == 2:
                    return None
    return path


class Basemap:
    """Ghép tile thành 1 ảnh lớn ở mức zoom z, đã chỉnh tối theo phong cách kênh."""

    def __init__(self, bbox, z, brightness=0.62, saturation=0.72):
        lon0, lat0, lon1, lat1 = bbox
        x0, y0 = lonlat_to_px(lon0, lat1, z)
        x1, y1 = lonlat_to_px(lon1, lat0, z)
        tx0, ty0, tx1, ty1 = int(x0 // 256), int(y0 // 256), int(x1 // 256), int(y1 // 256)
        self.z, self.ox, self.oy = z, tx0 * 256, ty0 * 256
        tiles = [(x, y) for y in range(ty0, ty1 + 1) for x in range(tx0, tx1 + 1)]
        print(f"[*] Ảnh nền: {len(tiles)} tile, zoom {z}")
        with ThreadPoolExecutor(8) as ex:
            paths = list(ex.map(lambda xy: _fetch_tile(z, *xy), tiles))
        img = Image.new("RGB", ((tx1 - tx0 + 1) * 256, (ty1 - ty0 + 1) * 256), (10, 12, 16))
        missing = 0
        for (x, y), p in zip(tiles, paths):
            if p is None:
                missing += 1
                continue
            img.paste(Image.open(p).convert("RGB"), ((x - tx0) * 256, (y - ty0) * 256))
        if missing:
            print(f"[!] Thiếu {missing} tile")
        img = ImageEnhance.Color(img).enhance(saturation)
        img = ImageEnhance.Brightness(img).enhance(brightness)
        self.levels = [img, img.reduce(2), img.reduce(4)]

    def px(self, lon, lat):
        x, y = lonlat_to_px(lon, lat, self.z)
        return x - self.ox, y - self.oy


# ---------------------------------------------------------------- Camera 3D

def homography(cam):
    """Ma trận 3x3: điểm màn hình (u, v, 1) -> pixel ảnh nền mức 0 (camera nghiêng pitch, xoay bearing)."""
    th, be = math.radians(cam["pitch"]), math.radians(cam["bearing"])
    h = cam["m"] * math.cos(th) * FOCAL
    hg = np.array([
        [h, 0, -h * W / 2],
        [0, -h / math.cos(th), h * H / (2 * math.cos(th))],
        [0, math.sin(th), FOCAL * math.cos(th) - H / 2 * math.sin(th)],
    ])
    aff = np.array([
        [math.cos(be), math.sin(be), cam["cx"]],
        [math.sin(be), -math.cos(be), cam["cy"]],
        [0, 0, 1],
    ])
    return aff @ hg


def warp(basemap, cam):
    hs = homography(cam)
    lvl = 2 if cam["m"] >= 4 else 1 if cam["m"] >= 2 else 0
    s = 2 ** lvl
    hl = np.diag([1 / s, 1 / s, 1]) @ hs
    hl = hl / hl[2, 2]
    coeffs = tuple(hl.flatten()[:8])
    return basemap.levels[lvl].transform((W, H), Image.Transform.PERSPECTIVE, coeffs,
                                         Image.Resampling.BILINEAR, fillcolor=(8, 10, 14)), hs


def project(hs_inv, x, y):
    p = hs_inv @ np.array([x, y, 1.0])
    if p[2] <= 0:
        return None
    return p[0] / p[2], p[1] / p[2]


# ---------------------------------------------------------------- Âm thanh

def _ffmpeg_to_wav(src, dst):
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", str(src), "-ac", "1", "-ar", "44100",
                    "-sample_fmt", "s16", str(dst)], check=True)


def synth_line(text, voice, rate):
    key = hashlib.sha1(f"{voice}|{rate}|{text}".encode()).hexdigest()[:16]
    mp3, wav_path = CACHE / "tts" / f"{key}.mp3", CACHE / "tts" / f"{key}.wav"
    if not wav_path.exists():
        mp3.parent.mkdir(parents=True, exist_ok=True)
        for attempt in range(6):  # dịch vụ edge-tts hay lỗi tạm thời (NoAudioReceived) → chờ rồi thử lại
            try:
                asyncio.run(edge_tts.Communicate(text, voice, rate=rate).save(str(mp3)))
                break
            except Exception:
                if attempt == 5:
                    raise
                time.sleep(2 + 3 * attempt)
        _ffmpeg_to_wav(mp3, wav_path)
    with wave.open(str(wav_path)) as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)


def build_timeline(spec, out_wav):
    """Đọc từng câu bằng TTS, xếp nối tiếp; trả về mốc giây của cảnh và câu."""
    voice, rate = spec["meta"]["voice"], spec["meta"]["rate"]
    sr, t, chunks = 44100, 0.4, [np.zeros(int(0.4 * 44100), np.int16)]
    for sc in spec["scenes"]:
        sc["t_start"] = t
        sc["_lines"] = []
        for i, ln in enumerate(sc["lines"]):
            pcm = synth_line(ln["tts"], voice, rate)
            dur = len(pcm) / sr
            sc["_lines"].append((t, t + dur, ln["sub"]))
            chunks.append(pcm)
            gap = 0.25 if i < len(sc["lines"]) - 1 else sc.get("tail", 0.5)
            chunks.append(np.zeros(int(gap * sr), np.int16))
            t += dur + gap
        sc["t_end"] = t
    chunks.append(np.zeros(int(1.0 * sr), np.int16))
    t += 1.0
    spec["scenes"][-1]["t_end"] = t
    with wave.open(str(out_wav), "wb") as w:
        w.setnchannels(1), w.setsampwidth(2), w.setframerate(sr)
        w.writeframes(np.concatenate(chunks).tobytes())
    return t


# ---------------------------------------------------------------- Vẽ lớp phủ

def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        trial = f"{cur} {wd}".strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def chip(d, x, y, text, style, a, size=26):
    fg, bg = CHIP_STYLE.get(style, CHIP_STYLE["neutral"])
    f = font(size)
    tw = d.textlength(text, font=f)
    w = tw + 32
    if bg:
        d.rounded_rectangle([x, y, x + w, y + size + 22], radius=(size + 22) // 2, fill=rgba(bg, 0.92 * a))
        d.text((x + 16, y + 8), text, font=f, fill=rgba((12, 14, 20), a))
    else:
        d.rounded_rectangle([x, y, x + w, y + size + 22], radius=(size + 22) // 2, fill=rgba("panel", 0.85 * a),
                            outline=rgba(fg, 0.9 * a), width=2)
        d.text((x + 16, y + 8), text, font=f, fill=rgba(fg, a))
    return x + w + 14


def draw_card(d, card, a, dy):
    accent = card.get("accent", "red")
    x0, y0, x1, y1 = 40, 110 + dy, 1040, 285 + dy
    d.rounded_rectangle([x0, y0, x1, y1], radius=24, fill=rgba("panel", 0.9 * a))
    d.rounded_rectangle([x0, y0, x0 + 12, y1], radius=6, fill=rgba(accent, a))
    cx, cy, r = x0 + 88, (y0 + y1) // 2, 52
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=rgba(accent, a), outline=rgba("white", a), width=3)
    b = card.get("badge", "")
    d.text((cx - d.textlength(b, font=font(38)) / 2, cy - 26), b, font=font(38), fill=rgba("white", a))
    tx = x0 + 165
    d.text((tx, y0 + 22), card.get("kicker", ""), font=font(26), fill=rgba(accent, a))
    d.text((tx, y0 + 56), card.get("title", ""), font=font(50), fill=rgba("white", a))
    d.text((tx, y0 + 122), card.get("subtitle", ""), font=font(28, False), fill=rgba("muted", a))
    x = 40
    for c in card.get("chips", []):
        x = chip(d, x, y1 + 18, c["text"], c.get("style", "neutral"), a)


def panel(d, y0, h, a, outline=None):
    d.rounded_rectangle([40, y0, 1040, y0 + h], radius=24, fill=rgba("panel", 0.9 * a),
                        outline=rgba(outline, 0.9 * a) if outline else None, width=3)


def item_alpha(item, local, idx, line_starts, dim=0.0):
    """Độ hiện của một mục: hiện khi lời đọc tới câu at_line; dim > 0 = hiện mờ sẵn từ đầu cảnh."""
    if "at_line" in item and item["at_line"] < len(line_starts):
        start = line_starts[item["at_line"]]
    else:
        start = 0.4 + 0.5 * idx
    return dim + (1 - dim) * smooth((local - start) / 0.4)


def draw_overlay(d, ov, local, a, line_starts, y0):
    typ, items = ov["type"], ov.get("items", [])
    if typ == "title":
        k = ov.get("kicker", "")
        d.text(((W - d.textlength(k, font=font(30))) / 2, y0), k, font=font(30), fill=rgba("yellow", a))
        for i, ln in enumerate(ov.get("lines", [])):
            f = font(92)
            d.text(((W - d.textlength(ln, font=f)) / 2, y0 + 48 + i * 104), ln, font=f, fill=rgba("red", a),
                   stroke_width=8, stroke_fill=rgba((10, 12, 18), a))
        sub = ov.get("sub", "")
        sy = y0 + 60 + len(ov.get("lines", [])) * 104
        d.text(((W - d.textlength(sub, font=font(36))) / 2, sy), sub, font=font(36), fill=rgba("white", a),
               stroke_width=4, stroke_fill=rgba((10, 12, 18), a))
        return
    if typ == "kpi":
        panel(d, y0, 330, a)
        t = ov.get("title", "")
        d.text(((W - d.textlength(t, font=font(26))) / 2, y0 + 20), t, font=font(26), fill=rgba("yellow", a))
        colw = 1000 / max(1, len(items))
        for i, it in enumerate(items):
            ia = a * item_alpha(it, local, i, line_starts)
            x = 40 + i * colw + 40
            d.text((x, y0 + 70), it["name"], font=font(34), fill=mixc(it.get("color", "red"), ia / max(a, 1e-3), a))
            for j, (val, lab) in enumerate(it["rows"]):
                yy = y0 + 125 + j * 95
                d.text((x, yy), val, font=font(54), fill=mixc("white", ia / max(a, 1e-3), a))
                d.text((x, yy + 62), lab, font=font(24, False), fill=mixc("muted", ia / max(a, 1e-3), a))
            if i:
                d.line([(40 + i * colw, y0 + 75), (40 + i * colw, y0 + 300)], fill=rgba((60, 70, 90), a), width=2)
        return
    if typ == "parts":
        n = len(items)
        panel(d, y0, 70 + n * 118, a)
        d.text((70, y0 + 20), ov.get("title", ""), font=font(26), fill=rgba("yellow", a))
        for i, it in enumerate(items):
            ia = a * item_alpha(it, local, i, line_starts, ov.get("dim_before", 0.3))
            yy = y0 + 66 + i * 118
            col = CHIP_STYLE.get(it.get("style", "neutral"))[0]
            d.rounded_rectangle([70, yy + 6, 82, yy + 100], radius=6, fill=mixc(col, ia / max(a, 1e-3), a))
            d.text((102, yy), it["tag"], font=font(24), fill=mixc(col, ia / max(a, 1e-3), a))
            d.text((102, yy + 32), it["title"], font=font(36), fill=mixc("white", ia / max(a, 1e-3), a))
            d.text((102, yy + 76), it.get("sub", ""), font=font(24, False), fill=mixc("muted", ia / max(a, 1e-3), a))
        return
    if typ == "compare":
        n = len(items)
        panel(d, y0, 80 + n * 130, a)
        d.text((70, y0 + 22), ov.get("title", ""), font=font(26), fill=rgba("yellow", a))
        for i, it in enumerate(items):
            ia = a * item_alpha(it, local, i, line_starts)
            yy = y0 + 72 + i * 130
            d.text((70, yy), it["label"], font=font(32), fill=mixc("white", ia / max(a, 1e-3), a))
            d.text((70, yy + 46), it["from"], font=font(48), fill=mixc("gray", ia / max(a, 1e-3), a))
            fx = 70 + d.textlength(it["from"], font=font(48)) + 24
            d.text((fx, yy + 46), "→", font=font(48), fill=mixc("red", ia / max(a, 1e-3), a))
            d.text((fx + 70, yy + 46), it["to"], font=font(48), fill=mixc("red", ia / max(a, 1e-3), a))
            nt = it.get("note", "")
            d.text((1010 - d.textlength(nt, font=font(22, False)), yy + 8), nt, font=font(22, False),
                   fill=mixc("muted", ia / max(a, 1e-3), a))
        return
    if typ == "callout":
        ia = a * item_alpha(ov, local, 0, line_starts)
        lines = wrap(d, ov["text"], font(34), 880)
        hh = 50 + len(lines) * 46
        d.rounded_rectangle([40, y0, 1040, y0 + hh], radius=22, fill=rgba((60, 16, 24), 0.92 * ia),
                            outline=rgba("red", ia), width=3)
        for i, ln in enumerate(lines):
            d.text(((W - d.textlength(ln, font=font(34))) / 2, y0 + 24 + i * 46), ln, font=font(34),
                   fill=rgba("white", ia))
        return
    if typ == "timeline":
        n = len(items)
        panel(d, y0, 80 + n * 104, a)
        d.text((70, y0 + 22), ov.get("title", ""), font=font(26), fill=rgba("yellow", a))
        for i, it in enumerate(items):
            ia = a * item_alpha(it, local, i, line_starts)
            yy = y0 + 76 + i * 104
            col = it.get("color", "white")
            if i < n - 1:
                d.line([(90, yy + 18), (90, yy + 122)], fill=rgba((80, 90, 110), a), width=3)
            d.ellipse([76, yy + 4, 104, yy + 32], fill=rgba(col, ia), outline=rgba("white", ia), width=2)
            d.text((126, yy - 6), it["date"], font=font(36), fill=rgba(col, ia))
            d.text((126, yy + 42), it["text"], font=font(26, False), fill=rgba("muted", ia))
        return
    if typ == "cta":
        d.rounded_rectangle([110, y0, 970, y0 + 170], radius=28, fill=rgba("yellow", a))
        q = ov.get("question", "")
        d.text(((W - d.textlength(q, font=font(56))) / 2, y0 + 26), q, font=font(56), fill=rgba((15, 18, 24), a))
        s = ov.get("sub", "")
        d.text(((W - d.textlength(s, font=font(32))) / 2, y0 + 106), s, font=font(32), fill=rgba((50, 55, 62), a))
        ia = a * item_alpha(ov.get("follow", {}), local, 2, line_starts)
        f = ov.get("follow", {}).get("text", "")
        if f:
            fw = d.textlength(f, font=font(40)) + 80
            d.rounded_rectangle([(W - fw) / 2, y0 + 200, (W + fw) / 2, y0 + 290], radius=26, fill=rgba("red", ia),
                                outline=rgba("white", ia), width=3)
            d.text(((W - fw) / 2 + 40, y0 + 220), f, font=font(40), fill=rgba("white", ia))


def draw_pin(d, u, v, pin, a, t):
    pulse = (t * 0.8) % 1.0
    rr = 22 + 40 * pulse
    d.ellipse([u - rr, v - rr, u + rr, v + rr], outline=rgba("red", a * (1 - pulse)), width=4)
    d.ellipse([u - 16, v - 16, u + 16, v + 16], fill=rgba("red", a), outline=rgba("white", a), width=4)
    side = pin.get("label_side", "right")
    t1, t2 = pin["label"], pin.get("sub", "")
    w = max(d.textlength(t1, font=font(30)), d.textlength(t2, font=font(22, False))) + 36
    bx = u + 46 if side == "right" else u - 46 - w
    bx = max(20, min(W - 20 - w, bx))
    by = v - 44
    d.line([(u, v), (bx if side == "right" else bx + w, by + 44)], fill=rgba("red", a), width=3)
    d.rounded_rectangle([bx, by, bx + w, by + 88], radius=14, fill=rgba("panel", 0.92 * a),
                        outline=rgba("red", a), width=2)
    d.text((bx + 18, by + 8), t1, font=font(30), fill=rgba("white", a))
    d.text((bx + 18, by + 50), t2, font=font(22, False), fill=rgba("muted", a))


def draw_chrome(d, spec, sub):
    meta = spec["meta"]
    leg = meta.get("legend", [])
    if leg:
        d.rounded_rectangle([40, 1440, 1040, 1530], radius=20, fill=rgba("panel", 0.88))
        x = 70
        for it in leg:
            if it.get("shape") == "line":
                d.line([(x - 4, 1481), (x + 30, 1481)], fill=rgba(it["color"]), width=8)
            elif it.get("shape") == "dashed":
                d.line([(x - 4, 1481), (x + 9, 1481)], fill=rgba(it["color"]), width=8)
                d.line([(x + 17, 1481), (x + 30, 1481)], fill=rgba(it["color"]), width=8)
            else:
                d.ellipse([x, 1468, x + 26, 1494], fill=rgba(it["color"]), outline=rgba("white"), width=2)
            d.text((x + 38, 1463), it["label"], font=font(26), fill=rgba("white"))
            x += 38 + d.textlength(it["label"], font=font(26)) + 40
        lab = "Chú thích của kênh"
        d.text((1010 - d.textlength(lab, font=font(22, False)), 1467), lab, font=font(22, False), fill=rgba("muted"))
    src = meta.get("source_line", "")
    d.text(((W - d.textlength(src, font=font(21, False))) / 2, 1548), src, font=font(21, False), fill=rgba("muted"))
    if sub:
        lines = wrap(d, sub, font(44), 960)[:3]
        for i, ln in enumerate(lines):
            d.text(((W - d.textlength(ln, font=font(44))) / 2, 1600 + i * 58), ln, font=font(44),
                   fill=rgba("white"), stroke_width=5, stroke_fill=rgba((8, 10, 14)))
    brand = meta.get("brand", "")
    d.text((50, 1810), brand, font=font(34), fill=rgba("white"))
    bx = 50 + d.textlength(brand, font=font(34)) + 18
    pw = d.textlength("MÔ PHỎNG", font=font(24)) + 36
    d.rounded_rectangle([bx, 1812, bx + pw, 1854], radius=21, fill=rgba("yellow"))
    d.text((bx + 18, 1817), "MÔ PHỎNG", font=font(24), fill=rgba((12, 12, 12)))
    d.text((50, 1868), meta.get("map_credit", ""), font=font(20, False), fill=rgba("muted"))


def vignette():
    g = np.zeros((H, W, 4), np.uint8)
    ys = np.arange(H)[:, None]
    top = np.clip(1 - ys / 620, 0, 1) ** 1.6 * 225
    bot = np.clip((ys - 1250) / 670, 0, 1) ** 1.3 * 215
    g[..., 3] = np.maximum(top, bot).astype(np.uint8).repeat(W, axis=1)
    g[..., :3] = (6, 8, 12)
    return Image.fromarray(g)


# ---------------------------------------------------------------- Hình học tuyến / khu

# Bảng màu "trang_thai" (chỉ dùng khi chủ dự án đã duyệt, xem docs/prompt_video_map3d.md mục 5.1)
STATUS_COLOR = {"dang_khai_thac": "green", "co_san": "gray", "dang_thi_cong": "yellow",
                "du_kien": "orange", "cham_lui": "red"}


def _kml_shapes(path, name=None):
    import xml.etree.ElementTree as ET
    shapes = []
    for pm in ET.parse(path).getroot().iter():
        if not pm.tag.endswith("Placemark"):
            continue
        nm = next((c.text for c in pm if c.tag.endswith("name")), "") or ""
        if name and nm.strip() != name:
            continue
        for el in pm.iter():
            tag = el.tag.split("}")[-1]
            if tag in ("LineString", "LinearRing"):
                co = next((c.text for c in el.iter() if c.tag.endswith("coordinates")), "") or ""
                pts = [tuple(map(float, p.split(",")[:2])) for p in co.split()]
                if len(pts) >= 2:
                    shapes.append(("polygon" if tag == "LinearRing" else "line", pts))
    return shapes


def _geojson_shapes(path, name=None):
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    if d.get("type") == "FeatureCollection":
        feats = d["features"]
    elif d.get("type") == "Feature":
        feats = [d]
    else:
        feats = [{"geometry": d, "properties": {}}]
    shapes = []
    for f in feats:
        if name and (f.get("properties") or {}).get("name") != name:
            continue
        g = f["geometry"]
        t, c = g["type"], g["coordinates"]
        if t == "LineString":
            shapes.append(("line", [tuple(p[:2]) for p in c]))
        elif t == "MultiLineString":
            shapes += [("line", [tuple(p[:2]) for p in ln]) for ln in c]
        elif t == "Polygon":
            shapes.append(("polygon", [tuple(p[:2]) for p in c[0]]))
        elif t == "MultiPolygon":
            shapes += [("polygon", [tuple(p[:2]) for p in poly[0]]) for poly in c]
    return shapes


def load_part_shapes(part, base_dir):
    """Đọc hình học một phần dự án (lon, lat). Bắt buộc có 'source' (CLAUDE.md 2.5: không tự đoán tọa độ)."""
    if not part.get("source"):
        raise ValueError(f"Phần '{part['id']}' thiếu 'source' cho tọa độ. "
                         "Chỉ dùng tọa độ người dùng đưa hoặc nguồn mức A/B.")
    if part.get("coords"):
        return [(part.get("kind", "line"), [tuple(p[:2]) for p in part["coords"]])]
    path = (base_dir / part["file"]).resolve()
    if path.suffix.lower() == ".kml":
        shapes = _kml_shapes(path, part.get("feature"))
    else:
        shapes = _geojson_shapes(path, part.get("feature"))
    if not shapes:
        raise ValueError(f"Không đọc được đường/khu nào trong {path} (feature={part.get('feature')})")
    return shapes


def cut_polyline(pts, f):
    """Phần đầu của polyline theo tỉ lệ chiều dài f (0..1)."""
    if f >= 1 or len(pts) < 2:
        return pts
    seg = np.hypot(*np.diff(pts, axis=0).T)
    cum = np.concatenate([[0], np.cumsum(seg)])
    target = cum[-1] * max(0.0, f)
    k = int(np.searchsorted(cum, target))
    if k == 0:
        return pts[:1]
    r = (target - cum[k - 1]) / max(seg[k - 1], 1e-9)
    return np.vstack([pts[:k], pts[k - 1] + (pts[k] - pts[k - 1]) * r])


def project_many(hs_inv, pts):
    p = hs_inv @ np.vstack([pts.T, np.ones(len(pts))])
    ok = p[2] > 1e-6
    uv = (p[:2] / np.where(ok, p[2], 1)).T
    return uv, ok


def densify(pts, step=25.0):
    """Chèn thêm điểm để có thể cắt phần tuyến nằm ngoài tầm nhìn camera."""
    out = [pts[0]]
    for a, b in zip(pts[:-1], pts[1:]):
        n = max(1, int(np.hypot(*(b - a)) // step))
        out += [a + (b - a) * (k / n) for k in range(1, n + 1)]
    return np.array(out)


def visible_runs(hs_inv, pts):
    """Chiếu polyline lên màn hình, trả về các đoạn liên tục nằm trước camera."""
    if len(pts) < 2:
        return []
    uv, ok = project_many(hs_inv, densify(pts))
    ok &= (np.abs(uv[:, 0] - W / 2) < 4000) & (np.abs(uv[:, 1] - H / 2) < 5000)
    runs, cur = [], []
    for p, good in zip(uv, ok):
        if good:
            cur.append(p)
        elif cur:
            runs.append(np.array(cur))
            cur = []
    if cur:
        runs.append(np.array(cur))
    return [r for r in runs if len(r) >= 2]


def _dashes(uv, dash=30.0, gap=18.0):
    out, carry, on = [], 0.0, True
    for a, b in zip(uv[:-1], uv[1:]):
        seg = float(np.hypot(*(b - a)))
        pos = 0.0
        while pos < seg - 1e-6:
            need = (dash if on else gap) - carry
            step = min(need, seg - pos)
            if on:
                p0 = a + (b - a) * (pos / seg)
                p1 = a + (b - a) * ((pos + step) / seg)
                out.append((tuple(p0), tuple(p1)))
            pos += step
            carry += step
            if carry >= (dash if on else gap) - 1e-6:
                carry, on = 0.0, not on
    return out


def draw_route(d, uv, color, a, strong, dashed):
    pts = [tuple(p) for p in uv]
    if len(pts) < 2:
        return
    wide, core = (28, 11) if strong else (16, 6)
    if dashed:  # nét đứt: viền mảnh, mờ để phân biệt rõ với nét liền
        d.line(pts, fill=rgba(color, (0.12 if strong else 0.06) * a), width=wide - 10, joint="curve")
        for p0, p1 in _dashes(np.asarray(uv)):
            d.line([p0, p1], fill=rgba(color, 0.85 * a if strong else 0.5 * a), width=core - 3)
        return
    d.line(pts, fill=rgba(color, (0.30 if strong else 0.15) * a), width=wide, joint="curve")
    d.line(pts, fill=rgba(color, a if strong else 0.55 * a), width=core, joint="curve")
    if strong:
        base = COL[color] if isinstance(color, str) else tuple(color)
        d.line(pts, fill=rgba(tuple(min(255, c + 90) for c in base), 0.8 * a), width=3, joint="curve")


def draw_area(d, uv, color, a, strong):
    pts = [tuple(p) for p in uv]
    if len(pts) < 3:
        return
    d.polygon(pts, fill=rgba(color, (0.20 if strong else 0.10) * a))
    d.line(pts + [pts[0]], fill=rgba(color, a if strong else 0.5 * a), width=6 if strong else 3, joint="curve")


def draw_vehicle(d, u, v, a):
    d.ellipse([u - 30, v - 30, u + 30, v + 30], fill=rgba("white", 0.25 * a))
    d.ellipse([u - 17, v - 17, u + 17, v + 17], fill=rgba("white", a), outline=rgba("red", a), width=4)
    d.rounded_rectangle([u - 8, v - 5, u + 8, v + 5], radius=3, fill=rgba((20, 22, 30), a))


def draw_route_label(d, u, v, text, color, a):
    f = font(26)
    w = d.textlength(text, font=f) + 30
    u = max(20 + w / 2, min(W - 20 - w / 2, u))  # giữ nhãn trong khung hình
    d.rounded_rectangle([u - w / 2, v - 22, u + w / 2, v + 22], radius=12, fill=rgba(color, 0.95 * a))
    d.text((u - w / 2 + 15, v - 17), text, font=f, fill=rgba("white", a))


# ---------------------------------------------------------------- Dựng

class Renderer:
    def __init__(self, spec, base_dir):
        self.spec = spec
        meta = spec["meta"]
        geo = spec.get("geometry", {})
        self.parts = {p["id"]: p for p in geo.get("parts", [])}
        for p in self.parts.values():
            p["_ll"] = load_part_shapes(p, base_dir)
        self.pins = {p["id"]: p for p in geo.get("pins", [])}
        for p in self.pins.values():
            if p.get("coord") and not p.get("coord_source"):
                raise ValueError(f"Ghim '{p['id']}' thiếu 'coord_source'.")
        self.bm = Basemap(meta.get("bbox") or self._auto_bbox(), meta.get("zoom", 15))
        for p in self.pins.values():
            p["_px"] = self.bm.px(*p["coord"]) if p.get("coord") else None
        for p in self.parts.values():
            p["_shapes"] = [(k, np.array([self.bm.px(lo, la) for lo, la in pts])) for k, pts in p["_ll"]]
            if p.get("color"):
                p["_color"] = p["color"]
            elif meta.get("palette") == "trang_thai":
                p["_color"] = STATUS_COLOR.get(p.get("status"), "red")
            else:  # luật kênh: đỏ = tuyến/dự án, vàng = ranh giới khu
                p["_color"] = "yellow" if all(k == "polygon" for k, _ in p["_shapes"]) else "red"
        self._reveals = {}
        for sc in spec["scenes"]:
            starts = [s for s, _, _ in sc["_lines"]]
            for key in ("draw", "vehicle"):
                cfg = sc.get(key)
                if cfg:
                    li = cfg.get("at_line", 0)
                    cfg["_t0"] = starts[li] if li < len(starts) else sc["t_start"]
            for pid in (sc.get("draw") or {}).get("parts", []):
                self._reveals.setdefault(pid, (sc["draw"]["_t0"], sc["draw"].get("duration_s", 3.0)))
        self.vig = vignette()
        self.cams = [self._cam_for(sc) for sc in spec["scenes"]]

    def _auto_bbox(self):
        pts = [p["coord"] for p in self.pins.values() if p.get("coord")]
        for p in self.parts.values():
            for _, s in p["_ll"]:
                pts += s
        lons, lats = [p[0] for p in pts], [p[1] for p in pts]
        mx = max(0.08, 0.7 * (max(lons) - min(lons)))
        my = max(0.08, 0.7 * (max(lats) - min(lats)))
        return [min(lons) - mx, min(lats) - my, max(lons) + mx, max(lats) + my]

    def _ids_px(self, ids):
        pts = []
        for i in ids:
            if i in self.pins and self.pins[i]["_px"]:
                pts.append(np.array([self.pins[i]["_px"]]))
            elif i in self.parts:
                pts += [s for _, s in self.parts[i]["_shapes"]]
        return np.vstack(pts)

    def _cam_for(self, sc):
        c = sc["camera"]
        tgt = c["target"]
        if tgt.startswith(("pin:", "part:")):
            ids = [tgt.split(":", 1)[1]]
        else:  # fit:<id>,<id> (id ghim hoặc id phần)
            ids = tgt[4:].split(",")
        pts = self._ids_px(ids)
        lo, hi = pts.min(axis=0), pts.max(axis=0)
        cx, cy = (lo + hi) / 2
        m = c.get("m") or max(0.6, min(6.0, max((hi[0] - lo[0]) / (W * 0.72), (hi[1] - lo[1]) / (H * 0.40))))
        off = c.get("offset_px", [0, 0])
        return {"cx": cx + off[0], "cy": cy + off[1], "m": m, "pitch": c["pitch"], "bearing": c["bearing"],
                "ease": c.get("ease_s", 2.5), "drift": c.get("drift", 0.06), "rot": c.get("rotate", 4)}

    def _end_state(self, i):
        c = dict(self.cams[i])
        c["m"] *= 1 - c["drift"]
        c["bearing"] += c["rot"]
        return c

    def camera_at(self, t):
        scenes = self.spec["scenes"]
        i = max(k for k, s in enumerate(scenes) if s["t_start"] <= t or k == 0)
        sc, cur = scenes[i], self.cams[i]
        local, dur = t - sc["t_start"], sc["t_end"] - sc["t_start"]
        ease = cur["ease"] if i else 0
        p = max(0.0, (local - ease) / max(0.1, dur - ease))
        steady = {"cx": cur["cx"], "cy": cur["cy"], "pitch": cur["pitch"],
                  "m": cur["m"] * (1 - cur["drift"] * p), "bearing": cur["bearing"] + cur["rot"] * p}
        if i == 0 or local >= ease:
            return steady, i, local
        a, b, s = self._end_state(i - 1), dict(steady, m=cur["m"], bearing=cur["bearing"]), smooth(local / ease)
        dist = math.hypot(b["cx"] - a["cx"], b["cy"] - a["cy"])
        bump = max(0.0, min(1.2, dist / (W * max(a["m"], b["m"])) - 0.3))
        db = (b["bearing"] - a["bearing"] + 180) % 360 - 180
        cam = {"cx": a["cx"] + (b["cx"] - a["cx"]) * s, "cy": a["cy"] + (b["cy"] - a["cy"]) * s,
               "pitch": a["pitch"] + (b["pitch"] - a["pitch"]) * s, "bearing": a["bearing"] + db * s,
               "m": math.exp(math.log(a["m"]) + (math.log(b["m"]) - math.log(a["m"])) * s)
               * (1 + bump * math.sin(math.pi * s))}
        return cam, i, local

    def _draw_geometry(self, d, sc, hs_inv, t):
        show = sc.get("parts", list(self.parts))
        hl = set(sc.get("highlight", show))
        dim_others = sc.get("dim_others", True)
        for pid in sorted(show, key=lambda x: x in hl):  # phần được làm nổi vẽ sau cùng
            part = self.parts[pid]
            t0, dur = self._reveals.get(pid, (-1.0, 1.0))
            f = max(0.0, min(1.0, (t - t0) / max(dur, 0.1)))
            if f <= 0:
                continue
            strong = pid in hl or not dim_others
            for kind, pts in part["_shapes"]:
                if kind == "polygon":
                    uv, ok = project_many(hs_inv, pts)
                    if ok.all():
                        draw_area(d, uv, part["_color"], smooth(f), strong)
                    continue
                for run in visible_runs(hs_inv, cut_polyline(pts, f)):
                    draw_route(d, run, part["_color"], 1.0, strong, part.get("line") == "dashed")
            if strong and f >= 1 and part.get("label") and sc.get("route_labels", True):
                pts = part["_shapes"][0][1]
                uv = project_many(hs_inv, cut_polyline(pts, part.get("label_at", 0.5))[-1:])[0][0]
                if 0 < uv[0] < W and 420 < uv[1] < 1420:
                    draw_route_label(d, uv[0], uv[1] - 40, part["label"], part["_color"], 1.0)
        vh = sc.get("vehicle")
        if vh and vh["part"] in self.parts:
            pts = self.parts[vh["part"]]["_shapes"][0][1]
            if vh.get("reverse"):
                pts = pts[::-1]
            f = max(0.0, min(1.0, (t - vh["_t0"]) / vh.get("duration_s", 6.0)))
            uv, ok = project_many(hs_inv, cut_polyline(pts, max(f, 1e-3))[-1:])
            if ok.all():
                draw_vehicle(d, uv[0][0], uv[0][1], 1.0)

    def frame(self, t):
        cam, i, local = self.camera_at(t)
        bg, hs = warp(self.bm, cam)
        img = Image.alpha_composite(bg.convert("RGBA"), self.vig)
        sc = self.spec["scenes"][i]
        hs_inv = np.linalg.inv(hs)
        if self.parts:
            geo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            self._draw_geometry(ImageDraw.Draw(geo), sc, hs_inv, t)
            img = Image.alpha_composite(img, geo)
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        dur = sc["t_end"] - sc["t_start"]
        a_in = smooth((local - (0.6 if i else 0.0)) / 0.5) if i else 1.0
        a_out = smooth((dur - local) / 0.35) if i < len(self.spec["scenes"]) - 1 else 1.0
        a = min(a_in, a_out)
        for pid in sc.get("pins", []):
            pin = self.pins[pid]
            if pin["_px"] is None:
                continue
            uv = project(hs_inv, *pin["_px"])
            if uv and -100 < uv[0] < W + 100 and 300 < uv[1] < 1420:
                draw_pin(d, uv[0], uv[1], pin, smooth(local / 0.6) if i else 1.0, t)
        line_starts = [s - sc["t_start"] for s, _, _ in sc["_lines"]]
        dy = int((1 - a_in) * 24)
        y_next = 110
        if sc.get("card"):
            draw_card(d, sc["card"], a, dy)
            y_next = 380
        for ov in sc.get("overlays", []):
            draw_overlay(d, ov, local, a, line_starts, ov.get("y", y_next) + dy)
        sub = next((s for st, en, s in sc["_lines"] if st <= t < en + 0.2), "")
        draw_chrome(d, self.spec, sub)
        return Image.alpha_composite(img, layer).convert("RGB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--preview", help="Danh sách giây cần xuất ảnh tĩnh, VD 3,20,45")
    args = ap.parse_args()
    spec_path = Path(args.spec).resolve()
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    out_dir = spec_path.parent
    wav = CACHE / f"narration_{spec['meta']['slug']}.wav"
    total = build_timeline(spec, wav)
    print(f"[*] Thời lượng lời đọc: {total:.1f}s")
    for sc in spec["scenes"]:
        print(f"    {sc['id']}: {sc['t_start']:.1f}–{sc['t_end']:.1f}s")
    r = Renderer(spec, spec_path.parent)
    if args.preview:
        for s in args.preview.split(","):
            p = out_dir / f"preview_{float(s):05.1f}s.jpg"
            r.frame(float(s)).save(p, quality=88)
            print(f"[+] {p.name}")
        return
    out = out_dir / spec["meta"]["output"]
    cmd = [FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "pipe:0", "-i", str(wav), "-c:v", "libx264", "-preset", "medium", "-crf", "20",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
           "-af", "loudnorm=I=-16:TP=-1.5:LRA=11,pan=stereo|c0=c0|c1=c0", "-shortest", "-movflags", "+faststart", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(total * FPS)
    for k in range(n):
        if k % (FPS * 10) == 0:
            print(f"[*] Khung {k}/{n} ({k / FPS:.0f}s)")
        proc.stdin.write(r.frame(k / FPS).tobytes())
    proc.stdin.close()
    proc.wait()
    print(f"[+] Xong: {out} ({out.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
