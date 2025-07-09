# scraper.py
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

MAX_WORKERS = 10

visited_urls = set()
visited_ids = set()

def is_article_url(url):
    return '/read/' in url and url.startswith("https://") and "bisnis.com" in urlparse(url).netloc

def get_article_id(url):
    match = re.search(r"/read/\d+/\d+/(\d+)", url)
    return match.group(1) if match else None

def normalize_url(base, link):
    return urljoin(base, link)

def get_links(soup, base_url):
    anchors = soup.find_all("a", href=True)
    urls = set()
    for a in anchors:
        href = a["href"]
        full_url = normalize_url(base_url, href)
        if full_url.startswith("https://") and "bisnis.com" in urlparse(full_url).netloc:
            urls.add(full_url)
    return urls

def parse_article(url):
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
    except Exception:
        return None

    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else ''

    meta_date = soup.find("meta", attrs={"name": "publishdate"})
    date_str = meta_date["content"] if meta_date and meta_date.has_attr("content") else 'premium content'
    try:
        date_obj = datetime.strptime(date_str, "%Y/%m/%d %H:%M:%S")
        iso_date = date_obj.isoformat()
    except Exception:
        iso_date = date_str

    article = soup.select_one("article.detailsContent")
    if not article:
        return {
            "url": url,
            "title": title,
            "date": iso_date,
            "content": 'premium content'
        }

    paragraphs = []
    for p in article.find_all("p"):
        if p.get("class") and ("disclaimer" in p.get("class") or "baca-juga-title" in p.get("class")):
            continue
        if p.find_parent("div", class_="baca-juga-box"):
            continue
        text = p.get_text(strip=False)
        if text:
            paragraphs.append(text)

    content = "\n".join(paragraphs)
    return {
        "url": url,
        "title": title,
        "date": iso_date,
        "content": content
    }

def crawl_site(start_url, max_depth=1):
    articles = []
    to_visit = [(start_url, 0)]
    seen = set()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        while to_visit:
            url, depth = to_visit.pop()
            if url in seen or depth > max_depth:
                continue
            seen.add(url)

            try:
                res = requests.get(url, timeout=10)
                soup = BeautifulSoup(res.text, 'html.parser')
            except Exception:
                continue

            if is_article_url(url):
                article_id = get_article_id(url)
                if article_id and article_id in visited_ids:
                    continue
                visited_ids.add(article_id)
                future = executor.submit(parse_article, url)
                articles.append(future)

            for link in get_links(soup, url):
                if link not in seen:
                    to_visit.append((link, depth + 1))

        # Gather all parsed article results
        results = []
        for future in as_completed(articles):
            article = future.result()
            if article:
                results.append(article)
    return results
