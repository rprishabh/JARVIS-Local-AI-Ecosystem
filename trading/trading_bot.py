"""
JARVIS TRADING BOT — CONSOLIDATED
Runs in background. Paper trades every 30 minutes.
Learns from outcomes to improve strategy.
"""

import sys
sys.path.append("C:/jarvis/config")
sys.path.append("C:/jarvis/trading")

import asyncio
from fastapi import FastAPI
import redis
import json
import chromadb
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from api_keys import REDIS_HOST, REDIS_PORT
from strategy import generate_signal, scan_watchlist, paper_trade, PAPER_PORTFOLIO

app = FastAPI(title="JARVIS Trading Bot")

# Connect to shared brain
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
chroma_client = chromadb.HttpClient(host="localhost", port=8000)
trade_brain = chroma_client.get_or_create_collection("trade_brain")

scheduler = BackgroundScheduler()
portfolio = PAPER_PORTFOLIO.copy()

TRADING_WATCHLIST = [
    "AAPL", "MSFT", "NVDA", "GOOGL", "META",
    "TSLA", "AMD", "AMZN", "JPM", "BAC",
    "BTC-USD", "ETH-USD"
]

def trading_cycle():
    global portfolio
    print(f"[{datetime.now()}] Running trading cycle...")

    signals = scan_watchlist(TRADING_WATCHLIST)

    # Filter signals that have high confidence
    actionable = [s for s in signals if s.get("signal") in ["BUY", "SELL"]
                  and s.get("confidence", 0) >= 60]

    for signal in actionable:
        portfolio = paper_trade(signal, portfolio)

    # Calculate portfolio total value
    total_value = portfolio["cash"]
    for ticker, pos in portfolio["positions"].items():
        signal = generate_signal(ticker)
        if signal.get("current_price"):
            total_value += pos["shares"] * signal["current_price"]

    # Save state to Redis
    portfolio_state = {
        "cash": round(portfolio["cash"], 2),
        "positions": portfolio["positions"],
        "total_value": round(total_value, 2),
        "pnl": round(total_value - 100000, 2),
        "pnl_pct": round(((total_value - 100000) / 100000) * 100, 2),
        "total_trades": len(portfolio["trades"]),
        "last_update": datetime.now().isoformat()
    }

    r.set("portfolio_state", json.dumps(portfolio_state))
    r.set("latest_signals", json.dumps(signals))

    print(f"Portfolio Value: ${portfolio_state['total_value']} | PnL: ${portfolio_state['pnl']} ({portfolio_state['pnl_pct']}%)")

@app.on_event("startup")
async def startup():
    # Schedule the cycle to run every 30 minutes
    scheduler.add_job(
        trading_cycle,
        "interval",
        minutes=30,
        id="trading_cycle",
        next_run_time=datetime.now() # Trigger immediately on startup
    )
    scheduler.start()
    print("Trading Bot started. Cycles every 30 minutes.")

@app.get("/portfolio")
async def get_portfolio():
    raw = r.get("portfolio_state")
    if raw:
        return json.loads(raw)
    return {"error": "No portfolio data yet"}

@app.get("/trades")
async def get_trades():
    return {
        "total_trades": len(portfolio["trades"]),
        "recent_trades": portfolio["trades"][-10:]
    }

@app.get("/signals")
async def get_signals():
    raw = r.get("latest_signals")
    if raw:
        return json.loads(raw)
    return []

@app.post("/trigger")
async def trigger_cycle():
    trading_cycle()
    return {"status": "Trading cycle executed"}

@app.get("/health")
async def health():
    return {"status": "Trading Bot Online", "mode": "PAPER", "port": 6003}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=6003)