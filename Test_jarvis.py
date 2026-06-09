import requests

url = "http://localhost:6001/ask"
payload = {
    "question": "What is the current market sentiment?",
    "role": "trader"
}

try:
    response = requests.post(url, json=payload)
    print("STATUS CODE:", response.status_code)
    print("RESPONSE:", response.json())
except Exception as e:
    print("ERROR:", e)