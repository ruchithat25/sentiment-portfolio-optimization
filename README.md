# Sentiment-Driven Portfolio Optimization

A quantitative finance project that investigates whether financial-news sentiment can be incorporated into a constrained portfolio allocation strategy for major Indian equities.

---

## Project Overview

This project combines:

* Financial market data
* Financial-news headlines
* FinBERT sentiment analysis
* Lagged sentiment signals
* Portfolio optimization
* Benchmark comparison
* Transaction-cost analysis
* Risk and performance analysis

The objective is to investigate whether information extracted from financial news can be used as an input to portfolio construction.

This project is designed as a research experiment rather than a claim that sentiment-based investing consistently outperforms traditional portfolio construction.

---

## Research Question

> Can financial-news sentiment be transformed into a lagged trading signal and used to construct a portfolio that improves risk-adjusted performance relative to an equal-weight benchmark?

---

## Assets

The current portfolio universe contains five large Indian equities:

| Ticker       | Company    |
| ------------ | ---------- |
| RELIANCE.NS  | Reliance   |
| TCS.NS       | TCS        |
| INFY.NS      | Infosys    |
| HDFCBANK.NS  | HDFC Bank  |
| ICICIBANK.NS | ICICI Bank |

---

## Methodology

### 1. Market Data

Historical daily price data is collected using Yahoo Finance through `yfinance`.

The price dataset contains:

* Open
* High
* Low
* Close
* Volume
* Daily returns

The available price history begins in January 2024.

---

### 2. News Collection

Financial-news headlines are collected using NewsAPI.

News is associated with individual companies using company-specific searches.

The current NewsAPI developer account limits the historical news window, so the current research sample covers approximately:

**28 August 2026 – 27 September 2026**

The available sample therefore does not provide enough history for strong statistical conclusions.

---

### 3. News Cleaning

Duplicate headlines are removed based on ticker and headline.

The pipeline reduced the collected dataset from:

**358 headlines → 338 unique headlines**

---

### 4. Sentiment Analysis

Each headline is processed using **FinBERT**, a financial-domain language model.

For every headline, the model produces probabilities for:

* Positive
* Negative
* Neutral

A continuous sentiment score is calculated as:

```text
Sentiment Score = Positive Probability − Negative Probability
```

Therefore:

* Positive values indicate relatively positive sentiment.
* Negative values indicate relatively negative sentiment.
* Values close to zero indicate weaker directional sentiment.

---

### 5. Daily Sentiment Aggregation

Multiple headlines belonging to the same company and calendar day are aggregated.

For each ticker-date combination, the pipeline calculates:

* Mean sentiment score
* Number of headlines

The current dataset contains:

**96 daily sentiment observations**

---

### 6. Sentiment Alignment

News sentiment is aligned with daily stock returns.

Because news may continue to influence market expectations after publication, the project currently allows sentiment to be carried forward for up to **three trading days** when no new headline is available.

This is an explicit modeling assumption and should not be interpreted as established evidence.

A `sentiment_available` indicator is also retained to distinguish directly observed sentiment from carried-forward values.

---

### 7. Lagged Signal

To reduce look-ahead bias, the portfolio does not directly use the same day's sentiment to explain the same day's return.

Instead:

```text
Today's Signal = Previous Trading Day's Sentiment
```

This produces a lagged sentiment signal that is used for portfolio allocation.

The current sample contains **86 lagged observations**.

---

### 8. Portfolio Construction

Portfolio weights are determined using the lagged sentiment signal.

The portfolio is subject to:

```text
Minimum weight per stock = 5%

Maximum weight per stock = 40%

Total portfolio weight = 100%
```

The portfolio is re-optimized each trading day using the stocks for which valid lagged sentiment and return observations are available.

Therefore, the number of stocks in the active portfolio can vary across dates.

In the current sample:

* Average stocks per day: **4.30**
* Minimum stocks on a day: **3**
* Maximum stocks on a day: **5**
* Total portfolio dates: **20**

Stocks unavailable on a particular date are assigned a portfolio weight of 0% for turnover calculation.

---

