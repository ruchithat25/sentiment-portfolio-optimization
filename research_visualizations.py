import pandas as pd
import matplotlib.pyplot as plt

COMPARISON_FILE = "data/portfolio_comparison.csv"
THRESHOLD_FILE = "data/signal_threshold_analysis.csv"

PERFORMANCE_CHART = "data/portfolio_performance.png"
THRESHOLD_CHART = "data/threshold_robustness.png"


# ==================================================
# 1. PORTFOLIO PERFORMANCE
# ==================================================

comparison = pd.read_csv(COMPARISON_FILE)
comparison["date"] = pd.to_datetime(comparison["date"])

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

plt.title("Portfolio Performance Comparison")
plt.xlabel("Date")
plt.ylabel("Portfolio Value")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig(
    PERFORMANCE_CHART,
    dpi=200
)

plt.close()


# ==================================================
# 2. SENTIMENT THRESHOLD ROBUSTNESS
# ==================================================

threshold = pd.read_csv(THRESHOLD_FILE)

plt.figure(figsize=(10, 6))

plt.plot(
    threshold["threshold"],
    threshold["total_return"] * 100,
    marker="o"
)

plt.title("Sentiment Threshold Robustness")
plt.xlabel("Sentiment Threshold")
plt.ylabel("Total Return (%)")
plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig(
    THRESHOLD_CHART,
    dpi=200
)

plt.close()


print("\n==============================")
print("RESEARCH VISUALIZATIONS")
print("==============================")

print(
    f"Saved performance chart to "
    f"{PERFORMANCE_CHART}"
)

print(
    f"Saved threshold chart to "
    f"{THRESHOLD_CHART}"
)