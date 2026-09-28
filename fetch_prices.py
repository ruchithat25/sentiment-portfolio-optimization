"""
Week 1, part 1: pull daily OHLCV price history for each ticker and save
one tidy CSV (long format — one row per ticker per day).

Run: python fetch_prices.py
"""

import pandas as pd
import yfinance as yf

from config import END_DATE, START_DATE, TICKERS


def fetch_prices(tickers, start, end):
    """Download daily price history for a list of tickers.

    Returns a single long-format dataframe with columns:
    date, ticker, open, high, low, close, volume
    """
    all_data = []
    for ticker in tickers:
        print(f"Fetching prices for {ticker}...")
        df = yf.download(ticker, start=start, end=end, progress=False)
        if df.empty:
            print(f"  Warning: no data returned for {ticker} — check the symbol")
            continue
        # yfinance can return either flat or multi-index columns depending
        # on version, so normalize before selecting.
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0] for c in df.columns]
        df = df.reset_index()
        df["ticker"] = ticker
        all_data.append(df[["Date", "ticker", "Open", "High", "Low", "Close", "Volume"]])

    if not all_data:
        raise RuntimeError("No price data fetched for any ticker — check your tickers and connection")

    combined = pd.concat(all_data, ignore_index=True)
    combined.columns = ["date", "ticker", "open", "high", "low", "close", "volume"]
    return combined


if __name__ == "__main__":
    prices = fetch_prices(TICKERS, START_DATE, END_DATE)
    prices.to_csv("data/prices.csv", index=False)
    print(f"\nSaved {len(prices)} rows to data/prices.csv")
    print(prices.head())
