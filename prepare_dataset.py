import pandas as pd

PRICE_FILE = "data/prices.csv"
SENTIMENT_FILE = "data/daily_sentiment.csv"
OUTPUT_FILE = "data/modeling_dataset.csv"

prices = pd.read_csv(PRICE_FILE)
sentiment = pd.read_csv(SENTIMENT_FILE)

prices["date"] = pd.to_datetime(prices["date"])
sentiment["date"] = pd.to_datetime(sentiment["date"])

prices = prices.sort_values(["ticker", "date"])
sentiment = sentiment.sort_values(["ticker", "date"])

# Calculate daily returns
prices["return"] = (
    prices.groupby("ticker")["close"].pct_change()
)

# Keep required price columns
returns = prices[
    ["date", "ticker", "close", "return"]
].copy()


# --------------------------------------------------
# Carry forward sentiment for up to 3 trading days
# --------------------------------------------------

sentiment_parts = []

for ticker, group in sentiment.groupby("ticker"):

    group = group.sort_values("date").copy()

    # Reindex sentiment to trading dates for this stock
    ticker_prices = returns[
        returns["ticker"] == ticker
    ][["date"]].copy()

    group = (
        group.set_index("date")
        .reindex(ticker_prices["date"])
    )

    # Restore date
    group.index.name = "date"
    group = group.reset_index()

    group["ticker"] = ticker

    # Track whether sentiment was originally available
    group["sentiment_available"] = (
        group["sentiment_score"].notna()
    )

    # Carry sentiment forward for at most 3 trading days
    group["sentiment_score"] = (
        group["sentiment_score"]
        .ffill(limit=3)
    )

    # Headline count is zero when sentiment was carried forward
    group["headline_count"] = (
        group["headline_count"]
        .fillna(0)
    )

    sentiment_parts.append(group)


sentiment_extended = pd.concat(
    sentiment_parts,
    ignore_index=True
)


# --------------------------------------------------
# Merge price + sentiment
# --------------------------------------------------

dataset = pd.merge(
    returns,
    sentiment_extended[
        [
            "date",
            "ticker",
            "sentiment_score",
            "headline_count",
            "sentiment_available"
        ]
    ],
    on=["date", "ticker"],
    how="inner"
)


# Remove rows without a usable sentiment signal
dataset = dataset.dropna(
    subset=["sentiment_score"]
)

dataset = dataset.sort_values(
    ["ticker", "date"]
)


# Save
dataset.to_csv(
    OUTPUT_FILE,
    index=False
)


print(f"Saved {len(dataset)} rows to {OUTPUT_FILE}")

print("\nColumns:")
print(dataset.columns.tolist())

print("\nRows per ticker:")
print(dataset.groupby("ticker").size())

print("\nSentiment coverage:")
print(
    dataset.groupby("ticker")["sentiment_available"]
    .agg(["sum", "count"])
)

print("\nFirst 10 rows:")
print(dataset.head(10))