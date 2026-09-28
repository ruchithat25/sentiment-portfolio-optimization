import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

INPUT_FILE = "data/optimized_portfolio.csv"
OUTPUT_FILE = "data/portfolio_comparison.csv"
CHART_FILE = "data/portfolio_comparison.png"

TRANSACTION_COST = 0.001


# --------------------------------------------------
# Load data
# --------------------------------------------------

df = pd.read_csv(INPUT_FILE)

df["date"] = pd.to_datetime(df["date"])

df = df.sort_values(
    ["date", "ticker"]
)


# --------------------------------------------------
# Portfolio definitions
# --------------------------------------------------

n_stocks = df["ticker"].nunique()

# Equal-weight benchmark
df["equal_weight"] = 1 / n_stocks


# --------------------------------------------------
# Daily gross returns
# --------------------------------------------------

df["equal_weight_return"] = (
    df["equal_weight"] * df["return"]
)

df["sentiment_weight_return"] = (
    df["portfolio_weight"] * df["return"]
)


# --------------------------------------------------
# Equal-weight turnover
# --------------------------------------------------

df["previous_equal_weight"] = (
    df.groupby("ticker")[
        "equal_weight"
    ].shift(1)
)

df["equal_weight_change"] = (
    df["equal_weight"]
    - df["previous_equal_weight"]
)

# Initial portfolio formation
df["equal_weight_change"] = (
    df["equal_weight_change"]
    .fillna(df["equal_weight"])
)


# --------------------------------------------------
# Sentiment portfolio turnover
# --------------------------------------------------

df["previous_sentiment_weight"] = (
    df.groupby("ticker")[
        "portfolio_weight"
    ].shift(1)
)

df["sentiment_weight_change"] = (
    df["portfolio_weight"]
    - df["previous_sentiment_weight"]
)

# Initial portfolio formation
df["sentiment_weight_change"] = (
    df["sentiment_weight_change"]
    .fillna(df["portfolio_weight"])
)


# --------------------------------------------------
# Aggregate turnover
# --------------------------------------------------

turnover = (
    df.groupby("date")
    .agg(
        equal_turnover=(
            "equal_weight_change",
            lambda x: x.abs().sum()
        ),
        sentiment_turnover=(
            "sentiment_weight_change",
            lambda x: x.abs().sum()
        )
    )
    .reset_index()
)


# --------------------------------------------------
# Separate initial formation turnover
# --------------------------------------------------

first_date = turnover["date"].min()

turnover["initial_formation"] = (
    turnover["date"] == first_date
)

turnover["equal_ongoing_turnover"] = (
    turnover["equal_turnover"]
)

turnover["sentiment_ongoing_turnover"] = (
    turnover["sentiment_turnover"]
)

turnover.loc[
    turnover["initial_formation"],
    "equal_ongoing_turnover"
] = 0.0

turnover.loc[
    turnover["initial_formation"],
    "sentiment_ongoing_turnover"
] = 0.0


# --------------------------------------------------
# Create comparison dataset
# --------------------------------------------------

comparison = (
    df.groupby("date")
    .agg(
        equal_weight_return=(
            "equal_weight_return",
            "sum"
        ),
        sentiment_weight_return=(
            "sentiment_weight_return",
            "sum"
        )
    )
    .reset_index()
)


comparison = comparison.merge(
    turnover,
    on="date",
    how="left"
)


# --------------------------------------------------
# Transaction costs
# --------------------------------------------------

comparison["equal_transaction_cost"] = (
    comparison["equal_turnover"]
    * TRANSACTION_COST
)

comparison["sentiment_transaction_cost"] = (
    comparison["sentiment_turnover"]
    * TRANSACTION_COST
)


# --------------------------------------------------
# Net returns
# --------------------------------------------------

comparison["equal_net_return"] = (
    comparison["equal_weight_return"]
    - comparison["equal_transaction_cost"]
)

