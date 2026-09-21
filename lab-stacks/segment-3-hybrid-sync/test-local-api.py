import requests

url = "http://localhost:11434/api/generate"
payload = {
    "model": "gemma:latest",
    "prompt": "Summarize the value of a hybrid home/cloud AI lab in 2 sentences.",
    "stream": False
}

try:
    res = requests.post(url, json=payload, timeout=30)
    res.raise_for_status()
    print("Response from local Gemma:\n", res.json().get("response"))
except Exception as e:
    print("Error connecting to local Ollama:", e)
