import pandas as pd

COMPARISON_FILE = "data/portfolio_comparison.csv"
SENSITIVITY_FILE = "data/transaction_cost_sensitivity.csv"

OUTPUT_FILE = "data/research_summary.csv"


# --------------------------------------------------
# Load results
# --------------------------------------------------

comparison = pd.read_csv(
    COMPARISON_FILE
)

sensitivity = pd.read_csv(
    SENSITIVITY_FILE
)


# --------------------------------------------------
# Extract final portfolio values
# --------------------------------------------------

equal_final_value = (
    comparison[
        "equal_weight_cumulative"
    ].iloc[-1]
)

sentiment_final_value = (
    comparison[
        "sentiment_cumulative"
    ].iloc[-1]
)


# --------------------------------------------------
# Extract total returns
# --------------------------------------------------

equal_return = (
    comparison[
        "equal_net_return"
    ]
    .add(1)
    .prod()
    - 1
)

sentiment_return = (
    comparison[
        "sentiment_net_return"
    ]
    .add(1)
    .prod()
    - 1
)


# --------------------------------------------------
# Create summary
# --------------------------------------------------

summary = pd.DataFrame({

    "metric": [
        "Trading Days",
        "Equal-Weight Total Return",
        "Sentiment-Weighted Total Return",
        "Equal-Weight Final Value",
        "Sentiment-Weighted Final Value",
        "Equal-Weight Average Turnover",
        "Sentiment Average Ongoing Turnover",
        "Equal-Weight Total Transaction Costs",
        "Sentiment Total Transaction Costs",
        "Gross Sentiment Return",
        "Sentiment Return at 0.05% Cost",
        "Sentiment Return at 0.10% Cost",
        "Sentiment Return at 0.20% Cost"
    ],

    "value": [

        len(comparison),

        equal_return,

        sentiment_return,

        equal_final_value,

        sentiment_final_value,

        comparison[
            "equal_ongoing_turnover"
        ].mean(),

        comparison[
            "sentiment_ongoing_turnover"
        ].mean(),

        comparison[
            "equal_transaction_cost"
        ].sum(),

        comparison[
            "sentiment_transaction_cost"
        ].sum(),

        sensitivity.loc[
            sensitivity[
                "transaction_cost"
            ] == 0,
            "total_return"
        ].iloc[0],

        sensitivity.loc[
            sensitivity[
                "transaction_cost"
            ] == 0.0005,
            "total_return"
        ].iloc[0],

        sensitivity.loc[
            sensitivity[
                "transaction_cost"
            ] == 0.001,
            "total_return"
        ].iloc[0],

        sensitivity.loc[
            sensitivity[
                "transaction_cost"
            ] == 0.002,
            "total_return"
        ].iloc[0]
    ]
})


# --------------------------------------------------
# Save
# --------------------------------------------------

summary.to_csv(
    OUTPUT_FILE,
    index=False
)


# --------------------------------------------------
# Print
# --------------------------------------------------

print(
    "\n=============================="
)

print(
    "RESEARCH SUMMARY"
)

print(
    "=============================="
)

print(
    summary.to_string(
        index=False
    )
)

print(
    f"\nSaved research summary to "
    f"{OUTPUT_FILE}"
)