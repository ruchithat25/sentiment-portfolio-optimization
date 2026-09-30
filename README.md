# Sentiment-Driven Portfolio Optimization

A quantitative research project that studies whether **financial news sentiment can be used as a signal for portfolio construction**.

The project combines financial market data, financial-news sentiment analysis using **FinBERT**, lagged sentiment signals, portfolio construction, transaction-cost modeling, benchmark comparison, and robustness analysis.

---

## Project Overview

The objective of this project is to investigate whether sentiment extracted from financial news can provide useful information for constructing a stock portfolio.

The research pipeline follows these steps:

1. Collect historical stock-price data.
2. Collect company-specific financial news headlines.
3. Clean and preprocess the news data.
4. Apply FinBERT to classify financial sentiment.
5. Aggregate headline sentiment into daily sentiment scores.
6. Carry sentiment information forward for a limited number of trading days.
7. Lag the sentiment signal to avoid using same-day information.
8. Convert the sentiment signal into portfolio weights.
9. Backtest the resulting portfolio.
10. Compare it with an equal-weight benchmark.
11. Incorporate transaction costs.
12. Test sensitivity to different transaction-cost assumptions.
13. Test sentiment-signal thresholds.
14. Generate research visualizations.

---

## Research Question

> **Does financial-news sentiment provide useful information for constructing a portfolio of large Indian equities?**

The project evaluates this question using five Indian stocks:

* Reliance Industries
* Tata Consultancy Services (TCS)
* Infosys
* HDFC Bank
* ICICI Bank

The analysis uses NSE ticker symbols through Yahoo Finance.

---

## Data

### Price Data

Stock-price data is collected using `yfinance`.

The current price dataset covers:

**January 2024 – September 2026**

The stocks included are:

| Company             | Ticker         |
| ------------------- | -------------- |
| Reliance Industries | `RELIANCE.NS`  |
| TCS                 | `TCS.NS`       |
| Infosys             | `INFY.NS`      |
| HDFC Bank           | `HDFCBANK.NS`  |
| ICICI Bank          | `ICICIBANK.NS` |

### News Data

Financial news headlines are collected using **NewsAPI**.

Due to the historical-access limitations of the current NewsAPI developer plan, the usable news sample begins on:

**August 28, 2026**

The current dataset contains approximately **338 cleaned headlines** across the five companies.

Because the available historical news window is short, the portfolio evaluation period is also limited.

---

## Sentiment Analysis

The project uses:

**ProsusAI/FinBERT**

FinBERT is a transformer-based model designed specifically for financial sentiment classification.

Each headline is classified into:

* Positive
* Negative
* Neutral

A numerical sentiment score is calculated as:

```text
Sentiment Score = Positive Probability − Negative Probability
```

Therefore:

* Positive values indicate relatively positive sentiment.
* Negative values indicate relatively negative sentiment.
* Values near zero indicate weaker directional sentiment.

---

## Signal Construction

Daily sentiment is calculated by averaging the sentiment scores of the available headlines for each stock and trading date.

To reduce the possibility of using information that would not have been available at the time of the investment decision, the strategy uses **lagged sentiment**.

The signal used for portfolio construction is:

```text
Lagged Sentiment(t) = Sentiment(t − 1)
```

A limited **3-trading-day carry-forward** is also used when sentiment is temporarily unavailable.

The dataset keeps a `sentiment_available` flag to distinguish directly observed sentiment from carried-forward values.

---

## Portfolio Construction

The portfolio assigns weights according to lagged sentiment.

The current portfolio constraints are:

```text
Minimum Weight = 5%
Maximum Weight = 40%
Transaction Cost = 0.10%
```

Stocks with stronger relative sentiment receive larger portfolio weights.

The portfolio is long-only and the weights sum to:

```text
100%
```

The strategy also handles days where only a subset of the five stocks has usable sentiment information.

---

## Benchmark

The sentiment-weighted portfolio is compared against an:

**Equal-Weight Portfolio**

The benchmark assigns equal weights to all stocks available on each trading day.

Both portfolios are evaluated using the same transaction-cost assumption.

---

## Performance Metrics

The backtest evaluates:

* Total Return
* Annualized Volatility
* Sharpe Ratio
* Maximum Drawdown
* Portfolio Turnover
* Transaction Costs
* Final Portfolio Value

---

## Current Results

The current backtest contains:

**20 trading days**

The available universe varies during the sample, with an average of approximately:

**4.30 stocks per day**

### Portfolio Comparison

| Metric                   | Equal-Weight | Sentiment-Weighted |
| ------------------------ | -----------: | -----------------: |
| Total Return             |       -6.48% |             -8.99% |
| Annualized Volatility    |       10.56% |             14.40% |
| Sharpe Ratio             |        -7.93 |              -8.15 |
| Maximum Drawdown         |       -7.12% |            -10.62% |
| Final Portfolio Value    |       0.9352 |             0.9101 |
| Average Ongoing Turnover |        2.00% |             37.10% |
| Transaction Costs        |        0.10% |              0.84% |

These results describe the current sample only. The short evaluation period means they should not be interpreted as evidence of long-term strategy performance.

---

## Transaction-Cost Sensitivity

The strategy was evaluated under several transaction-cost assumptions.

| Transaction Cost | Total Return | Volatility | Sharpe Ratio | Max Drawdown |
| ---------------: | -----------: | ---------: | -----------: | -----------: |
|            0.00% |       -8.21% |     14.40% |        -7.42 |      -10.02% |
|            0.05% |       -8.60% |     14.40% |        -7.79 |      -10.32% |
|            0.10% |       -8.99% |     14.40% |        -8.15 |      -10.62% |
|            0.20% |       -9.75% |     14.41% |        -8.88 |      -11.23% |

