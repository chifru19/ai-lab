import time, json, urllib.request, datetime

log_entry = {
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "model": "phi3:latest",
    "backend": "local-ollama",
    "prompt": "Summarize the value of a hybrid home/cloud AI lab in 2 sentences."
}

start_time = time.time()
url = "http://localhost:11434/api/generate"
payload = {
    "model": log_entry["model"],
    "prompt": log_entry["prompt"],
    "stream": False
}

req = urllib.request.Request(
    url,
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)

with urllib.request.urlopen(req, timeout=120) as res:
    data = json.loads(res.read().decode("utf-8"))
    log_entry["duration_sec"] = round(time.time() - start_time, 3)
    log_entry["response"] = data.get("response")

with open("lab-stacks/segment-3-hybrid-sync/experiments.jsonl", "a") as f:
    f.write(json.dumps(log_entry) + "\n")

print("Logged experiment entry cleanly.")
