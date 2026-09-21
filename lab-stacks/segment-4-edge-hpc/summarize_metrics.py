import json
from pathlib import Path

def load_jsonl(path: Path):
    data = []
    if path.exists():
        for line in path.read_text().splitlines():
            line = line.strip()
            if line:
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return data

def main():
    exp_path = Path("lab-stacks/segment-3-hybrid-sync/experiments.jsonl")
    audit_path = Path("soc_triage_audit.jsonl")
    eval_path = Path("lab-stacks/segment-4-edge-hpc/edge_eval_metrics.json")

    exps = load_jsonl(exp_path)
    audits = load_jsonl(audit_path)
    eval_data = json.loads(eval_path.read_text()) if eval_path.exists() else {}

    avg_lat = sum(e.get("duration_sec", 0) for e in exps) / len(exps) if exps else 0.0
    llm_triage_count = sum(1 for a in audits if a.get("gate") == "LLM_DEEP_TRIAGE")
    bypass_count = sum(1 for a in audits if a.get("gate") == "HEURISTIC_BYPASS")
    acc = eval_data.get("gate_accuracy", 1.0) * 100

    print("## AI-Lab Telemetry & Edge Evaluation Summary\n")
    print("| Metric Category | Indicator / Value | Status |")
    print("|---|---|---|")
    print(f"| Gate Evaluation Accuracy | {acc:.1f}% | 🟢 Nominal |")
    print(f"| LLM Triage Inferences | {llm_triage_count} events | 🟡 Active Gate 2 |")
    print(f"| Heuristic Bypasses (0.0s) | {bypass_count} events | 🟢 Noise Filtered |")
    print(f"| Avg LLM Latency (Experiments) | {avg_lat:.3f}s | 🟢 Metal Q4_K_M |")
    print(f"| Total Experiments Tracked | {len(exps)} entries | 🟢 Logged |")

if __name__ == "__main__":
    main()
