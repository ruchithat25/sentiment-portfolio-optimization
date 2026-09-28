import pandas as pd

INPUT_FILE = "data/headlines.csv"
OUTPUT_FILE = "data/headlines_clean.csv"


# Load headlines
df = pd.read_csv(INPUT_FILE)

print(f"Original headlines: {len(df)}")

# Remove duplicate headlines for the same ticker
df = df.drop_duplicates(subset=["ticker", "headline"])

# Remove rows with missing headlines
df = df.dropna(subset=["headline"])

# Sort by ticker and date
df = df.sort_values(["ticker", "date"])

# Save cleaned data
df.to_csv(OUTPUT_FILE, index=False)

print(f"Clean headlines: {len(df)}")
print(f"\nSaved to {OUTPUT_FILE}")

print("\nHeadlines per ticker:")
print(df.groupby("ticker").size())
