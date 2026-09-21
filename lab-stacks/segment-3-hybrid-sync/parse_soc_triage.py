import json, time, urllib.request, pathlib, sys

LOG_FILE = pathlib.Path("data/soc_lab.log")
OUTPUT_FILE = pathlib.Path("soc_triage_audit.jsonl")
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "phi3:latest"

def summarize_log_line(line_text: str):
    prompt = f"Analyze this SOC log for threat severity, classification, and recommended action in 2 concise sentences:\n{line_text.strip()}"
    payload = {"model": MODEL, "prompt": prompt, "stream": False}
    req = urllib.request.Request(OLLAMA_URL, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as res:
        return json.loads(res.read().decode("utf-8")).get("response", "").strip()

def main():
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not LOG_FILE.exists():
        LOG_FILE.write_text("Failed password for invalid user admin from 192.168.1.50 port 51234 ssh2\n")
    lines = [l for l in LOG_FILE.read_text().splitlines() if l.strip()][:3]
    with open(OUTPUT_FILE, "a") as out:
        for idx, line in enumerate(lines):
            t0 = time.time()
            res = summarize_log_line(line)
            dur = round(time.time() - t0, 3)
            out.write(json.dumps({"timestamp": time.time(), "log": line, "duration_sec": dur, "triage": res}) + "\n")
            print(f"[{idx+1}] Triaged in {dur}s")

if __name__ == "__main__": main()
