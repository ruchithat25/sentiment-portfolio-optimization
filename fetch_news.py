import time
import requests
import pandas as pd

from config import (
    NEWS_API_KEY,
    TICKER_TO_NAME
)

OUTPUT_FILE = "data/headlines.csv"

START_DATE = "2026-08-28"
END_DATE = "2026-09-27"

PAGE_SIZE = 100
MAX_PAGES = 3
PAUSE_SECONDS = 2


def fetch_news(ticker, company_name):

    print(f"\nFetching news for {ticker} ({company_name})...")

    articles = []

    for page in range(1, MAX_PAGES + 1):

        params = {
            "qInTitle": company_name,
            "from": START_DATE,
            "to": END_DATE,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": PAGE_SIZE,
            "page": page,
            "apiKey": NEWS_API_KEY
        }

        try:
            response = requests.get(
                "https://newsapi.org/v2/everything",
                params=params,
                timeout=30
            )

            data = response.json()

            if response.status_code != 200:
                print(
                    f"  API error: "
                    f"{response.status_code} - "
                    f"{data.get('message', 'Unknown error')}"
                )
                break

            page_articles = data.get("articles", [])

            if not page_articles:
                break

            articles.extend(page_articles)

            print(
                f"  Page {page}: "
                f"{len(page_articles)} articles"
            )

            total_results = data.get("totalResults", 0)

            if len(articles) >= total_results:
                break

            if len(page_articles) < PAGE_SIZE:
                break

            time.sleep(PAUSE_SECONDS)

        except requests.RequestException as e:
            print(f"  Request error: {e}")
            break

    rows = []

    for article in articles:

        title = article.get("title")

        if not title:
            continue

        rows.append({
            "ticker": ticker,
            "date": article.get("publishedAt"),
            "headline": title,
            "source": (
                article.get("source", {}).get("name")
            )
        })

    print(
        f"  Collected {len(rows)} usable headlines"
    )

    return rows


if __name__ == "__main__":

    if not NEWS_API_KEY:
        raise SystemExit(
            "NEWS_API_KEY not found. "
            "Check your .env file."
        )

    all_articles = []

    for ticker, company_name in TICKER_TO_NAME.items():

        rows = fetch_news(
            ticker,
            company_name
        )

        all_articles.extend(rows)

        time.sleep(PAUSE_SECONDS)

    df = pd.DataFrame(all_articles)

    if df.empty:
        raise RuntimeError(
            "No news articles were collected."
        )

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["date", "headline"]
    )

    df = df.sort_values(
        ["ticker", "date"]
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\n==============================")
    print("NEWS COLLECTION COMPLETE")
    print("==============================")

    print(
        f"Total headlines: {len(df)}"
    )

    print("\nHeadlines per ticker:")
    print(
        df.groupby("ticker").size()
    )

    print(
        f"\nSaved to {OUTPUT_FILE}"
    )