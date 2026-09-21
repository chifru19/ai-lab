import json
import time
import re
import urllib.request
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="AI-Lab Dual-Gate SecOps Triage Daemon", version="1.1.0")

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "phi3:latest"

noise_regex = re.compile(r"(session closed|CRON\[\d+\])")
threat_regex = re.compile(r"(Failed password|sudo:|base64|cmd\.exe)")

class TriageRequest(BaseModel):
    log_line: str
    stream: bool = False

@app.get("/healthz")
def healthz():
    return {
        "status": "healthy",
        "backend": "local-ollama",
        "model": MODEL,
        "gates": ["deterministic_noise_drop", "threat_indicator_routing"]
    }

@app.post("/v1/triage")
def triage(req: TriageRequest):
    line = req.log_line.strip()
    t_start = time.time()

    # Gate 1: Noise drop
    if noise_regex.search(line):
        return {
            "timestamp": t_start,
            "gate": "HEURISTIC_BYPASS",
            "action": "drop_noise",
            "log": line,
            "duration_sec": 0.0,
            "triage": "Filtered noise chaff"
        }

    # Gate 2: High-risk threat routing to local LLM
    if threat_regex.search(line):
        t0 = time.time()
        prompt = f"Analyze this SOC log for threat severity, classification, and recommended action in 2 concise sentences:\n{line}"
        payload = {"model": MODEL, "prompt": prompt, "stream": False}
        ext_req = urllib.request.Request(
            OLLAMA_URL, 
            data=json.dumps(payload).encode("utf-8"), 
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(ext_req, timeout=120) as r:
                ai_resp = json.loads(r.read().decode("utf-8")).get("response", "").strip()
        except Exception as e:
            ai_resp = f"Local LLM fallback error: {e}"
        dur = round(time.time() - t0, 3)
        return {
            "timestamp": t_start,
            "gate": "LLM_DEEP_TRIAGE",
            "action": "route_to_local_llm",
            "log": line,
            "duration_sec": dur,
            "triage": ai_resp
        }

    # Audit bypass plane
    return {
        "timestamp": t_start,
        "gate": "HEURISTIC_BYPASS",
        "action": "standard_pass",
        "log": line,
        "duration_sec": 0.0,
        "triage": "Standard pass (heuristic)"
    }