### 9. Transaction Costs

A transaction-cost assumption of **0.10% per unit of turnover** is applied to the portfolio.

Turnover is calculated from changes in portfolio weights between trading days.

The analysis distinguishes between:

* Initial portfolio formation turnover
* Ongoing turnover

This allows the research to examine how portfolio trading activity affects net performance.

---

## Benchmark

The sentiment-weighted portfolio is compared with an equal-weight portfolio.

The benchmark allocates the available portfolio capital equally across the stocks available on each trading day.

For example, when five stocks are available:

```text
1 / 5 = 20%
```

When fewer stocks are available, the capital is distributed equally across the available stocks.

This provides a simple benchmark for evaluating whether the sentiment-based allocation produces different portfolio characteristics.

---

## Performance Metrics

The project evaluates:

### Total Return

Measures the cumulative portfolio performance over the test period.

### Annualized Volatility

Measures the annualized variability of portfolio returns.

### Sharpe Ratio

Measures return relative to volatility.

Because the current test contains only a small number of observations, the annualized Sharpe ratio should be interpreted cautiously.

### Maximum Drawdown

Measures the largest decline from a previous portfolio peak.

### Turnover

Measures the amount of portfolio weight that changes between trading periods.

### Transaction Costs

Measures the estimated performance impact of the assumed trading-cost rate.

---

## Current Results

The current portfolio comparison contains:

**20 trading days**

| Metric                | Equal Weight | Sentiment Weighted |
| --------------------- | -----------: | -----------------: |
| Trading Days          |           20 |                 20 |
| Total Return          |       -6.48% |             -8.99% |
| Annualized Volatility |       10.56% |             14.40% |
| Sharpe Ratio          |        -7.93 |              -8.15 |
| Maximum Drawdown      |       -7.12% |            -10.62% |
| Final Portfolio Value |       0.9352 |             0.9101 |

For this particular test window, the sentiment-weighted portfolio had lower cumulative performance and higher volatility and drawdown than the equal-weight benchmark.

The sentiment-weighted portfolio also had higher ongoing turnover:

* Equal-weight average ongoing turnover: **2.00%**
* Sentiment-weighted average ongoing turnover: **37.10%**

Estimated total transaction costs were:

* Equal-weight: **0.10%**
* Sentiment-weighted: **0.84%**

These results describe this specific sample and should not be interpreted as evidence of persistent future performance.

---

## Transaction-Cost Sensitivity

The project evaluates how different transaction-cost assumptions affect the sentiment-weighted portfolio.

| Transaction Cost | Total Return | Annualized Volatility | Sharpe Ratio | Maximum Drawdown |
| ---------------- | -----------: | --------------------: | -----------: | ---------------: |
| 0.00%            |       -8.21% |                14.40% |        -7.42 |          -10.02% |
| 0.05%            |       -8.60% |                14.40% |        -7.79 |          -10.32% |
| 0.10%            |       -8.99% |                14.40% |        -8.15 |          -10.62% |
| 0.20%            |       -9.75% |                14.41% |        -8.88 |          -11.23% |

The sensitivity analysis shows how increasing assumed trading costs affects net portfolio performance.

The assumed **0.10% transaction cost is a modeling assumption**, not an estimate derived from observed bid-ask spreads, taxes, or market impact.

---

## Correlation Analysis

The relationship between lagged sentiment and next-day returns is also examined.

Current ticker-level correlations are:

| Ticker     | Lagged Sentiment Correlation |
| ---------- | ---------------------------: |
| HDFC Bank  |                       0.2951 |
| ICICI Bank |                      -0.3771 |
| Infosys    |                       0.0146 |
| Reliance   |                      -0.4009 |
| TCS        |                      -0.3220 |

Overall lagged correlation:

```text
-0.0767
```

These correlations are descriptive statistics from a small sample and should not be interpreted as evidence of a stable predictive relationship.

---

## Limitations

The current implementation has several important limitations.

### Limited News History

The NewsAPI developer account restricts the historical period available to the project.

The current news sample covers approximately one month.

### Small Backtest Sample

