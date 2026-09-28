import pandas as pd
import numpy as np

INPUT_FILE = "data/strategy_dataset.csv"
OUTPUT_FILE = "data/signal_threshold_analysis.csv"

THRESHOLDS = [
    0.00,
    0.25,
    0.50
]

MIN_WEIGHT = 0.05
MAX_WEIGHT = 0.40
TRANSACTION_COST = 0.001


df = pd.read_csv(INPUT_FILE)
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values(["date", "ticker"]).copy()


def calculate_weights(group, threshold):

    group = group.copy()

    sentiment = group["lagged_sentiment"].to_numpy(dtype=float)

    # Treat weak sentiment as neutral
    adjusted_sentiment = np.where(
        np.abs(sentiment) >= threshold,
        sentiment,
        0.0
    )

    n = len(group)

    weights = np.full(n, MIN_WEIGHT)

    remaining = 1.0 - weights.sum()

    scores = (
        adjusted_sentiment
        - adjusted_sentiment.min()
        + 0.1
    )

    if scores.sum() == 0:
        scores = np.ones(n)

    scores = scores / scores.sum()

    weights += remaining * scores

    while np.any(weights > MAX_WEIGHT + 1e-12):

        excess = np.maximum(
            weights - MAX_WEIGHT,
            0
        ).sum()

        weights = np.minimum(
            weights,
            MAX_WEIGHT
        )

        available = (
            weights < MAX_WEIGHT - 1e-12
        )

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

    return weights


results = []


for threshold in THRESHOLDS:

    working = df.copy()

    working["portfolio_weight"] = np.nan

    # -----------------------------
    # Calculate daily weights
    # -----------------------------

    for date, group in working.groupby("date"):

        weights = calculate_weights(
            group,
            threshold
        )

        working.loc[
            group.index,
            "portfolio_weight"
        ] = weights

    # -----------------------------
    # Portfolio returns
    # -----------------------------

    working["weighted_return"] = (
        working["portfolio_weight"]
        * working["return"]
    )

    portfolio = (
        working.groupby("date")
        .agg(
            gross_return=(
                "weighted_return",
                "sum"
            )
        )
        .reset_index()
    )

    # -----------------------------
    # Turnover
    # -----------------------------

    dates = sorted(
        working["date"].unique()
    )

    tickers = sorted(
        working["ticker"].unique()
    )

    full_index = pd.MultiIndex.from_product(
        [dates, tickers],
        names=["date", "ticker"]
    )

    weights = (
        working
        .set_index(["date", "ticker"])
        ["portfolio_weight"]
        .reindex(full_index)
        .fillna(0.0)
        .reset_index()
    )

    weights = weights.sort_values(
        ["ticker", "date"]
    )

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
        weights.groupby("date")["weight_change"]
        .apply(lambda x: x.abs().sum())
        .reset_index(name="turnover")
    )

    portfolio = portfolio.merge(
        turnover,
        on="date",
        how="left"
    )

    # -----------------------------
    # Transaction costs
    # -----------------------------

    portfolio["transaction_cost"] = (
        portfolio["turnover"]
        * TRANSACTION_COST
    )

    portfolio["net_return"] = (
        portfolio["gross_return"]
        - portfolio["transaction_cost"]
    )

    # -----------------------------
    # Performance metrics
    # -----------------------------

    returns = portfolio["net_return"]

    total_return = (
        (1 + returns).prod() - 1
    )

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

    running_max = wealth.cummax()

    drawdown = (
        wealth / running_max
    ) - 1

    max_drawdown = drawdown.min()

    # -----------------------------
    # Signal statistics
    # -----------------------------

    neutral_fraction = (
        np.abs(
            working["lagged_sentiment"]
        ) < threshold
    ).mean()

    results.append({
        "threshold": threshold,
        "trading_days": len(portfolio),
        "neutral_signal_fraction": neutral_fraction,
        "total_return": total_return,
        "annualized_volatility": volatility,
        "sharpe_ratio": sharpe,
        "maximum_drawdown": max_drawdown,
        "average_turnover": portfolio["turnover"].mean(),
        "total_transaction_cost": portfolio[
            "transaction_cost"
        ].sum()
    })


results_df = pd.DataFrame(results)


print("\n==============================")
print("SIGNAL THRESHOLD ANALYSIS")
print("==============================")

print(
    results_df.to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}"
    )
)


results_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print(
    f"\nSaved threshold analysis to "
    f"{OUTPUT_FILE}"
)