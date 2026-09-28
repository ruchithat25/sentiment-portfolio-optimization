import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification


MODEL_NAME = "ProsusAI/finbert"

INPUT_FILE = "data/headlines_clean.csv"
OUTPUT_FILE = "data/sentiment_scores.csv"


print("Loading FinBERT...")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

model.eval()


# Load cleaned headlines
df = pd.read_csv(INPUT_FILE)

print(f"Processing {len(df)} headlines...\n")


results = []

for i, row in df.iterrows():

    headline = row["headline"]

    inputs = tokenizer(
        headline,
        return_tensors="pt",
        truncation=True,
        max_length=512
    )

    with torch.no_grad():
        outputs = model(**inputs)

    probabilities = torch.softmax(outputs.logits, dim=1)[0]

    positive = probabilities[0].item()
    negative = probabilities[1].item()
    neutral = probabilities[2].item()

    # Sentiment score: positive probability - negative probability
    sentiment_score = positive - negative

    results.append({
        "ticker": row["ticker"],
        "date": row["date"],
        "headline": headline,
        "source": row["source"],
        "positive": positive,
        "negative": negative,
        "neutral": neutral,
        "sentiment_score": sentiment_score
    })

    if (i + 1) % 25 == 0:
        print(f"Processed {i + 1}/{len(df)} headlines")


# Convert results to dataframe
sentiment_df = pd.DataFrame(results)

# Save results
sentiment_df.to_csv(OUTPUT_FILE, index=False)

print("\nSentiment analysis complete!")
print(f"Saved {len(sentiment_df)} rows to {OUTPUT_FILE}")

print("\nFirst 5 results:")
print(sentiment_df.head())