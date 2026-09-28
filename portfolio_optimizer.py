import pandas as pd
import numpy as np

INPUT_FILE = "data/strategy_dataset.csv"
OUTPUT_FILE = "data/optimized_portfolio.csv"
RESULTS_FILE = "data/portfolio_results.csv"

MIN_WEIGHT = 0.05
MAX_WEIGHT = 0.40
TRANSACTION_COST = 0.001

df = pd.read_csv(INPUT_FILE)
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values(["date", "ticker"]).copy()


def calculate_weights(group):
    sentiment = group["lagged_sentiment"].to_numpy(dtype=float)
    n = len(sentiment)

    if n * MIN_WEIGHT > 1:
        raise ValueError(
            f"Cannot allocate {n} stocks with minimum weight {MIN_WEIGHT:.2f}"
        )

    if n * MAX_WEIGHT < 1:
        raise ValueError(
            f"Cannot allocate {n} stocks with maximum weight {MAX_WEIGHT:.2f}"
        )

    weights = np.full(n, MIN_WEIGHT)

    remaining = 1.0 - weights.sum()

    scores = sentiment - sentiment.min() + 0.1

    if scores.sum() == 0:
        scores = np.ones(n)

    scores = scores / scores.sum()

    weights += remaining * scores

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

    difference = 1.0 - weights.sum()

    if abs(difference) > 1e-12:
        available = np.where(
            weights < MAX_WEIGHT - 1e-12
        )[0]

        if len(available) > 0:
            weights[available[0]] += difference

    return pd.Series(
        weights,
        index=group.index
    )


# --------------------------------------------------
# CALCULATE DAILY PORTFOLIO WEIGHTS
# --------------------------------------------------

df["portfolio_weight"] = np.nan

for date, group in df.groupby("date"):

    weights = calculate_weights(group)

    df.loc[group.index, "portfolio_weight"] = weights.values


# --------------------------------------------------
# PORTFOLIO RETURNS
# --------------------------------------------------

df["weighted_return"] = (
    df["portfolio_weight"]
    * df["return"]
)

portfolio = (
    df.groupby("date")
    .agg(
        portfolio_return=("weighted_return", "sum")
    )
    .reset_index()
)


# --------------------------------------------------
# TURNOVER
# --------------------------------------------------

# Create a complete date × ticker grid.
# This allows stocks missing on a particular day
# to correctly move from their previous weight to 0.

dates = sorted(df["date"].unique())
tickers = sorted(df["ticker"].unique())

full_index = pd.MultiIndex.from_product(
    [dates, tickers],
    names=["date", "ticker"]
)

weights = (
    df.set_index(["date", "ticker"])["portfolio_weight"]
    .reindex(full_index)
    .fillna(0.0)
    .reset_index()
)

weights = weights.sort_values(["ticker", "date"])

weights["previous_weight"] = (
    weights
    .groupby("ticker")["portfolio_weight"]
    .shift(1)
    .fillna(0.0)
)

weights["weight_change"] = (
    weights["portfolio_weight"]
    - weights["previous_weight"]
)

turnover = (
    weights
    .groupby("date")["weight_change"]
    .apply(lambda x: x.abs().sum())
    .reset_index(name="turnover")
)


# --------------------------------------------------
# INITIAL FORMATION
# --------------------------------------------------

first_date = turnover["date"].min()

turnover["initial_formation"] = (
    turnover["date"] == first_date
)

turnover["ongoing_turnover"] = (
    turnover["turnover"]
)

turnover.loc[
    turnover["initial_formation"],
    "ongoing_turnover"
] = 0.0


# --------------------------------------------------
# TRANSACTION COSTS
# --------------------------------------------------

portfolio = portfolio.merge(
    turnover,
    on="date",
    how="left"
)

portfolio["transaction_cost"] = (
    portfolio["turnover"]
    * TRANSACTION_COST
)

portfolio["ongoing_transaction_cost"] = (
    portfolio["ongoing_turnover"]
    * TRANSACTION_COST
)

portfolio["net_return"] = (
    portfolio["portfolio_return"]
    - portfolio["transaction_cost"]
)


# --------------------------------------------------
# CUMULATIVE PERFORMANCE
# --------------------------------------------------

portfolio["gross_cumulative"] = (
    1 + portfolio["portfolio_return"]
).cumprod()

portfolio["net_cumulative"] = (
    1 + portfolio["net_return"]
).cumprod()

portfolio["cumulative_return"] = (
    portfolio["net_cumulative"] - 1
)


# --------------------------------------------------
# PERFORMANCE METRICS
# --------------------------------------------------

returns = portfolio["net_return"]
gross_returns = portfolio["portfolio_return"]

total_return = (
    (1 + returns).prod() - 1
)

gross_total_return = (
    (1 + gross_returns).prod() - 1
)

volatility = (
    returns.std()
    * np.sqrt(252)
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
# VALIDATION
# --------------------------------------------------

daily_weight_sum = (
    df.groupby("date")["portfolio_weight"]
    .sum()
)

print("\n==============================")
print("SENTIMENT PORTFOLIO")
print("==============================")

print(
    f"Trading Days: {len(portfolio)}"
)

print(
    f"Average Stocks Per Day: "
    f"{df.groupby('date')['ticker'].nunique().mean():.2f}"
)

print(
    f"Gross Total Return: "
    f"{gross_total_return:.4f}"
)

print(
    f"Net Total Return: "
    f"{total_return:.4f}"
)

print(
    f"Annualized Volatility: "
    f"{volatility:.4f}"
)

print(
    f"Sharpe Ratio: "
    f"{sharpe:.4f}"
)

print(
    f"Maximum Drawdown: "
    f"{max_drawdown:.4f}"
)


print("\n==============================")
print("TURNOVER ANALYSIS")
print("==============================")

print(
    f"Transaction cost rate: "
    f"{TRANSACTION_COST:.4%}"
)

print(
    f"Initial formation turnover: "
    f"{turnover.loc[turnover['initial_formation'], 'turnover'].iloc[0]:.4f}"
)

print(
    f"Average ongoing turnover: "
    f"{turnover['ongoing_turnover'].mean():.4f}"
)

print(
    f"Total turnover: "
    f"{turnover['turnover'].sum():.4f}"
)

print(
    f"Total transaction costs: "
    f"{portfolio['transaction_cost'].sum():.4f}"
)


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

print(
    f"Minimum daily weight sum: "
    f"{daily_weight_sum.min():.4f}"
)

print(
    f"Maximum daily weight sum: "
    f"{daily_weight_sum.max():.4f}"
)


print("\n==============================")
print("STOCKS PER DAY")
print("==============================")

print(
    df.groupby("date")["ticker"]
    .nunique()
    .to_string()
)


# --------------------------------------------------
# SAVE RESULTS
# --------------------------------------------------

df.to_csv(
    OUTPUT_FILE,
    index=False
)

portfolio.to_csv(
    RESULTS_FILE,
    index=False
)

print(
    f"\nSaved portfolio weights to "
    f"{OUTPUT_FILE}"
)

print(
    f"Saved portfolio results to "
    f"{RESULTS_FILE}"
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

print("\nSample turnover:")

print(
    portfolio[
        [
            "date",
            "turnover",
            "ongoing_turnover",
            "transaction_cost",
            "net_return"
        ]
    ].head(10)
)