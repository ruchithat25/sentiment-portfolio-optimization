import pandas as pd
import numpy as np

INPUT_FILE = "data/strategy_dataset.csv"
OUTPUT_FILE = "data/optimized_portfolio.csv"
RESULTS_FILE = "data/portfolio_results.csv"

MIN_WEIGHT = 0.05
MAX_WEIGHT = 0.40

# Transaction cost assumption
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
# Keep only dates where all stocks are available
# --------------------------------------------------

all_tickers = sorted(
    df["ticker"].unique()
)

n_stocks = len(all_tickers)

valid_dates = (
    df.groupby("date")["ticker"]
    .nunique()
)

valid_dates = valid_dates[
    valid_dates == n_stocks
].index

df = df[
    df["date"].isin(valid_dates)
].copy()

print(
    f"Stocks in universe: {n_stocks}"
)

print(
    f"Valid portfolio dates: "
    f"{len(valid_dates)}"
)


# --------------------------------------------------
# Calculate constrained sentiment weights
# --------------------------------------------------

def calculate_weights(group):

    sentiment = group[
        "lagged_sentiment"
    ].to_numpy(dtype=float)

    n = len(sentiment)

    if n * MIN_WEIGHT > 1:
        raise ValueError(
            f"Cannot allocate {n} stocks "
            f"with minimum weight {MIN_WEIGHT:.2f}"
        )

    if n * MAX_WEIGHT < 1:
        raise ValueError(
            f"Cannot allocate {n} stocks "
            f"with maximum weight {MAX_WEIGHT:.2f}"
        )

    # Start every stock at minimum weight
    weights = np.full(
        n,
        MIN_WEIGHT
    )

    remaining = (
        1.0 - weights.sum()
    )

    # Convert sentiment into positive scores
    scores = (
        sentiment
        - sentiment.min()
        + 0.1
    )

    if scores.sum() == 0:
        scores = np.ones(n)

    scores = (
        scores / scores.sum()
    )

    # Allocate remaining weight
    # according to sentiment
    weights += (
        remaining * scores
    )

    # --------------------------------------------------
    # Enforce maximum weight
    # --------------------------------------------------

    while np.any(
        weights > MAX_WEIGHT + 1e-12
    ):

        excess = np.maximum(
            weights - MAX_WEIGHT,
            0
        ).sum()

        weights = np.minimum(
            weights,
            MAX_WEIGHT
        )

        available = (
            weights
            < MAX_WEIGHT - 1e-12
        )

        if not available.any():
            break

        available_scores = (
            scores.copy()
        )

        available_scores[
            ~available
        ] = 0

        if available_scores.sum() == 0:
            available_scores[
                available
            ] = 1

        weights += (
            excess
            * available_scores
            / available_scores.sum()
        )

    # --------------------------------------------------
    # Correct floating-point difference
    # --------------------------------------------------

    difference = (
        1.0 - weights.sum()
    )

    if abs(difference) > 1e-12:

        available = np.where(
            weights
            < MAX_WEIGHT - 1e-12
        )[0]

        if len(available) > 0:
            weights[
                available[0]
            ] += difference

    return pd.Series(
        weights,
        index=group.index
    )


# --------------------------------------------------
# Calculate weights for each date
# --------------------------------------------------

df["portfolio_weight"] = np.nan

for date, group in df.groupby("date"):

    weights = calculate_weights(
        group
    )

    df.loc[
        group.index,
        "portfolio_weight"
    ] = weights.values


# --------------------------------------------------
# Portfolio returns
# --------------------------------------------------

df["weighted_return"] = (
    df["portfolio_weight"]
    * df["return"]
)

portfolio = (
    df.groupby("date")
    .agg(
        portfolio_return=(
            "weighted_return",
            "sum"
        )
    )
    .reset_index()
)


# --------------------------------------------------
# Calculate turnover
# --------------------------------------------------

df["previous_weight"] = (
    df.groupby("ticker")[
        "portfolio_weight"
    ].shift(1)
)

df["weight_change"] = (
    df["portfolio_weight"]
    - df["previous_weight"]
)


# First portfolio formation:
# previous holdings are assumed to be zero.
df["weight_change"] = (
    df["weight_change"]
    .fillna(df["portfolio_weight"])
)


turnover = (
    df.groupby("date")[
        "weight_change"
    ]
    .apply(
        lambda x: x.abs().sum()
    )
    .reset_index(
        name="turnover"
    )
)


# --------------------------------------------------
# Identify initial vs ongoing turnover
# --------------------------------------------------

first_date = (
    portfolio["date"].min()
)

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
# Merge turnover into portfolio
# --------------------------------------------------

portfolio = portfolio.merge(
    turnover,
    on="date",
    how="left"
)


# --------------------------------------------------
# Transaction costs
# --------------------------------------------------

portfolio["transaction_cost"] = (
    portfolio["turnover"]
    * TRANSACTION_COST
)


portfolio["ongoing_transaction_cost"] = (
    portfolio["ongoing_turnover"]
    * TRANSACTION_COST
)


# --------------------------------------------------
# Net return
# --------------------------------------------------

portfolio["net_return"] = (
    portfolio["portfolio_return"]
    - portfolio["transaction_cost"]
)


# --------------------------------------------------
# Cumulative returns
# --------------------------------------------------

portfolio["gross_cumulative"] = (
    1 + portfolio["portfolio_return"]
).cumprod()


portfolio["net_cumulative"] = (
    1 + portfolio["net_return"]
).cumprod()


portfolio["cumulative_return"] = (
    portfolio["net_cumulative"]
    - 1
)


# --------------------------------------------------
# Performance metrics
# --------------------------------------------------

returns = (
    portfolio["net_return"]
)

gross_returns = (
    portfolio["portfolio_return"]
)


total_return = (
    1 + returns
).prod() - 1


gross_total_return = (
    1 + gross_returns
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


# --------------------------------------------------
# Results
# --------------------------------------------------

print(
    "\n=============================="
)

print(
    "SENTIMENT PORTFOLIO"
)

print(
    "=============================="
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


# --------------------------------------------------
# Turnover analysis
# --------------------------------------------------

print(
    "\n=============================="
)

print(
    "TURNOVER ANALYSIS"
)

print(
    "=============================="
)

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

print(
    f"Ongoing transaction costs: "
    f"{portfolio['ongoing_transaction_cost'].sum():.4f}"
)


# --------------------------------------------------
# Weight validation
# --------------------------------------------------

print(
    "\n=============================="
)

print(
    "WEIGHT VALIDATION"
)

print(
    "=============================="
)

print(
    f"Minimum weight observed: "
    f"{df['portfolio_weight'].min():.4f}"
)

print(
    f"Maximum weight observed: "
    f"{df['portfolio_weight'].max():.4f}"
)


daily_weight_sum = (
    df.groupby("date")[
        "portfolio_weight"
    ].sum()
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
# Save portfolio weights
# --------------------------------------------------

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# Save portfolio results
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


# --------------------------------------------------
# Sample weights
# --------------------------------------------------

print(
    "\nSample weights:"
)

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


# --------------------------------------------------
# Sample turnover
# --------------------------------------------------

print(
    "\nSample turnover:"
)

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