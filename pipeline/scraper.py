import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import sys

# Đảm bảo in tiếng Việt không bị lỗi font trên Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

def clean_text(text: str) -> str:
    """Làm sạch khoảng trắng thừa và ngắt dòng."""
    if not text:
        return ""
    text = re.sub(r'\r\n|\r', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def extract_article(url: str) -> dict:
    """
    Cào nội dung chi tiết bài báo từ URL.
    Hỗ trợ Tuổi Trẻ, VnExpress, CafeF, SGGP, Thanh Niên, Báo Xây Dựng, Dân Trí, VietnamNet,...
    """
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding or "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")
    except Exception as e:
        return {
            "success": False,
            "error": f"Lỗi kết nối tải trang: {str(e)}",
            "url": url
        }

    # Bóc tách tiêu đề
    title = ""
    title_tags = [
        soup.find("h1", class_=lambda x: x and ("title" in x.lower() or "detail" in x.lower())),
        soup.find("h1"),
        soup.find("title")
    ]
    for tag in title_tags:
        if tag and tag.get_text().strip():
            title = tag.get_text().strip()
            break

    # Bóc tách thời gian đăng
    published_date = ""
    date_tag = (
        soup.find(class_=lambda x: x and any(k in x.lower() for k in ["date", "time", "published"])) or
        soup.find("time") or
        soup.find("meta", property="article:published_time")
    )
    if date_tag:
        if date_tag.name == "meta" and date_tag.get("content"):
            published_date = date_tag.get("content").strip()
        else:
            published_date = date_tag.get_text().strip()

    # Bóc tách tác giả / nguồn
    author = ""
    author_tag = soup.find(class_=lambda x: x and any(k in x.lower() for k in ["author", "tac-gia", "nguon"]))
    if author_tag:
        author = author_tag.get_text().strip()

    # Xóa các thành phần rác trước khi lấy body
    for junk in soup.find_all(["script", "style", "nav", "footer", "aside", "form"]):
        junk.decompose()

    # Tìm phần thân bài viết
    content_selectors = [
        {"class_": lambda x: x and any(c in x.lower() for c in ["detail-content", "content-detail", "fck_detail", "maincontent", "content_detail", "singular-content", "entry-content"])},
        {"id": lambda x: x and any(c in x.lower() for c in ["content", "main-content", "article-body"])},
        {"class_": lambda x: x and "content" in x.lower()}
    ]

    body_tag = None
    for selector in content_selectors:
        body_tag = soup.find("article", **selector) or soup.find("div", **selector)
        if body_tag:
            break

    if not body_tag:
        body_tag = soup.find("article") or soup.body

    paragraphs = []
    if body_tag:
        for p in body_tag.find_all(["p", "h2", "h3"]):
            p_text = p.get_text().strip()
            # Bỏ qua các text quảng cáo ngắn hoặc link bài liên quan
            if len(p_text) > 15 and not p_text.startswith(">>") and not p_text.startswith("Xem thêm"):
                paragraphs.append(p_text)

    full_text = "\n\n".join(paragraphs)

    return {
        "success": True,
        "url": url,
        "title": clean_text(title),
        "published_date": clean_text(published_date),
        "author": clean_text(author),
        "content": clean_text(full_text),
        "crawled_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

if __name__ == "__main__":
    import sys
    test_url = sys.argv[1] if len(sys.argv) > 1 else "https://tuoitre.vn/khoi-cong-cau-cat-lai-va-cau-long-hung-noi-dong-nai-voi-tphcm-100260929111812275.htm"
    print(f"[*] Cào thử nghiệm: {test_url}")
    res = extract_article(test_url)
    if res.get("success"):
        print(f"[OK] Tiêu đề: {res['title']}")
        print(f"[OK] Ngày đăng: {res['published_date']}")
        print(f"[OK] Độ dài nội dung: {len(res['content'])} ký tự")
    else:
        print(f"[X] Lỗi: {res.get('error')}")
