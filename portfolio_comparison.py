import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

INPUT_FILE = "data/optimized_portfolio.csv"
OUTPUT_FILE = "data/portfolio_comparison.csv"
CHART_FILE = "data/portfolio_comparison.png"

df = pd.read_csv(INPUT_FILE)

df["date"] = pd.to_datetime(df["date"])
df = df.sort_values(["date", "ticker"])

# Equal-weight portfolio
n_stocks = df["ticker"].nunique()

df["equal_weight"] = 1 / n_stocks

df["equal_weight_return"] = (
    df["equal_weight"] * df["return"]
)

df["sentiment_weight_return"] = (
    df["portfolio_weight"] * df["return"]
)

# Daily portfolio returns
comparison = (
    df.groupby("date")
    .agg(
        equal_weight_return=("equal_weight_return", "sum"),
        sentiment_weight_return=("sentiment_weight_return", "sum")
    )
    .reset_index()
)

# Cumulative portfolio value
comparison["equal_weight_cumulative"] = (
    1 + comparison["equal_weight_return"]
).cumprod()

comparison["sentiment_cumulative"] = (
    1 + comparison["sentiment_weight_return"]
).cumprod()


def calculate_metrics(returns):

    returns = returns.dropna()

    total_return = (
        (1 + returns).prod() - 1
    )

    volatility = (
        returns.std() * np.sqrt(252)
    )

    sharpe = (
        (returns.mean() * 252) / volatility
        if volatility != 0
        else np.nan
    )

    wealth = (1 + returns).cumprod()

    running_max = wealth.cummax()

    drawdown = (
        wealth / running_max
    ) - 1

    max_drawdown = drawdown.min()

    return {
        "Trading Days": len(returns),
        "Total Return": total_return,
        "Annualized Volatility": volatility,
        "Sharpe Ratio": sharpe,
        "Maximum Drawdown": max_drawdown
    }


equal_metrics = calculate_metrics(
    comparison["equal_weight_return"]
)

sentiment_metrics = calculate_metrics(
    comparison["sentiment_weight_return"]
)


print("\n==============================")
print("PORTFOLIO COMPARISON")
print("==============================")

print("\nEqual-Weight Portfolio")

for metric, value in equal_metrics.items():
    print(f"{metric}: {value:.4f}")


print("\nSentiment-Weighted Portfolio")

for metric, value in sentiment_metrics.items():
    print(f"{metric}: {value:.4f}")


print("\n==============================")
print("FINAL PORTFOLIO VALUES")
print("==============================")

print(
    f"Equal Weight: "
    f"{comparison['equal_weight_cumulative'].iloc[-1]:.4f}"
)

print(
    f"Sentiment Weight: "
    f"{comparison['sentiment_cumulative'].iloc[-1]:.4f}"
)


# Save comparison data
comparison.to_csv(
    OUTPUT_FILE,
    index=False
)


# Create chart
plt.figure(figsize=(10, 6))

plt.plot(
    comparison["date"],
    comparison["equal_weight_cumulative"],
    marker="o",
    label="Equal-Weight Portfolio"
)

plt.plot(
    comparison["date"],
    comparison["sentiment_cumulative"],
    marker="o",
    label="Sentiment-Weighted Portfolio"
)

plt.title(
    "Equal-Weight vs Sentiment-Weighted Portfolio"
)

plt.xlabel("Date")
plt.ylabel("Portfolio Value")

plt.legend()

plt.grid(True, alpha=0.3)

plt.tight_layout()

plt.savefig(
    CHART_FILE,
    dpi=200
)

plt.close()


print(
    f"\nSaved comparison data to {OUTPUT_FILE}"
)

print(
    f"Saved performance chart to {CHART_FILE}"
)
