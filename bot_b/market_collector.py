"""
JARVIS BOT B — MARKET DATA COLLECTOR (OPTIMIZED)
Collects live stock, crypto, and news data asynchronously.
"""

import sys
sys.path.append("C:/jarvis/config")

import yfinance as yf
import requests
import redis
import json
import chromadb
import asyncio
import pandas as pd
from datetime import datetime
from api_keys import NEWS_API_KEY, REDIS_HOST, REDIS_PORT

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
chroma_client = chromadb.HttpClient(host="localhost", port=8000)
brain = chroma_client.get_or_create_collection("jarvis_brain")

# WATCHLIST: Added 'crypto' to ensure assets are properly aggregated
WATCHLIST = {
    "indices": ["^GSPC", "^DJI", "^NSEI", "^N225"],
    "stocks": ["AAPL", "MSFT", "GOOGL", "NVDA", "META", "RELIANCE.NS"],
    "commodities": ["GC=F", "CL=F"],
    "crypto": ["BTC-USD"]
}

def get_sp500_tickers() -> list:
    try:
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        headers = {'User-Agent': 'Mozilla/5.0'}
        df = pd.read_html(requests.get(url, headers=headers).text)[0]
        tickers = df['Symbol'].str.replace('.', '-', regex=False).tolist()
        return tickers[:20] 
    except Exception as e:
        print(f"S&P 500 fetch failed: {e}")
        return ["AAPL", "MSFT", "NVDA"]

async def fetch_ticker_batch_async(tickers: list) -> dict:
    loop = asyncio.get_event_loop()
    try:
        data = await loop.run_in_executor(
            None, 
            lambda: yf.download(tickers=tickers, period="1d", interval="5m", 
                               group_by="ticker", auto_adjust=True, progress=False, threads=True)
        )
        return data
    except Exception as e:
        print(f"Batch download error: {e}")
        return pd.DataFrame()

async def process_market_data():
    # Aggregating all categories from WATCHLIST
    all_tickers = (
        WATCHLIST["indices"] + 
        WATCHLIST["stocks"] + 
        WATCHLIST["commodities"] + 
        WATCHLIST["crypto"] + 
        get_sp500_tickers()
    )
    all_tickers = list(set(all_tickers))
    
    data = await fetch_ticker_batch_async(all_tickers)
    snapshot = {}
    
    for ticker in all_tickers:
        try:
            # Check if ticker exists in downloaded data
            if ticker in data.columns.get_level_values(0):
                td = data[ticker].dropna()
                if not td.empty:
                    snapshot[ticker] = {
                        "price": round(float(td["Close"].iloc[-1]), 2),
                        "change_pct": round(((float(td["Close"].iloc[-1]) - float(td["Close"].iloc[-2])) / float(td["Close"].iloc[-2])) * 100, 2)
                    }
        except: continue
    
    # Save to Redis
    r.set("latest_market_data", json.dumps(snapshot))
    return snapshot

def fetch_news():
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"
        response = requests.get(url, timeout=10)
        articles = response.json().get("articles", [])
        r.set("latest_news", json.dumps(articles[:5]))
    except: pass

def collect_and_analyze():
    """Triggered by Bot A's background scheduler."""
    asyncio.run(process_market_data())
    fetch_news()
    print(f"[{datetime.now()}] Market collection complete.")

if __name__ == "__main__":
    collect_and_analyze()