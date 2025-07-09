# backtrack.py
import argparse
import json
import os
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from scraper import parse_article, get_article_id, is_article_url
from concurrent.futures import ThreadPoolExecutor, as_completed

MAX_WORKERS = 10
os.makedirs("output", exist_ok=True)
CATEGORY_ID =[
    "all", #supposedly all but pagination isn't working lol
    1, #Rekomendasi
    655, #Premium
    194, #Market
    5, #Finansial
    43, #Ekonomi
    277, #Tekno
    197, #Style
    186, #Kabar24
    392, #Bola
    547, #Infografik
    272, #Otomotif
    258, #Entreprenur
    222, #Travel
    382, #Jakarta
    548, #Bandung
    420, #Banten
    528, #Semarang
    526, #Surabaya
    529, #Bali
    527, #Sumatra
    406, #Kalimantan
    530, #Sulawesi
    413, #Papua
    242, #Koran
    638, #Viral
    390, #Ramalan
]
def get_total_pages(soup):
    total_page_input = soup.find("input", {"id": "total_page"})
    if total_page_input and total_page_input.has_attr("value"):
        try:
            return int(total_page_input["value"])
        except ValueError:
            return 1
    return 1

def get_article_links_from_index(url):
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
    except Exception:
        return [], None

    links = []
    for a in soup.select("a.artLink"):
        href = a.get("href")
        if href and is_article_url(href):
            links.append(href)

    total_pages = get_total_pages(soup)
    return links, total_pages

def generate_index_urls_for_date(date_str):
    base_url = "https://www.bisnis.com/index?categoryId=0&type=indeks"
    urls = []

    first_url = f"{base_url}&date={date_str}&page=1"
    first_links, total_pages = get_article_links_from_index(first_url)
    urls.append((first_url, first_links))

    for page in range(2, total_pages + 1):
        page_url = f"{base_url}&date={date_str}&page={page}"
        page_links, _ = get_article_links_from_index(page_url)
        urls.append((page_url, page_links))

    return urls

def backtrack_mode(start, end, output_file):
    visited_ids = set()
    articles = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []

        current = start
        while current <= end:
            date_str = current.strftime("%Y-%m-%d")
            print(f"📆 Crawling archive for date: {date_str}")
            
            for category_id in CATEGORY_ID:
                print(f"  📂 Category ID: {category_id}")
                base_url = f"https://www.bisnis.com/index?categoryId={category_id}&type=indeks"
                
                first_url = f"{base_url}&date={date_str}&page=1"
                first_links, total_pages = get_article_links_from_index(first_url)

                if not first_links:
                    print(f"    ⚠️ No articles found in category {category_id} on {date_str}")
                    continue

                indexed_pages = [(first_url, first_links)]

                for page in range(2, total_pages + 1):
                    page_url = f"{base_url}&date={date_str}&page={page}"
                    page_links, _ = get_article_links_from_index(page_url)
                    if not page_links:
                        print(f"    ⚠️ No articles on page {page} for category {category_id}")
                        continue
                    indexed_pages.append((page_url, page_links))

                for page_url, links in indexed_pages:
                    print(f"    🔍 Page: {page_url} - {len(links)} links")
                    for url in links:
                        article_id = get_article_id(url)
                        if article_id and article_id not in visited_ids:
                            visited_ids.add(article_id)
                            futures.append(executor.submit(parse_article, url))

            current += timedelta(days=1)

        for future in as_completed(futures):
            article = future.result()
            if article:
                articles.append(article)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved {len(articles)} articles to {output_file}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--start', required=True, help="Start date in YYYY-MM-DD")
    parser.add_argument('--end', required=True, help="End date in YYYY-MM-DD")
    parser.add_argument('--output', default='output/backtrack_output.json', help="Output JSON file")
    args = parser.parse_args()

    start_date = datetime.strptime(args.start, "%Y-%m-%d")
    end_date = datetime.strptime(args.end, "%Y-%m-%d")

    backtrack_mode(start_date, end_date, args.output)
