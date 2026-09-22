import re

def extract_ip(line: str) -> str:
    m = re.search(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", line)
    return m.group(0) if m else "0.0.0.0"

def evaluate(ip: str) -> dict:
    known_bad = {"10.0.0.99": {"reputation": "MALICIOUS", "threat_score": 0.98, "asn": "AS9999-AttackerNet"}}
    return known_bad.get(ip, {"reputation": "NEUTRAL", "threat_score": 0.1, "asn": "AS0000-Unknown"})
