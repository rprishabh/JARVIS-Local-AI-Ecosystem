"""
JARVIS BLACKROCK-LEVEL DASHBOARD — CRASH PROOF
Real-time market intelligence. Portfolio tracking. Bot monitoring.
"""

import sys
sys.path.append("C:/jarvis/config")

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import redis
import json
import yfinance as yf
import requests as req
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from api_keys import REDIS_HOST, REDIS_PORT

st.set_page_config(
    page_title="JARVIS COMMAND CENTER",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="⚡"
)

st.markdown("""
<style>
    .main { background: #0a0a1a; color: #e2e8f0; }
    .stApp { background: #0a0a1a; }
    .metric-card {
        background: #0f0f2a;
        border: 1px solid #1e3a5f;
        border-radius: 12px;
        padding: 20px;
        margin: 8px 0;
    }
    h1, h2, h3 { color: #f59e0b !important; }
    .stMetric { background: #0f0f2a; border-radius: 8px; padding: 10px; }
    .stSelectbox, .stTextInput { background: #0f0f2a; }
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=30000, limit=None, key="dashboard_refresh")

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def get_redis_data(key, default=None):
    try:
        raw = r.get(key)
        return json.loads(raw) if raw else default
    except:
        return default

st.markdown("# ⚡ JARVIS COMMAND CENTER")
st.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Auto-refresh: 30s*")
st.markdown("---")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Market Overview", "💼 Portfolio", "🤖 Bot Status", "📰 Intelligence", "🎯 Signals"])

with tab1:
    st.markdown("## Global Market Overview")
    market_data = get_redis_data("latest_market_data", {})
    col1, col2, col3, col4, col5 = st.columns(5)
    key_markets = {"^GSPC": ("S&P 500", col1), "^NSEI": ("NIFTY 50", col2), "BTC-USD": ("Bitcoin", col3), "GC=F": ("Gold", col4), "CL=F": ("Crude Oil", col5)}

    for ticker, (name, col) in key_markets.items():
        data = market_data.get(ticker, {})
        col.metric(label=name, value=f"${data.get('price', 0):,.2f}" if data.get('price') else "Loading...", delta=f"{data.get('change_pct', 0):+.2f}%")

    st.markdown("### Price Charts")
    chart_ticker = st.selectbox("Select instrument:", ["^GSPC", "^NSEI", "BTC-USD", "ETH-USD", "AAPL", "MSFT", "NVDA", "RELIANCE.NS"])
    try:
        hist = yf.download(chart_ticker, period="30d", interval="1h", auto_adjust=True, progress=False, threads=False)
        if not hist.empty:
            fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist["Open"], high=hist["High"], low=hist["Low"], close=hist["Close"])])
            fig.update_layout(paper_bgcolor="#0a0a1a", plot_bgcolor="#0a0a1a", font_color="#e2e8f0", title=f"{chart_ticker} Price Action")
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Chart error: {e}")

with tab2:
    st.markdown("## Portfolio Dashboard")
    portfolio = get_redis_data("portfolio_state", {})
    if portfolio:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Value", f"${portfolio.get('total_value', 0):,.2f}")
        c2.metric("PnL", f"${portfolio.get('pnl', 0):,.2f}", f"{portfolio.get('pnl_pct', 0):+.2f}%")
        c3.metric("Cash", f"${portfolio.get('cash', 0):,.2f}")
        c4.metric("Trades", portfolio.get("total_trades", 0))
        st.dataframe(pd.DataFrame.from_dict(portfolio.get("positions", {}), orient='index'), use_container_width=True)
    else:
        st.info("Trading bot not started yet.")

with tab3:
    st.markdown("## Bot Status")
    c1, c2, c3 = st.columns(3)
    
    # Defensive check for Bot A
    c1.markdown("### Bot A (Brain)")
    try:
        resp_a = req.get("http://localhost:6001/health", timeout=2)
        if resp_a.status_code == 200:
            c1.success("● ONLINE")
        else:
            c1.error("● OFFLINE (Bad Response)")
    except Exception:
        c1.error("● OFFLINE (Connection Refused)")

    # Defensive check for Trading Bot
    c2.markdown("### Trading Engine")
    try:
        resp_t = req.get("http://localhost:6003/health", timeout=2)
        if resp_t.status_code == 200:
            c2.success("● ONLINE")
        else:
            c2.error("● OFFLINE (Bad Response)")
    except Exception:
        c2.error("● OFFLINE (Connection Refused)")

    # Neural Link Status
    c3.markdown("### Neural Link")
    try:
        r.ping()
        c3.success("● Redis: CONNECTED")
    except Exception:
        c3.error("● Redis: OFFLINE")

with tab4:
    st.markdown("## Intelligence Feed")
    st.text_area("Latest Market Analysis", r.get("bot_b_latest_analysis") or "No analysis yet", height=150)
    news = get_redis_data("latest_news", [])
    for article in news[:5]:
        st.markdown(f"**{article.get('title', '')}**")
        st.divider()

with tab5:
    st.markdown("## Trading Signals")
    signals = get_redis_data("latest_signals", [])
    if signals:
        st.dataframe(pd.DataFrame(signals), use_container_width=True)
    else:
        st.info("Waiting for first trading cycle...")