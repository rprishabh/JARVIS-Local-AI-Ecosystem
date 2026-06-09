"""
JARVIS TRADING STRATEGY ENGINE
Paper trading first. Never use real money until profitable for 90 days.
Strategy: Momentum + RSI mean reversion hybrid
"""

import sys
sys.path.append("C:/jarvis/config")

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
try:
    from api_keys import ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL
except ImportError:
    # Fallback for testing/development if keys aren't set yet
    ALPACA_API_KEY = ALPACA_SECRET_KEY = ALPACA_BASE_URL = None

PAPER_TRADING_MODE = True
RISK_PER_TRADE = 0.02
MAX_POSITIONS = 5
STOP_LOSS_PCT = 0.03
TAKE_PROFIT_PCT = 0.06

def calculate_rsi(prices: pd.Series, period: int = 14) -> float:
    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return float(rsi.iloc[-1])

def calculate_macd(prices: pd.Series) -> tuple:
    ema12 = prices.ewm(span=12).mean()
    ema26 = prices.ewm(span=26).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9).mean()
    histogram = macd - signal
    return float(macd.iloc[-1]), float(signal.iloc[-1]), float(histogram.iloc[-1])

def calculate_bollinger(prices: pd.Series, period: int = 20) -> dict:
    sma = prices.rolling(period).mean()
    std = prices.rolling(period).std()
    upper = sma + (2 * std)
    lower = sma - (2 * std)
    current = float(prices.iloc[-1])
    position = (current - float(lower.iloc[-1])) / (float(upper.iloc[-1]) - float(lower.iloc[-1]))
    return {
        "upper": float(upper.iloc[-1]),
        "middle": float(sma.iloc[-1]),
        "lower": float(lower.iloc[-1]),
        "position": round(position, 3)
    }