comparison["sentiment_net_return"] = (
    comparison["sentiment_weight_return"]
    - comparison["sentiment_transaction_cost"]
)


# --------------------------------------------------
# Cumulative portfolio values
# --------------------------------------------------

comparison["equal_weight_cumulative"] = (
    1 + comparison["equal_net_return"]
).cumprod()

comparison["sentiment_cumulative"] = (
    1 + comparison["sentiment_net_return"]
).cumprod()


# --------------------------------------------------
# Performance metrics
# --------------------------------------------------

def calculate_metrics(returns):

    returns = returns.dropna()

    total_return = (
        1 + returns
    ).prod() - 1

    volatility = (
        returns.std()
        * np.sqrt(252)
    )

    sharpe = (
        (returns.mean() * 252)
        / volatility
        if volatility != 0
        else np.nan
    )

    wealth = (
        1 + returns
    ).cumprod()

    running_max = (
        wealth.cummax()
    )

    drawdown = (
        wealth / running_max
    ) - 1

    max_drawdown = (
        drawdown.min()
    )

    return {
        "Trading Days": len(returns),
        "Total Return": total_return,
        "Annualized Volatility": volatility,
        "Sharpe Ratio": sharpe,
        "Maximum Drawdown": max_drawdown
    }


equal_metrics = calculate_metrics(
    comparison["equal_net_return"]
)

sentiment_metrics = calculate_metrics(
    comparison["sentiment_net_return"]
)


# --------------------------------------------------
# Print performance
# --------------------------------------------------

print("\n==============================")
print("PORTFOLIO COMPARISON")
print("==============================")


print("\nEqual-Weight Portfolio")

for metric, value in equal_metrics.items():

    if metric == "Trading Days":
        print(
            f"{metric}: {int(value)}"
        )
    else:
        print(
            f"{metric}: {value:.4f}"
        )


print("\nSentiment-Weighted Portfolio")

for metric, value in sentiment_metrics.items():

    if metric == "Trading Days":
        print(
            f"{metric}: {int(value)}"
        )
    else:
        print(
            f"{metric}: {value:.4f}"
        )


# --------------------------------------------------
# Turnover analysis
# --------------------------------------------------

print("\n==============================")
print("TURNOVER ANALYSIS")
print("==============================")

print(
    f"Transaction cost rate: "
    f"{TRANSACTION_COST:.4%}"
)

print(
    f"Equal-weight initial turnover: "
    f"{turnover.loc[turnover['initial_formation'], 'equal_turnover'].iloc[0]:.4f}"
)

print(
    f"Sentiment initial turnover: "
    f"{turnover.loc[turnover['initial_formation'], 'sentiment_turnover'].iloc[0]:.4f}"
)

print(
    f"Equal-weight average ongoing turnover: "
    f"{turnover['equal_ongoing_turnover'].mean():.4f}"
)

print(
    f"Sentiment average ongoing turnover: "
    f"{turnover['sentiment_ongoing_turnover'].mean():.4f}"
)

print(
    f"Equal-weight total transaction costs: "
    f"{comparison['equal_transaction_cost'].sum():.4f}"
)

print(
    f"Sentiment total transaction costs: "
    f"{comparison['sentiment_transaction_cost'].sum():.4f}"
)


# --------------------------------------------------
# Final portfolio values
# --------------------------------------------------

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


# --------------------------------------------------
# Save comparison data
# --------------------------------------------------

comparison.to_csv(
    OUTPUT_FILE,
    index=False
)


# --------------------------------------------------
# Performance chart
# --------------------------------------------------

plt.figure(
    figsize=(10, 6)
)

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

plt.grid(
    True,
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    CHART_FILE,
    dpi=200
)

plt.close()


print(
    f"\nSaved comparison data to "
    f"{OUTPUT_FILE}"
)

print(
    f"Saved performance chart to "
    f"{CHART_FILE}"
)