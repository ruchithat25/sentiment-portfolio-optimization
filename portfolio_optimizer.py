import pandas as pd
import numpy as np

INPUT_FILE = "data/strategy_dataset.csv"
OUTPUT_FILE = "data/optimized_portfolio.csv"

MIN_WEIGHT = 0.05
MAX_WEIGHT = 0.40


df = pd.read_csv(INPUT_FILE)
df["date"] = pd.to_datetime(df["date"])

df = df.sort_values(["date", "ticker"])


# --------------------------------------------------
# Keep only dates where all stocks are available
# --------------------------------------------------

all_tickers = sorted(df["ticker"].unique())
n_stocks = len(all_tickers)

valid_dates = (
    df.groupby("date")["ticker"]
    .nunique()
)

valid_dates = valid_dates[
    valid_dates == n_stocks
].index

df = df[df["date"].isin(valid_dates)].copy()

print(f"Stocks in universe: {n_stocks}")
print(f"Valid portfolio dates: {len(valid_dates)}")


# --------------------------------------------------
# Calculate constrained sentiment weights
# --------------------------------------------------

def calculate_weights(group):

    sentiment = group["lagged_sentiment"].to_numpy(dtype=float)

    n = len(sentiment)

    # Start every stock at minimum weight
    weights = np.full(n, MIN_WEIGHT)

    remaining = 1.0 - weights.sum()

    # Convert sentiment into positive scores
    scores = sentiment - sentiment.min() + 0.1

    if scores.sum() == 0:
        scores = np.ones(n)

    scores = scores / scores.sum()

    # Allocate remaining weight according to sentiment
    weights += remaining * scores

    # --------------------------------------------------
    # Enforce maximum weight
    # --------------------------------------------------

    while np.any(weights > MAX_WEIGHT + 1e-12):

        excess = np.maximum(weights - MAX_WEIGHT, 0).sum()

        weights = np.minimum(weights, MAX_WEIGHT)

        available = weights < MAX_WEIGHT - 1e-12

        if not available.any():
            break

        available_scores = scores.copy()
        available_scores[~available] = 0

        if available_scores.sum() == 0:
            available_scores[available] = 1

        weights += (
            excess
            * available_scores
            / available_scores.sum()
        )

    # --------------------------------------------------
    # Correct tiny floating-point difference
    # --------------------------------------------------

    difference = 1.0 - weights.sum()

    if abs(difference) > 1e-12:

        available = np.where(
            weights < MAX_WEIGHT - 1e-12
        )[0]

        if len(available) > 0:
            weights[available[0]] += difference

    return pd.Series(weights, index=group.index)


# Calculate weights separately for each date
# and assign them using the original row indices.

df["portfolio_weight"] = np.nan

for date, group in df.groupby("date"):
    weights = calculate_weights(group)

    df.loc[group.index, "portfolio_weight"] = weights.values

# --------------------------------------------------
# Portfolio returns
# --------------------------------------------------

df["weighted_return"] = (
    df["portfolio_weight"] * df["return"]
)


portfolio = (
    df.groupby("date")
    .agg(
        portfolio_return=("weighted_return", "sum")
    )
    .reset_index()
)


portfolio["cumulative_return"] = (
    1 + portfolio["portfolio_return"]
).cumprod() - 1


# --------------------------------------------------
# Performance metrics
# --------------------------------------------------

returns = portfolio["portfolio_return"]

total_return = (
    1 + returns
).prod() - 1

volatility = (
    returns.std() * np.sqrt(252)
)

sharpe = (
    (returns.mean() * 252) / volatility
    if volatility != 0
    else np.nan
)

wealth = (
    1 + returns
).cumprod()

running_max = wealth.cummax()

drawdown = (
    wealth / running_max
) - 1

max_drawdown = drawdown.min()


# --------------------------------------------------
# Results
# --------------------------------------------------

print("\n==============================")
print("SENTIMENT PORTFOLIO")
print("==============================")

print(f"Total Return: {total_return:.4f}")
print(f"Annualized Volatility: {volatility:.4f}")
print(f"Sharpe Ratio: {sharpe:.4f}")
print(f"Maximum Drawdown: {max_drawdown:.4f}")


# --------------------------------------------------
# Weight validation
# --------------------------------------------------

print("\n==============================")
print("WEIGHT VALIDATION")
print("==============================")

print(
    f"Minimum weight observed: "
    f"{df['portfolio_weight'].min():.4f}"
)

print(
    f"Maximum weight observed: "
    f"{df['portfolio_weight'].max():.4f}"
)

daily_weight_sum = (
    df.groupby("date")["portfolio_weight"]
    .sum()
)

print(
    f"Minimum daily weight sum: "
    f"{daily_weight_sum.min():.4f}"
)

print(
    f"Maximum daily weight sum: "
    f"{daily_weight_sum.max():.4f}"
)


# --------------------------------------------------
# Save
# --------------------------------------------------

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print(
    f"\nSaved portfolio weights to "
    f"{OUTPUT_FILE}"
)

print("\nSample weights:")

print(
    df[
        [
            "date",
            "ticker",
            "lagged_sentiment",
            "portfolio_weight"
        ]
    ].head(15)
)