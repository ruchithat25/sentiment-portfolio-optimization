import pandas as pd

INPUT_FILE = "data/modeling_dataset.csv"
OUTPUT_FILE = "data/strategy_dataset.csv"

# Load dataset
df = pd.read_csv(INPUT_FILE)

# Convert date
df["date"] = pd.to_datetime(df["date"])

# Sort by stock and date
df = df.sort_values(["ticker", "date"])

# Shift sentiment by one trading observation
# Today's return will use the previous available day's sentiment.
df["lagged_sentiment"] = (
    df.groupby("ticker")["sentiment_score"].shift(1)
)

# Remove rows where previous-day sentiment doesn't exist
df = df.dropna(subset=["lagged_sentiment"])

# Save
df.to_csv(OUTPUT_FILE, index=False)

print(f"Saved {len(df)} rows to {OUTPUT_FILE}")

print("\nFirst 10 rows:")
print(
    df[
        [
            "date",
            "ticker",
            "return",
            "sentiment_score",
            "lagged_sentiment"
        ]
    ].head(10)
)

# Correlation between previous-day sentiment and today's return
print("\nLagged sentiment vs today's return:")

correlation = (
    df.groupby("ticker")
    .apply(
        lambda x: x["lagged_sentiment"].corr(x["return"])
    )
    .reset_index(name="lagged_correlation")
)

print(correlation.to_string(index=False))

overall = df["lagged_sentiment"].corr(df["return"])

print(f"\nOverall lagged correlation: {overall:.4f}")