def generate_signal(ticker: str) -> dict:
    try:
        # Fixed the yf.download call to be clean and valid
        data = yf.download(
            ticker, 
            period="60d", 
            interval="1h",
            auto_adjust=True, 
            progress=False, 
            threads=False,
            timeout=10
        )
        
        # Check if data is empty or insufficient
        if data.empty or len(data) < 50:
            print(f"DEBUG: No data returned for {ticker}.")
            return {"ticker": ticker, "signal": "NO_DATA", "confidence": 0}

        # Flatten MultiIndex DataFrame if necessary
        close = data["Close"]
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]
            
        current_price = float(close.iloc[-1])
        
        # --- Continue with your existing indicators ---
        rsi = calculate_rsi(close)
        macd_val, macd_signal, macd_hist = calculate_macd(close)
        bollinger = calculate_bollinger(close)
        sma_20 = float(close.rolling(20).mean().iloc[-1])
        sma_50 = float(close.rolling(50).mean().iloc[-1])

        volume = data["Volume"]
        # Handle potential MultiIndex in Volume as well
        if isinstance(volume, pd.DataFrame):
            volume = volume.iloc[:, 0]
            
        avg_volume = float(volume.rolling(20).mean().iloc[-1])
        current_volume = float(volume.iloc[-1])
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1

        buy_score = 0
        sell_score = 0

        # Scoring logic
        if rsi < 35: buy_score += 2
        elif rsi < 45: buy_score += 1
        elif rsi > 65: sell_score += 2
        elif rsi > 55: sell_score += 1

        if macd_hist > 0 and macd_val > macd_signal: buy_score += 2
        elif macd_hist < 0 and macd_val < macd_signal: sell_score += 2

        if current_price > sma_20 > sma_50: buy_score += 1
        elif current_price < sma_20 < sma_50: sell_score += 1

        if bollinger["position"] < 0.2: buy_score += 1
        elif bollinger["position"] > 0.8: sell_score += 1

        if volume_ratio > 1.5:
            if buy_score > sell_score: buy_score += 1
            else: sell_score += 1

        total_score = buy_score + sell_score
        confidence = round((max(buy_score, sell_score) / 7) * 100, 1) if total_score > 0 else 0

        if buy_score >= 4 and confidence >= 50: signal = "BUY"
        elif sell_score >= 4 and confidence >= 50: signal = "SELL"
        else: signal = "HOLD"

        return {
            "ticker": ticker,
            "signal": signal,
            "confidence": confidence,
            "current_price": round(current_price, 2),
            "rsi": round(rsi, 2),
            "macd": round(macd_val, 4),
            "macd_signal": round(macd_signal, 4),
            "bollinger_position": bollinger["position"],
            "volume_ratio": round(volume_ratio, 2),
            "sma_20": round(sma_20, 2),
            "sma_50": round(sma_50, 2),
            "buy_score": buy_score,
            "sell_score": sell_score,
            "stop_loss": round(current_price * (1 - STOP_LOSS_PCT), 2),
            "take_profit": round(current_price * (1 + TAKE_PROFIT_PCT), 2),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        return {"ticker": ticker, "signal": "ERROR", "error": str(e), "confidence": 0}

import time # Ensure this is at the top of your file with other imports

def scan_watchlist(tickers: list) -> list:
    signals = []
    for ticker in tickers:
        signal = generate_signal(ticker)
        signals.append(signal)
        print(f"{ticker}: {signal.get('signal')} ({signal.get('confidence')}% confidence)")
        time.sleep(2.5) # Add a 2.5-second pause between each ticker
    return signals

PAPER_PORTFOLIO = {
    "cash": 100000,
    "positions": {},
    "trades": []
}

def paper_trade(signal: dict, portfolio: dict) -> dict:
    if signal["signal"] not in ["BUY", "SELL"]:
        return portfolio
    if signal["confidence"] < 60:
        return portfolio

    ticker = signal["ticker"]
    price = signal["current_price"]
    cash = portfolio["cash"]
    positions = portfolio["positions"]

    if signal["signal"] == "BUY":
        if len(positions) >= MAX_POSITIONS:
            return portfolio
        if ticker in positions:
            return portfolio

        trade_value = cash * RISK_PER_TRADE
        shares = int(trade_value / price)

        if shares > 0 and trade_value <= cash:
            positions[ticker] = {
                "shares": shares,
                "entry_price": price,
                "entry_time": datetime.now().isoformat(),
                "stop_loss": signal["stop_loss"],
                "take_profit": signal["take_profit"],
                "cost": shares * price
            }
            portfolio["cash"] -= shares * price
            portfolio["trades"].append({
                "action": "BUY",
                "ticker": ticker,
                "shares": shares,
                "price": price,
                "timestamp": datetime.now().isoformat(),
                "confidence": signal["confidence"]
            })
            print(f"PAPER BUY: {shares} shares of {ticker} at ${price}")

    elif signal["signal"] == "SELL" and ticker in positions:
        position = positions[ticker]
        proceeds = position["shares"] * price
        pnl = proceeds - position["cost"]
        pnl_pct = (pnl / position["cost"]) * 100

        portfolio["cash"] += proceeds
        portfolio["trades"].append({
            "action": "SELL",
            "ticker": ticker,
            "shares": position["shares"],
            "price": price,
            "pnl": round(pnl, 2),
            "pnl_pct": round(pnl_pct, 2),
            "timestamp": datetime.now().isoformat()
        })
        del positions[ticker]
        print(f"PAPER SELL: {ticker} PnL: ${round(pnl, 2)} ({round(pnl_pct, 2)}%)")

    return portfolio

if __name__ == "__main__":
    test_tickers = ["AAPL", "MSFT", "NVDA", "GOOGL", "META"]
    print("Scanning watchlist...")
    signals = scan_watchlist(test_tickers)
    print("\nSignal Summary:")
    for s in signals:
        print(f"  {s['ticker']}: {s['signal']} | Confidence: {s.get('confidence', 0)}%")