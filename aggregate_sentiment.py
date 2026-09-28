import pandas as pd

INPUT_FILE = "data/sentiment_scores.csv"
OUTPUT_FILE = "data/daily_sentiment.csv"

df = pd.read_csv(INPUT_FILE)

# Convert timestamps to calendar dates
df["date"] = pd.to_datetime(df["date"], utc=True).dt.date

# Aggregate all headlines published on the same day
daily_sentiment = (
    df.groupby(["ticker", "date"])
    .agg(
        sentiment_score=("sentiment_score", "mean"),
        headline_count=("headline", "count")
    )
    .reset_index()
)

daily_sentiment["date"] = pd.to_datetime(
    daily_sentiment["date"]
)

daily_sentiment = daily_sentiment.sort_values(
    ["ticker", "date"]
)

daily_sentiment.to_csv(
    OUTPUT_FILE,
    index=False
)

print(
    f"Saved {len(daily_sentiment)} daily sentiment records"
)

print(f"\nFile: {OUTPUT_FILE}")

print("\nFirst 10 rows:")
print(daily_sentiment.head(10))

print("\nDaily records per ticker:")
print(
    daily_sentiment.groupby("ticker").size()
)