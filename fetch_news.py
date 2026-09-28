"""
Week 1, part 2: pull recent headlines for each company and save one CSV
(one row per headline, tagged with its ticker).

IMPORTANT — NewsAPI free tier limitation:
The free "Developer" plan only returns articles from the last 30 days.
It CANNOT backfill a few months of history for free. Two options:
  1. For this first pass, just work with the last 30 days of headlines —
     it's enough to build and test the full pipeline end-to-end.
  2. If you want a longer history later, look at a free/cheap alternative
     like GDELT (no key needed, goes back years) or scraping RSS feeds.
Don't let this block you — start with option 1 and get the pipeline
working; you can always swap the data source later without changing the
rest of your code.

Run: python fetch_news.py
"""

import time
from datetime import datetime, timedelta

import pandas as pd
import requests

from config import NEWS_API_KEY, TICKER_TO_NAME, TICKERS

BASE_URL = "https://newsapi.org/v2/everything"


def fetch_headlines_for_ticker(ticker, query, from_date, to_date, api_key):
    """Fetch headlines mentioning one company within a date range."""
    params = {
        "q": query,
        "from": from_date,
        "to": to_date,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 100,
        "apiKey": api_key,
    }
    resp = requests.get(BASE_URL, params=params, timeout=15)
    resp.raise_for_status()
    payload = resp.json()
    if payload.get("status") != "ok":
        print(f"  Warning: API returned an error for {query}: {payload.get('message')}")
        return []

    rows = []
    for article in payload.get("articles", []):
        rows.append(
            {
                "ticker": ticker,
                "date": article["publishedAt"][:10],
                "headline": article["title"],
                "source": article["source"]["name"],
            }
        )
    return rows


def fetch_all_headlines(tickers, name_map, start, end, api_key):
    all_rows = []
    for ticker in tickers:
        name = name_map.get(ticker, ticker)
        print(f"Fetching headlines for {name}...")
        rows = fetch_headlines_for_ticker(ticker, name, start, end, api_key)
        print(f"  Got {len(rows)} headlines")
        all_rows.extend(rows)
        time.sleep(1)  # stay well under the free tier's rate limit
    return pd.DataFrame(all_rows)


if __name__ == "__main__":
    if NEWS_API_KEY == "YOUR_NEWSAPI_KEY_HERE":
        raise SystemExit("Set NEWS_API_KEY in config.py first — get a free key at https://newsapi.org/register")

    end = datetime.today().strftime("%Y-%m-%d")
    start = (datetime.today() - timedelta(days=29)).strftime("%Y-%m-%d")  # free tier's 30-day window

    headlines = fetch_all_headlines(TICKERS, TICKER_TO_NAME, start, end, NEWS_API_KEY)
    headlines.to_csv("data/headlines.csv", index=False)
    print(f"\nSaved {len(headlines)} headlines to data/headlines.csv")
    print(headlines.head())
