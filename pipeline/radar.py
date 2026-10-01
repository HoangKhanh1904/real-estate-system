import sys
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
import re

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from pipeline.config import RSS_SOURCES, PRIORITY_KEYWORDS, DIR_RADAR

def clean_html(raw_html: str) -> str:
    """Lọc các thẻ HTML trong mô tả RSS."""
    if not raw_html:
        return ""
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', raw_html).strip()

def calculate_hot_score(title: str, description: str) -> tuple[int, list[str]]:
    """Tính điểm độ nóng và danh sách từ khóa bắt gặp."""
    text = (title + " " + description).lower()
    matched_keywords = []
    score = 0

    for kw in PRIORITY_KEYWORDS:
        if kw.lower() in text:
            matched_keywords.append(kw)
            score += 10

    # Ưu tiên thêm cho các chủ đề có tác động lớn
    high_impact = ["vành đai", "cao tốc", "khởi công", "bảng giá đất", "luật đất đai"]
    for hi in high_impact:
        if hi in text:
            score += 5

    return score, matched_keywords

def scan_radar() -> list[dict]:
    """Quét tất cả các nguồn RSS và lọc tin tức BĐS nóng."""
    items_found = []
    seen_links = set()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    }

    print(f"[*] Đang quét {len(RSS_SOURCES)} kênh RSS tin tức uy tín...")

    for source in RSS_SOURCES:
        try:
            resp = requests.get(source["url"], headers=headers, timeout=10)
            if resp.status_code != 200:
                continue

            # Parse XML
            root = ET.fromstring(resp.content)
            channel = root.find("channel")
            if channel is None:
                continue

            for item in channel.findall("item"):
                link = item.findtext("link", "").strip()
                if not link or link in seen_links:
                    continue

                title = item.findtext("title", "").strip()
                pub_date = item.findtext("pubDate", "").strip()
                desc = clean_html(item.findtext("description", ""))

                score, matched = calculate_hot_score(title, desc)

                # Chỉ lấy các tin có từ khóa liên quan đến quy hoạch, hạ tầng, đất đai
                if score >= 10:
                    seen_links.add(link)
                    items_found.append({
                        "source": source["name"],
                        "category": source["category"],
                        "title": title,
                        "link": link,
                        "pub_date": pub_date,
                        "description": desc,
                        "score": score,
                        "keywords": matched
                    })
        except Exception as e:
            # Bỏ qua nguồn lỗi để không gián đoạn
            continue

    # Sắp xếp theo điểm số giảm dần
    items_found.sort(key=lambda x: x["score"], reverse=True)
    return items_found

def save_radar_report(items: list[dict], date_str: str = None) -> Path:
    """Lưu danh sách đề tài nóng vào thư mục 01_Radar_Tin_Tuc."""
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")

    report_file = DIR_RADAR / f"{date_str}_Radar_Tin_Nong.md"

    lines = [
        f"# RADAR TIN NÓNG BĐS & QUY HOẠCH - NGÀY {date_str}",
        f"- Thời gian quét: {datetime.now().strftime('%H:%M:%S %d/%m/%Y')}",
        f"- Tổng số tin phát hiện: {len(items)} tin",
        "",
        "## TOP ĐỀ TÀI ĐƯỢC CHẤM ĐIỂM CAO NHẤT (ĐỀ XUẤT CHO ANH EM)",
        ""
    ]

    for idx, item in enumerate(items[:10], 1):
        kw_str = ", ".join(item["keywords"])
        lines.append(f"### {idx}. {item['title']}")
        lines.append(f"- **Nguồn:** {item['source']} | **Điểm Hot:** {item['score']} điểm")
        lines.append(f"- **Từ khóa:** `{kw_str}`")
        lines.append(f"- **Link:** [{item['link']}]({item['link']})")
        lines.append(f"- **Tóm tắt:** {item['description']}")
        lines.append("")

    report_file.write_text("\n".join(lines), encoding="utf-8")
    return report_file

if __name__ == "__main__":
    results = scan_radar()
    print(f"[OK] Tìm thấy {len(results)} tin tức phù hợp tiêu chí.")
    if results:
        report_path = save_radar_report(results)
        print(f"[OK] Đã lưu báo cáo tại: {report_path}")
        print("\n--- TOP 3 ĐỀ TÀI NỔI BẬT NHẤT HÔM NAY ---")
        for i, item in enumerate(results[:3], 1):
            print(f"{i}. [{item['source']}] {item['title']}")
            print(f"   Link: {item['link']}")
            print(f"   Keywords: {', '.join(item['keywords'])}")
