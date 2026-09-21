import urllib.request, json, time, sys

url = "http://localhost:11434/api/generate"
log_entry = {
    "timestamp": time.time(),
    "model": "phi3:latest",
    "backend": "local-ollama",
    "prompt": "Summarize the value of a hybrid home/cloud AI lab in 2 sentences."
}

payload = {
    "model": log_entry["model"],
    "prompt": log_entry["prompt"],
    "stream": False
}

print(f"Sending request to Ollama ({log_entry['model']})...")
start_time = time.time()
req = urllib.request.Request(
    url,
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)

try:
    with urllib.request.urlopen(req, timeout=120) as res:
        data = json.loads(res.read().decode("utf-8"))
        log_entry["duration_sec"] = round(time.time() - start_time, 3)
        log_entry["response"] = data.get("response")
        print(f"Success in {log_entry['duration_sec']}s")
except Exception as e:
    print(f"Error calling Ollama API: {e}", file=sys.stderr)
    sys.exit(1)

with open("lab-stacks/segment-3-hybrid-sync/experiments.jsonl", "a") as f:
    f.write(json.dumps(log_entry) + "\n")

print("Logged experiment entry cleanly.")
