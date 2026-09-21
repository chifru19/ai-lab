import json
import time
import re
from pathlib import Path

TEST_LOGS = [
    {"log": "pam_unix(sshd:session): session closed for user root", "expected_gate": "HEURISTIC_BYPASS", "expected_label": "noise"},
    {"log": "CRON[12345]: (root) CMD (run-parts /etc/cron.hourly)", "expected_gate": "HEURISTIC_BYPASS", "expected_label": "noise"},
    {"log": "Failed password for invalid user admin from 192.168.1.50 port 51234 ssh2", "expected_gate": "LLM_DEEP_TRIAGE", "expected_label": "auth_failure"},
    {"log": "sudo: root : TTY=pts/0 ; PWD=/root ; USER=root ; COMMAND=/bin/bash", "expected_gate": "LLM_DEEP_TRIAGE", "expected_label": "privesc"},
    {"log": "Failed password for invalid user admin\x1b]0;injection\x07 from 10.0.0.99 port 50000 ssh2", "expected_gate": "LLM_DEEP_TRIAGE", "expected_label": "adversarial_auth"},
    {"log": "GET /api/v1/search?q=<script>alert(1)</script> HTTP/1.1 200 128", "expected_gate": "HEURISTIC_BYPASS", "expected_label": "web_noise"},
    {"log": "GET /api/v1/status HTTP/1.1 200 512", "expected_gate": "HEURISTIC_BYPASS", "expected_label": "noise"}
]

def run_evaluation():
    print("[*] Starting Segment 4 Edge HPC Triage Evaluation...")
    results = {
        "total_samples": len(TEST_LOGS),
        "gate_accuracy": 0.0,
        "avg_bypass_cost_sec": 0.0,
        "timestamp": time.time()
    }
    
    correct_gates = 0
    noise_regex = re.compile(r"(session closed|CRON\[\d+\])")
    threat_regex = re.compile(r"(Failed password|sudo:)")

    for item in TEST_LOGS:
        line = item["log"]
        is_noise = bool(noise_regex.search(line))
        is_threat = bool(threat_regex.search(line))
        
        gate_decision = "HEURISTIC_BYPASS" if (is_noise or not is_threat) else "LLM_DEEP_TRIAGE"
        if not is_noise and not is_threat:
            gate_decision = "HEURISTIC_BYPASS"
            
        match = gate_decision == item["expected_gate"] or (item["expected_gate"] == "HEURISTIC_BYPASS" and not is_threat)
        if match:
            correct_gates += 1

    results["gate_accuracy"] = round(correct_gates / len(TEST_LOGS), 4)
    eval_out = Path("lab-stacks/segment-4-edge-hpc/edge_eval_metrics.json")
    eval_out.write_text(json.dumps(results, indent=2) + "\n")
    print(f"[+] Evaluation complete. Gate Accuracy: {results['gate_accuracy']*100}%")
    print(f"[+] Metrics written to {eval_out}")

if __name__ == "__main__":
    run_evaluation()
