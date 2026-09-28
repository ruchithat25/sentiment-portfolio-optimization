# Sentiment-Driven Portfolio Optimization

A quantitative finance project that investigates whether financial-news sentiment can be incorporated into a constrained portfolio allocation strategy for major Indian equities.

## Project Overview

This project combines:

* Financial market data
* Financial-news headlines
* FinBERT sentiment analysis
* Lagged sentiment signals
* Portfolio optimization
* Benchmark comparison
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

Only dates where all five stocks have valid observations are used for the constrained portfolio calculation.

This avoids infeasible allocations caused by having too few securities available on a particular date.

---

## Benchmark

The sentiment-weighted portfolio is compared with an equal-weight portfolio.

The equal-weight benchmark assigns:

```text
1 / 5 = 20%
```

to each stock.

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

---

## Current Results

The current portfolio comparison contains:

**12 complete trading days**

| Metric                | Equal Weight | Sentiment Weighted |
| --------------------- | -----------: | -----------------: |
| Trading Days          |           12 |                 12 |
| Total Return          |       -4.10% |             -5.14% |
| Annualized Volatility |       12.05% |             12.70% |
| Sharpe Ratio          |        -7.23 |              -8.64 |
| Maximum Drawdown      |       -2.78% |             -3.96% |
| Final Portfolio Value |       0.9590 |             0.9486 |

For this particular test window, the sentiment-weighted portfolio had lower cumulative performance and higher volatility and drawdown than the equal-weight benchmark.

However, the sample is too small to determine whether this difference represents a persistent characteristic of the strategy.

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

### Small Backtest Sample

Only 12 complete portfolio dates are currently available.

This makes performance metrics, particularly annualized statistics, highly unstable.

### Sentiment Carry-Forward Assumption

Sentiment can be carried forward for up to three trading days.

This is a modeling assumption rather than a proven market relationship.

### News Coverage Bias

The project relies on a single news provider and therefore does not capture every article published about each company.

### Simple Portfolio Allocation

The current allocation method uses sentiment-based scores subject to fixed portfolio constraints. It does not yet incorporate transaction costs, turnover, liquidity, factor exposures, or a formal convex optimization objective.

### No Transaction Costs

Trading costs, bid-ask spreads, taxes, and market impact are not currently modeled.

### No Statistical Significance Testing

The current sample is insufficient for robust hypothesis testing.

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
Benchmark
  ↓
Risk Analysis
```

A longer historical news dataset would be required before making stronger conclusions about predictive performance.

---

## Future Improvements

Potential extensions include:

1. Expand the historical news dataset.
2. Increase the number of stocks in the universe.
3. Add transaction costs.
4. Measure portfolio turnover.
5. Compare multiple sentiment models.
6. Test different sentiment aggregation methods.
7. Compare different signal horizons.
8. Perform walk-forward backtesting.
9. Add statistical significance tests.
10. Compare against additional portfolio strategies.
11. Introduce factor controls such as momentum and volatility.
12. Test alternative portfolio optimization objectives.

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
│   └── portfolio_comparison.png
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
