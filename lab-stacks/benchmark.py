import urllib.request, json, time

for m in ["phi3:mini", "llama3.1:8b", "gemma2:9b"]:
    start = time.time()
    req = urllib.request.Request(
        "http://127.0.0.1:11434/api/generate",
        data=json.dumps({"model": m, "prompt": "Define zero trust in 2 sentences.", "stream": False}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode())
    dur = time.time() - start
    tps = res.get("eval_count", 0) / (res.get("eval_duration", 1e9) / 1e9)
    print(f"{m:15} | {tps:5.2f} tok/s | total {dur:.2f}s")
