# standard.py
import time
import json
import schedule
from datetime import datetime
from scraper import crawl_site
import os

os.makedirs("output", exist_ok=True)

INTERVAL = 1  # minutes

def scrape_latest():
    print("Scraping recursively from bisnis.com... (called at)", datetime.now())
    start_url = "https://www.bisnis.com"
    articles = crawl_site(start_url, max_depth=2)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    with open(f'output/latest_{timestamp}.json', 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(articles)} articles to output/latest_{timestamp}.json")

if __name__ == "__main__":
    print(f"Running recursive crawler every {INTERVAL} minutes...")
    scrape_latest()
    schedule.every(INTERVAL).minutes.do(scrape_latest)
    while True:
        schedule.run_pending()
        time.sleep(1)
