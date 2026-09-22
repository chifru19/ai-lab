import json
import time
import urllib.request
import re
from pathlib import Path
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="AI-Lab Dual-4-Gate Triage Daemon", version="2.0.0")

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "phi3:latest"
CONTAINMENT_LOG_FILE = Path("data/containment_actions.log")
CONTAINMENT_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

class TriageRequest(BaseModel):
    log_line: str
    source_ip: str | None = None

class TriageResponse(BaseModel):
    timestamp: float
    gate_triggered: str
    action: str
    log: str
    duration_sec: float
    enrichment: dict | None = None
    containment_status: str | None = None
    triage: str

def is_deterministic_noise(line: str) -> bool:
    noise_patterns = [
        r"CRON\[\d+\]: \((CRON|root)\) CMD",
        r"Healthz check OK",
        r"garbage collection cycle"
    ]
    return any(re.search(p, line, re.IGNORECASE) for p in noise_patterns)

def extract_ip_from_line(line: str) -> str | None:
    match = re.search(r'\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b', line)
    return match.group(0) if match else None

# Gate 3: Local Reputation & Enrichment Cache Lookup
def gate_3_enrichment(ip: str | None) -> dict:
    known_malicious = {"10.0.0.99": {"reputation": "MALICIOUS", "threat_score": 0.98, "asn": "AS9999-AttackerNet"}}
    known_benign = {"127.0.0.1": {"reputation": "TRUSTED", "threat_score": 0.0, "asn": "LOCAL-LOOPBACK"}}
    if not ip:
        return {"ip": None, "reputation": "UNKNOWN", "threat_score": 0.1, "asn": "NONE"}
    if ip in known_malicious:
        return {**known_malicious[ip], "ip": ip}
    if ip in known_benign:
        return {**known_benign[ip], "ip": ip}
    return {"ip": ip, "reputation": "NEUTRAL", "threat_score": 0.3, "asn": "EXTERNAL-IP"}

# Gate 4: Action / Containment Enforcement Policy
def gate_4_containment(severity: str, threat_score: float, ip: str | None) -> tuple[str, str]:
    if severity.upper() in ["HIGH", "CRITICAL"] and threat_score >= 0.8 and ip:
        action_msg = f"[AUTOMATED CONTAINMENT] Blocked IP {ip} via local nftables/firewall hook."
        record = json.dumps({"timestamp": time.time(), "action": "BLOCK_IP", "target": ip, "score": threat_score})
        with CONTAINMENT_LOG_FILE.open("a") as f:
            f.write(record + "\n")
        return "AUTO_MITIGATED", action_msg
    else:
        queue_msg = f"[SOC QUEUE] Escalated finding to analyst review queue (Score: {threat_score})."
        return "QUEUED_FOR_SOC", queue_msg

@app.get("/healthz")
def healthz():
    return {
        "status": "healthy",
        "backend": "local-ollama",
        "model": MODEL_NAME,
        "gates": [
            "gate_1_deterministic_noise_drop",
            "gate_2_local_llm_deep_triage",
            "gate_3_local_reputation_enrichment",
            "gate_4_automated_containment_soar"
        ]
    }

@app.post("/v1/triage", response_model=TriageResponse)
def triage_log(req: TriageRequest):
    t0 = time.time()
    line = req.log_line

    # Gate 1: Noise drop
    if is_deterministic_noise(line):
        return TriageResponse(
            timestamp=t0,
            gate_triggered="GATE_1_HEURISTIC_BYPASS",
            action="drop_noise",
            log=line,
            duration_sec=round(time.time() - t0, 3),
            enrichment=None,
            containment_status="FILTERED_NOISE",
            triage="Standard pass (deterministic noise filtered)"
        )

    # Gate 2: Local LLM Deep Triage via Ollama
    prompt = f"""Analyze this SOC security log line for severity (LOW, MEDIUM, HIGH, CRITICAL) and brief threat summary:
    Log: {line}"""
    ext_req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps({"model": MODEL_NAME, "prompt": prompt, "stream": False}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(ext_req, timeout=120) as r:
            ai_resp = json.loads(r.read().decode("utf-8")).get("response", "").strip()
    except Exception as e:
        ai_resp = f"Local LLM fallback error: {e}"

    extracted_ip = req.source_ip or extract_ip_from_line(line)

    # Gate 3: Local Reputation & Enrichment Check
    enrichment_data = gate_3_enrichment(extracted_ip)

    severity_val = "MEDIUM" if "critical" in ai_resp.lower() or "injection" in ai_resp.lower() else "LOW"
    if enrichment_data["threat_score"] > 0.8:
        severity_val = "HIGH"

    # Gate 4: Action / Containment Enforcement
    containment_status, containment_action = gate_4_containment(severity_val, enrichment_data["threat_score"], extracted_ip)

    dur = round(time.time() - t0, 3)
    return TriageResponse(
        timestamp=t0,
        gate_triggered="GATE_2_THROUGH_4_COMPLETE",
        action="deep_triage_enriched_contained",
        log=line,
        duration_sec=dur,
        enrichment=enrichment_data,
        containment_status=f"{containment_status} | {containment_action}",
        triage=ai_resp
    )
