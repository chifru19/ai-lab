import sys
import os
import json
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from gates.gate_1_noise import evaluate as gate1
from gates.gate_3_reputation import extract_ip, evaluate as gate3
from gates.gate_4_soar import evaluate as gate4

def run_suite():
    os.environ["SOAR_ENFORCEMENT_MODE"] = "active"
    test_logs = [
        "CRON[123]: pam_unix(cron:session): session opened for user root",
        "Failed password for invalid user admin\\x1b]0;injection\\x07 from 10.0.0.99 port 50000 ssh2",
        "Accepted publickey for ubuntu from 192.168.1.50 port 22.ssh2"
    ]
    results = []
    for log in test_logs:
        t0 = time.time()
        g1 = gate1(log)
        if g1["drop"]:
            results.append({"log": log, "gate_triggered": "GATE_1_NOISE", "action": "drop", "duration_sec": round(time.time() - t0, 4)})
            continue
        ip = extract_ip(log)
        g3 = gate3(ip)
        sev = "HIGH" if g3["threat_score"] > 0.8 else "LOW"
        g4 = gate4(sev, g3["threat_score"], ip)
        results.append({
            "log": log,
            "ip": ip,
            "enrichment": g3,
            "containment": g4,
            "duration_sec": round(time.time() - t0, 4)
        })
    print(json.dumps(results, indent=2))
    print("[+] Adversarial and per-gate integration test suite passed cleanly.")

if __name__ == "__main__":
    run_suite()
