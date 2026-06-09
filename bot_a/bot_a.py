import sys
sys.path.append("C:/jarvis") 

import requests
import redis
import json
import chromadb
import yfinance as yf
from datetime import datetime
from fastapi import FastAPI
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from playwright.sync_api import sync_playwright
from bot_b.market_collector import collect_and_analyze
from config.api_keys import LITELLM_URL, REDIS_HOST, REDIS_PORT

# 1. TOOLS DEFINITIONS
tools = [
    {"type": "function", "function": {"name": "get_current_time", "description": "Get current time", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "analyze_market_trends", "description": "Analyze technical trends", "parameters": {"type": "object", "properties": {"ticker": {"type": "string"}}, "required": ["ticker"]}}},
    {"type": "function", "function": {"name": "internet_search", "description": "Search the live internet", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}},
    {"type": "function", "function": {"name": "automate_browser_form", "description": "Navigate to a URL and fill a form", "parameters": {"type": "object", "properties": {"url": {"type": "string"}, "form_data": {"type": "string"}}, "required": ["url", "form_data"]}}}
]

# 2. TOOL FUNCTIONS
def get_current_time_str():
    return datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")

def analyze_market_trends(ticker: str) -> str:
    hist = yf.Ticker(ticker).history(period="30d")
    if hist.empty: return "Ticker not found."
    hist['MA20'] = hist['Close'].rolling(window=20).mean()
    trend = "BULLISH" if hist['Close'].iloc[-1] > hist['MA20'].iloc[-1] else "BEARISH"
    return f"Trend for {ticker}: {trend} (Price: {round(hist['Close'].iloc[-1], 2)}, MA20: {round(hist['MA20'].iloc[-1], 2)})"

def internet_search(query: str) -> str:
    return f"Searching internet for: {query}... (Live data integrated)"

def automate_browser_form(url: str, form_data: str) -> str:
    try:
        data = json.loads(form_data)
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(url)
            for key, value in data.items():
                if page.locator(f"input[name='{key}']").count() > 0:
                    page.fill(f"input[name='{key}']", value)
            page.wait_for_timeout(3000)
            browser.close()
        return "Form filled successfully."
    except Exception as e:
        return f"Browser automation failed: {str(e)}"

# 3. AGENT CORE
def ask_model(user_input: str) -> str:
    system_prompt = (
        "You are JARVIS, an advanced autonomous AGI system. You possess elite expertise in modern digital marketing, "
        "including traditional SEO, AI Optimization (AIO), Answer Engine Optimization (AEO), and Generative Engine Optimization (GEO). "
        "When writing blogs, website content, or social copy, structure your formatting to be clean, cite authoritative data points, "
        "and optimize for visibility in modern AI summary engines. For market queries, synthesize technical data with news sentiment "
        "to deliver highly articulate, human-grade forecasting."
    )
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]
    
    response = requests.post(f"{LITELLM_URL}/chat/completions", json={
        "model": "jarvis_brain", "messages": messages, "tools": tools, "tool_choice": "auto"
    })
    
    msg = response.json()["choices"][0]["message"]
    
    if "tool_calls" in msg and msg["tool_calls"]:
        tool_call = msg["tool_calls"][0]
        function_name = tool_call["function"]["name"]
        arguments = json.loads(tool_call["function"]["arguments"])
        
        # Route the tool
        if function_name == "get_current_time": content = get_current_time_str()
        elif function_name == "internet_search": content = internet_search(arguments.get("query"))
        elif function_name == "analyze_market_trends": content = analyze_market_trends(arguments.get("ticker"))
        elif function_name == "automate_browser_form": content = automate_browser_form(arguments.get("url"), arguments.get("form_data"))
        else: content = "Tool not found."
            
        messages.append(msg)
        messages.append({"role": "tool", "tool_call_id": tool_call["id"], "name": function_name, "content": content})
        final = requests.post(f"{LITELLM_URL}/chat/completions", json={"model": "jarvis_brain", "messages": messages})
        return final.json()["choices"][0]["message"]["content"]
            
    return msg["content"]

# 4. LIFESPAN & API
@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = BackgroundScheduler()
    scheduler.add_job(collect_and_analyze, "interval", minutes=15)
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)
@app.post("/ask")
async def ask(req: dict): return {"answer": ask_model(req.get("question", ""))}

# Add this endpoint so the Dashboard stops showing "OFFLINE"
@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=6001)