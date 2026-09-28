import pandas as pd

INPUT_FILE = "data/modeling_dataset.csv"

df = pd.read_csv(INPUT_FILE)

# Calculate correlation between sentiment and same-day return
correlation = (
    df.groupby("ticker")
    .apply(lambda x: x["sentiment_score"].corr(x["return"]))
    .reset_index(name="sentiment_return_correlation")
)

print("\nSentiment vs Return Correlation")
print(correlation.to_string(index=False))

# Overall correlation
overall = df["sentiment_score"].corr(df["return"])

print(f"\nOverall correlation: {overall:.4f}")
