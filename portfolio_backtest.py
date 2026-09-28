import numpy as np
import pandas as pd

INPUT_FILE = "data/strategy_dataset.csv"
OUTPUT_FILE = "data/portfolio_results.csv"

# ---------------------------------------------------------
# 1. Load strategy dataset
# ---------------------------------------------------------

df = pd.read_csv(INPUT_FILE)
df["date"] = pd.to_datetime(df["date"])

df = df.sort_values(["date", "ticker"])


# ---------------------------------------------------------
# 2. Create equal-weight portfolio
# ---------------------------------------------------------

# Each stock receives equal weight
n_stocks = df["ticker"].nunique()
equal_weight = 1 / n_stocks

df["equal_weight"] = equal_weight


# ---------------------------------------------------------
# 3. Create sentiment-based weights
# ---------------------------------------------------------

# Cross-sectional sentiment score for each day
df["sentiment_rank"] = (
    df.groupby("date")["lagged_sentiment"]
    .rank(method="first", ascending=False)
)

# Convert rank into a positive score.
# Higher sentiment = higher portfolio weight.
df["rank_score"] = (
    n_stocks - df["sentiment_rank"] + 1
)

# Normalize weights so they sum to 1 each day
df["sentiment_weight"] = (
    df["rank_score"]
    / df.groupby("date")["rank_score"].transform("sum")
)


# ---------------------------------------------------------
# 4. Calculate portfolio returns
# ---------------------------------------------------------

df["equal_contribution"] = (
    df["equal_weight"] * df["return"]
)

df["sentiment_contribution"] = (
    df["sentiment_weight"] * df["return"]
)

portfolio = (
    df.groupby("date")
    .agg(
        equal_weight_return=("equal_contribution", "sum"),
        sentiment_return=("sentiment_contribution", "sum")
    )
    .reset_index()
)


# ---------------------------------------------------------
# 5. Calculate cumulative returns
# ---------------------------------------------------------

portfolio["equal_cumulative"] = (
    1 + portfolio["equal_weight_return"]
).cumprod()

portfolio["sentiment_cumulative"] = (
    1 + portfolio["sentiment_return"]
).cumprod()


# ---------------------------------------------------------
# 6. Performance metrics
# ---------------------------------------------------------

def calculate_metrics(returns):

    returns = returns.dropna()

    cumulative_return = (
        (1 + returns).prod() - 1
    )

    annualized_return = (
        (1 + cumulative_return)
        ** (252 / len(returns)) - 1
    )

    annualized_volatility = (
        returns.std() * np.sqrt(252)
    )

    sharpe_ratio = (
        annualized_return / annualized_volatility
        if annualized_volatility != 0
        else np.nan
    )

    cumulative = (1 + returns).cumprod()

    running_max = cumulative.cummax()

    drawdown = (
        cumulative / running_max - 1
    )

    max_drawdown = drawdown.min()

    return {
        "Total Return": cumulative_return,
        "Annualized Return": annualized_return,
        "Annualized Volatility": annualized_volatility,
        "Sharpe Ratio": sharpe_ratio,
        "Maximum Drawdown": max_drawdown
    }


# ---------------------------------------------------------
# 7. Print results
# ---------------------------------------------------------

equal_metrics = calculate_metrics(
    portfolio["equal_weight_return"]
)

sentiment_metrics = calculate_metrics(
    portfolio["sentiment_return"]
)

print("\n==============================")
print("PORTFOLIO BACKTEST RESULTS")
print("==============================")

print("\nEqual-Weight Portfolio")

for metric, value in equal_metrics.items():
    print(f"{metric}: {value:.4f}")


print("\nSentiment-Based Portfolio")

for metric, value in sentiment_metrics.items():
    print(f"{metric}: {value:.4f}")


# ---------------------------------------------------------
# 8. Save results
# ---------------------------------------------------------

portfolio.to_csv(
    OUTPUT_FILE,
    index=False
)

print(
    f"\nSaved portfolio results to {OUTPUT_FILE}"
)