The current portfolio backtest contains only **20 trading days**.

Although this is an improvement over the previous complete-universe approach, the sample remains too short for strong statistical conclusions.

Annualized performance metrics should therefore be interpreted cautiously.

### Variable Portfolio Universe

Not every stock has valid sentiment information on every trading day.

The current implementation handles this by optimizing across the available stocks rather than discarding the entire date.

This introduces variation in the number of securities held by the portfolio.

### Sentiment Carry-Forward Assumption

Sentiment can be carried forward for up to three trading days.

This is a modeling assumption rather than a proven market relationship.

### News Coverage Bias

The project relies on a single news provider and therefore does not capture every article published about each company.

### Simple Portfolio Allocation

The current allocation method uses sentiment-based scores subject to fixed portfolio constraints.

It does not yet incorporate a formal risk-optimization objective, factor exposures, liquidity constraints, or volatility targeting.

### Transaction-Cost Assumption

The project models transaction costs using a fixed 0.10% rate.

Actual trading costs can vary depending on spreads, brokerage, taxes, liquidity, and market impact.

### No Statistical Significance Testing

The current sample is insufficient for robust hypothesis testing.

### Short Evaluation Window

The current results cover only a short period from late August through September 2026.

The results should therefore be treated as an initial research experiment rather than evidence of a persistent investment effect.

---

## Research Interpretation

The current results should be viewed as an **initial research experiment** rather than evidence that sentiment investing works or does not work.

The primary achievement of the project is the construction of an end-to-end pipeline:

```text
News
  ↓
Cleaning
  ↓
FinBERT
  ↓
Daily Sentiment
  ↓
Lagged Signal
  ↓
Portfolio Construction
  ↓
Transaction Costs
  ↓
Benchmark
  ↓
Risk Analysis
  ↓
Sensitivity Analysis
```

The current sample does not provide enough historical data to determine whether the observed performance differences would persist over longer periods.

A longer historical news dataset would be required before making stronger conclusions about predictive performance.

---

## Future Improvements

Potential extensions include:

1. Expand the historical news dataset.
2. Increase the number of stocks in the universe.
3. Compare multiple sentiment models.
4. Test different sentiment aggregation methods.
5. Compare different signal horizons.
6. Perform walk-forward backtesting over a longer historical period.
7. Add statistical significance tests.
8. Compare against additional portfolio strategies.
9. Introduce factor controls such as momentum and volatility.
10. Test alternative portfolio optimization objectives.
11. Add volatility targeting and risk constraints.
12. Investigate sector-neutral portfolio construction.
13. Improve news coverage using multiple data sources.
14. Calibrate transaction costs using market liquidity and bid-ask spread information.

---

## Project Structure

```text
finance/
│
├── config.py
├── fetch_news.py
├── fetch_prices.py
├── clean_news.py
├── sentiment.py
├── aggregate_sentiment.py
├── prepare_dataset.py
├── analyze_sentiment.py
├── lagged_signal.py
├── portfolio_backtest.py
├── portfolio_optimizer.py
├── portfolio_comparison.py
├── transaction_cost_sensitivity.py
├── research_summary.py
│
├── data/
│   ├── prices.csv
│   ├── headlines.csv
│   ├── headlines_clean.csv
│   ├── sentiment_scores.csv
│   ├── daily_sentiment.csv
│   ├── modeling_dataset.csv
│   ├── strategy_dataset.csv
│   ├── portfolio_results.csv
│   ├── optimized_portfolio.csv
│   ├── portfolio_comparison.csv
│   ├── portfolio_comparison.png
│   ├── transaction_cost_sensitivity.csv
│   └── research_summary.csv
│
├── requirements.txt
└── README.md
```

---

## Technologies

* Python
* Pandas
* NumPy
* yfinance
* NewsAPI
* PyTorch
* Hugging Face Transformers
* FinBERT
* Matplotlib
* Git
* GitHub

---

## Disclaimer

This project is intended for educational and research purposes.

The results presented here are based on a limited dataset and should not be interpreted as investment advice or as evidence of a reliable trading strategy.
