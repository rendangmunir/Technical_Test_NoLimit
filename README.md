# Technical_Test_NoLimit

# Bisnis.com Article Crawler

A web crawler and scraper for [bisnis.com](https://www.bisnis.com), built in Python. It supports two crawling modes:

- ✅ **Standard Mode** – Periodically scrapes the latest articles from the homepage. Can Adjust Interval by changing INTERVAL value on standard.py
- 📆 **Backtrack Mode** – Crawls historical articles from the archive by date range.

---

## 📁 Project Structure
```
.
├── scraper.py # Core scraping logic used by both modes
├── standard.py # Runs periodic crawler for new articles
├── backtrack.py # Scrapes articles in a given date range
├── output/ # Stores resulting JSON files
└── README.md
```

## Installation
1. Clone this repository
```
git clone https://github.com/rendangmunir/Technical_Test_NoLimit
cd Technical_Test_NoLimit
```
3. (optional) create python venv
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
5. Install requirements `pip install -r requirements.txt`


## How To Use
1. Standard, output: `output/latest_{timestamp}.json`
  ```
python standard.py
```
3. Backtrack, output: `output/backtrack_output.json`
```
python backtrack.py --start 2025-05-01 --end 2025-05-02 --output output/backtrack_output.json
```

## Output Format
Each article is saved in the following JSON structure:
```
{
  "url": "https://...",
  "title": "Article Title",
  "date": "2025-07-09T02:00:00",
  "content": "Full article text..."
}
```
Note: some article contains premium content, so data might not be complete.
