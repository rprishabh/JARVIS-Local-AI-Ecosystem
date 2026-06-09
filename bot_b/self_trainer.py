"""
JARVIS BOT B — SELF TRAINING ENGINE
Uses market outcomes to train the brain.
Good predictions are reinforced. Bad ones are corrected.
Runs every hour automatically.
"""

import sys
sys.path.append("C:/jarvis/config")

import json
import redis
import chromadb
import requests
from datetime import datetime
from api_keys import LITELLM_URL, REDIS_HOST, REDIS_PORT

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
chroma_client = chromadb.HttpClient(host="localhost", port=8000)
brain = chroma_client.get_or_create_collection("jarvis_brain")
training_data = chroma_client.get_or_create_collection("training_data")

def analyze_market_pattern(market_data: dict, signals: dict) -> str:
    context = f"Market Data: {json.dumps(market_data)}\nSignals: {json.dumps(signals)}"

    response = requests.post(
        f"{LITELLM_URL}/chat/completions",
        json={
            "model": "jarvis_brain",
            "messages": [
                {
                    "role": "system",
                    "content": """You are a quantitative analyst. Analyze the provided market data.
Identify patterns, trends, anomalies. Generate a structured insight.
Output format:
TREND: [bullish/bearish/neutral]
STRENGTH: [1-10]
KEY_LEVELS: [important price levels]
PATTERN: [name of pattern if recognized]
RISK: [low/medium/high]
INSIGHT: [2 sentence analysis]"""
                },
                {"role": "user", "content": context}
            ]
        },
        timeout=120
    )
    return response.json()["choices"][0]["message"]["content"]

def generate_training_pair(query: str, good_answer: str, context: str = "") -> dict:
    return {
        "instruction": query,
        "context": context,
        "response": good_answer,
        "timestamp": datetime.now().isoformat(),
        "source": "bot_b_auto"
    }

def self_train_cycle():
    print(f"[{datetime.now()}] Starting self-training cycle...")

    market_data_raw = r.get("latest_market_data")
    signals_raw = r.get("latest_signals")

    if not market_data_raw:
        print("No market data available. Skipping training cycle.")
        return

    market_data = json.loads(market_data_raw)
    signals = json.loads(signals_raw) if signals_raw else {}

    analysis = analyze_market_pattern(market_data, signals)

    timestamp = datetime.now().isoformat()
    brain.add(
        documents=[analysis],
        metadatas=[{
            "type": "bot_b_analysis",
            "timestamp": timestamp,
            "cycle": "auto"
        }],
        ids=[f"analysis_{timestamp}"]
    )

    training_pair = generate_training_pair(
        query=f"Analyze current market conditions as of {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        good_answer=analysis,
        context=f"Market snapshot: {json.dumps(list(market_data.items())[:5])}"
    )

    training_data.add(
        documents=[json.dumps(training_pair)],
        metadatas=[{"timestamp": timestamp, "type": "market_analysis"}],
        ids=[f"training_{timestamp}"]
    )

    r.set("bot_b_latest_analysis", analysis)
    r.set("bot_b_last_trained", timestamp)

    total_training = training_data.count()
    print(f"[{datetime.now()}] Training cycle complete. Total training examples: {total_training}")

if __name__ == "__main__":
    self_train_cycle()