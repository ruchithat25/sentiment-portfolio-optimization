import pandas as pd
import numpy as np

INPUT_FILE = "data/optimized_portfolio.csv"
OUTPUT_FILE = "data/transaction_cost_sensitivity.csv"

TRANSACTION_COSTS = [
    0.0000,
    0.0005,
    0.0010,
    0.0020
]


# --------------------------------------------------
# Load data
# --------------------------------------------------

df = pd.read_csv(INPUT_FILE)

df["date"] = pd.to_datetime(df["date"])

df = df.sort_values(
    ["date", "ticker"]
)


# --------------------------------------------------
# Calculate sentiment portfolio returns
# --------------------------------------------------

df["weighted_return"] = (
    df["portfolio_weight"]
    * df["return"]
)


portfolio = (
    df.groupby("date")
    .agg(
        gross_return=(
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

# Initial portfolio formation
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


portfolio = portfolio.merge(
    turnover,
    on="date",
    how="left"
)


# --------------------------------------------------
# Test different transaction costs
# --------------------------------------------------

results = []


for cost in TRANSACTION_COSTS:

    portfolio["transaction_cost"] = (
        portfolio["turnover"]
        * cost
    )

    portfolio["net_return"] = (
        portfolio["gross_return"]
        - portfolio["transaction_cost"]
    )

    returns = (
        portfolio["net_return"]
    )

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

    total_transaction_cost = (
        portfolio["transaction_cost"]
        .sum()
    )

    results.append({
        "transaction_cost": cost,
        "total_return": total_return,
        "annualized_volatility": volatility,
        "sharpe_ratio": sharpe,
        "maximum_drawdown": max_drawdown,
        "total_transaction_cost": total_transaction_cost
    })


results_df = pd.DataFrame(
    results
)


# --------------------------------------------------
# Print results
# --------------------------------------------------

print(
    "\n=============================="
)

print(
    "TRANSACTION COST SENSITIVITY"
)

print(
    "=============================="
)

print(
    results_df.to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}"
    )
)


# --------------------------------------------------
# Save results
# --------------------------------------------------

results_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print(
    f"\nSaved sensitivity analysis to "
    f"{OUTPUT_FILE}"
)