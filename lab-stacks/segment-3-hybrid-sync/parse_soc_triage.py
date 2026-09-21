import json, time, urllib.request, pathlib, sys, re

LOG_FILE = pathlib.Path("data/soc_lab.log")
OUTPUT_FILE = pathlib.Path("soc_triage_audit.jsonl")
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "phi3:latest"

NOISE_PATTERNS = [
    re.compile(r"session closed for user", re.IGNORECASE),
    re.compile(r"pam_unix\(sshd:session\): session opened", re.IGNORECASE),
    re.compile(r"CRON\[", re.IGNORECASE)
]

THREAT_PATTERNS = [
    re.compile(r"failed password", re.IGNORECASE),
    re.compile(r"invalid user", re.IGNORECASE),
    re.compile(r"sudo:.*COMMAND", re.IGNORECASE),
    re.compile(r"(base64|cmd\.exe|powershell|curl|wget|eval\()", re.IGNORECASE)
]

def is_noise(line: str) -> bool: return any(p.search(line) for p in NOISE_PATTERNS)
def requires_llm_triage(line: str) -> bool: return any(p.search(line) for p in THREAT_PATTERNS)

def summarize_log_line(line_text: str):
    prompt = f"Analyze this SOC log for threat severity, classification, and recommended action in 2 concise sentences:\nLog: {json.dumps(line_text.strip())}"
    payload = {"model": MODEL, "prompt": prompt, "stream": False}
    req = urllib.request.Request(OLLAMA_URL, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as res:
        return json.loads(res.read().decode("utf-8")).get("response", "").strip()

def main():
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not LOG_FILE.exists():
        LOG_FILE.write_text("Failed password for invalid user admin from 192.168.1.50 port 51234 ssh2\npam_unix(sshd:session): session closed for user root\nsudo:       root : TTY=pts/0 ; PWD=/root ; USER=root ; COMMAND=/bin/bash\n")
    lines = [l for l in LOG_FILE.read_text().splitlines() if l.strip()]
    with open(OUTPUT_FILE, "a") as out:
        for idx, line in enumerate(lines):
            if is_noise(line): continue
            if requires_llm_triage(line):
                t0 = time.time()
                res = summarize_log_line(line)
                dur = round(time.time() - t0, 3)
                out.write(json.dumps({"timestamp": time.time(), "gate": "LLM_DEEP_TRIAGE", "log": line, "duration_sec": dur, "triage": res}) + "\n")
                print(f"[{idx+1}] Triaged threat in {dur}s")
            else:
                out.write(json.dumps({"timestamp": time.time(), "gate": "HEURISTIC_BYPASS", "log": line, "duration_sec": 0.0, "triage": "Standard pass"}) + "\n")
                print(f"[{idx+1}] Heuristic bypassed LLM")

if __name__ == "__main__": main()
