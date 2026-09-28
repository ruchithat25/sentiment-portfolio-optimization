import os
from dotenv import load_dotenv

load_dotenv()


# Stock tickers
TICKERS = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS"
]


# Company names used for NewsAPI searches
TICKER_TO_NAME = {
    "RELIANCE.NS": "Reliance Industries",
    "TCS.NS": "Tata Consultancy Services",
    "INFY.NS": "Infosys",
    "HDFCBANK.NS": "HDFC Bank",
    "ICICIBANK.NS": "ICICI Bank"
}


# Historical price data
START_DATE = "2024-01-01"
END_DATE = "2026-09-28"


# NewsAPI key
NEWS_API_KEY = os.getenv("NEWS_API_KEY")


# Number of news articles to fetch per request
NEWS_PAGE_SIZE = 100