The sensitivity analysis shows how increasing assumed trading costs affects the simulated portfolio results.

---

## Signal Threshold Robustness

An additional robustness test examines whether ignoring weak sentiment signals changes the portfolio characteristics.

Thresholds tested:

```text
0.00
0.25
0.50
```

Current results:

| Threshold | Neutral Signal Fraction | Total Return | Volatility | Sharpe | Max Drawdown | Avg. Turnover |
| --------: | ----------------------: | -----------: | ---------: | -----: | -----------: | ------------: |
|      0.00 |                   0.00% |       -9.00% |     14.39% |  -8.17 |      -10.62% |        42.66% |
|      0.25 |                  50.00% |       -8.51% |     13.81% |  -8.03 |      -10.17% |        40.43% |
|      0.50 |                  81.40% |       -7.51% |     12.63% |  -7.72 |       -8.83% |        30.23% |

In this specific sample, higher sentiment thresholds reduce portfolio turnover, volatility, and drawdown.

However, this is an **exploratory robustness analysis**, not evidence that a 0.50 threshold is optimal. Selecting a threshold based on the same sample can introduce overfitting.

---

## Research Visualizations

The project generates two visual research outputs:

### Portfolio Performance

`data/portfolio_performance.png`

This compares the cumulative performance of:

* Equal-Weight Portfolio
* Sentiment-Weighted Portfolio

### Sentiment Threshold Robustness

`data/threshold_robustness.png`

This visualizes how different sentiment thresholds affect simulated portfolio returns.

The charts are generated using:

```bash
python research_visualizations.py
```

---

## Key Research Observations

The current experiment provides several useful observations:

### 1. Sentiment signals can produce materially different portfolio weights

The sentiment strategy does not simply hold equal positions. Stronger relative sentiment leads to larger portfolio allocations.

### 2. The strategy has higher turnover

The sentiment portfolio has substantially higher ongoing turnover than the equal-weight benchmark.

This is important because a signal-driven strategy must be evaluated after realistic trading costs.

### 3. Transaction costs matter

The transaction-cost sensitivity analysis shows that increasing trading costs reduces simulated portfolio performance.

### 4. Signal thresholds affect portfolio behavior

Ignoring weaker sentiment signals reduces the amount of trading and portfolio volatility in this sample.

### 5. The current sample is too short for strong conclusions

The current backtest covers only 20 trading days. Therefore, the results should be treated as an initial research experiment rather than a statistically reliable estimate of long-term performance.

---

## Limitations

This project currently has several important limitations.

### Short News History

The available NewsAPI historical window limits the amount of usable news data.

### Short Backtest

The current evaluation period contains only 20 trading days.

### News Coverage Bias

NewsAPI may not capture every relevant article about each company. Media coverage can also differ significantly across companies.

### Variable Investment Universe

Not every stock has usable sentiment on every date, resulting in a changing number of investable stocks.

### Carry-Forward Assumption

Missing sentiment values can be carried forward for up to three trading days. This is a modeling assumption and may not accurately represent how information persists in real markets.

### Simple Portfolio Allocation

The current allocation mechanism uses sentiment scores with minimum and maximum weight constraints rather than a full mathematical portfolio optimization framework.

### Transaction-Cost Assumption

The current analysis uses a simplified transaction-cost assumption of 0.10%.

Actual trading costs can include:

* Brokerage
* Bid-ask spread
* Taxes
* Slippage
* Market impact

### No Statistical Significance Testing

The current analysis does not establish whether the observed relationships are statistically significant.

### Potential Overfitting

Threshold analysis and portfolio parameters can become overfit if they are selected based on the same historical sample used for evaluation.

---

## Future Improvements

Several extensions can make the research more rigorous.

### Data Improvements

* Obtain a longer historical news dataset.
* Increase the number of stocks.
* Include additional sectors.
* Combine multiple news sources.
* Remove duplicate or near-duplicate news more aggressively.

### Sentiment Improvements

* Compare FinBERT with other financial sentiment models.
* Test different sentiment aggregation methods.
* Weight headlines by source quality.
* Weight sentiment by headline importance.
* Study sentiment decay over time.
* Separate positive and negative news events.

### Quantitative Research Improvements

* Perform walk-forward backtesting.
* Use train/validation/test periods.
* Perform statistical significance testing.
* Calculate confidence intervals.
* Test different signal horizons.
* Analyze factor exposures.
* Compare against additional benchmarks.
* Test sector-neutral portfolios.
* Add volatility targeting.
* Compare alternative portfolio optimization methods.

### Portfolio Optimization

Future versions could test:

* Mean-variance optimization
* Risk parity
* Minimum variance
* Maximum Sharpe optimization
* Black-Litterman
* Volatility-scaled sentiment signals

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
├── signal_threshold_analysis.py
├── research_visualizations.py
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
│   ├── signal_threshold_analysis.csv
│   ├── portfolio_performance.png
│   ├── threshold_robustness.png
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

## Running the Project

Create and activate the virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure the required API key in a local `.env` file:

```text
NEWS_API_KEY=your_api_key
```

The `.env` file is excluded from Git using `.gitignore`.

Run the pipeline components individually:

```bash
python fetch_prices.py
python fetch_news.py
python clean_news.py
python sentiment.py
python aggregate_sentiment.py
python prepare_dataset.py
python lagged_signal.py
python portfolio_optimizer.py
python portfolio_comparison.py
python transaction_cost_sensitivity.py
python signal_threshold_analysis.py
python research_visualizations.py
python research_summary.py
```

---

## Disclaimer

This project is intended for educational and research purposes.

The results presented here are based on a limited dataset and should not be interpreted as investment advice or as evidence of a reliable trading strategy.
