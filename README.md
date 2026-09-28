# Week 1 — Price + Headline Pipeline

## Setup
```
pip install -r requirements.txt
```

## 1. Get prices (no API key needed)
```
python fetch_prices.py
```
Saves `data/prices.csv` — daily open/high/low/close/volume for each ticker
in `config.py`, from `START_DATE` to `END_DATE`.

## 2. Get headlines (needs a free NewsAPI key)
1. Get a free key: https://newsapi.org/register
2. Paste it into `NEWS_API_KEY` in `config.py`
3. Run:
```
python fetch_news.py
```
Saves `data/headlines.csv` — one row per headline, tagged with its ticker.

**Note:** NewsAPI's free tier only serves the last 30 days of articles, so
this pulls the last 30 days regardless of `START_DATE`/`END_DATE`. That's
enough to build and test the full pipeline. If you want longer headline
history later, GDELT is a free alternative that goes back years — worth
switching to once the rest of the pipeline (sentiment scoring, portfolio
weights) is working.

## Customize
Edit `TICKERS` and `TICKER_TO_NAME` in `config.py` to change your universe.
Keep tickers to well-covered large-caps for now — thin news coverage on
small-caps will make Week 2 (sentiment scoring) noisier than it needs to be.

## Next (Week 2)
Feed `data/headlines.csv` through FinBERT (`ProsusAI/finbert` on
HuggingFace) to get a sentiment score per headline, then aggregate to a
daily sentiment score per ticker.
