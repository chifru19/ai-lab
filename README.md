# AI-Lab: Multi-Segment Hybrid AI Inference Stack

Architected for multi-tier local and hybrid AI experimentation, quantization validation, telemetry tracking, and air-gapped SecOps log triage on Apple Silicon / edge hardware.

## Repository Structure
- `lab-stacks/segment-1-foundations/`: Core baseline container topologies.
- `lab-stacks/segment-3-hybrid-sync/`: Local LLM integration, zero-dep `urllib` API testing, dual-gate security log pre-filtering (`parse_soc_triage.py`), and experiment telemetry logging.
- `lab-stacks/segment-4-edge-hpc/`: Edge profile configurations (`edge-profile.yaml`) tuned for Apple Metal quantization (`Q4_K_M`), 4096 context window, and 16GB VRAM budget.
- `data/`: Sample forensic and SOC lab event logs (`soc_lab.log\فرنس).
- `run_lab.sh`: Orchestration entrypoint.

## Quick Start
```bash
./run_lab.sh
python3 lab-stacks/segment-3-hybrid-sync/track-experiment.py
python3 lab-stacks/segment-3-hybrid-sync/parse_soc_triage.py
```

## Security & Dual-Gate Architecture
1. **Gate 1 (Deterministic Noise Drop)**: Filters out operational chaff (`session closed`, cron background tasks) via compiled regex.
2. **Gate 2 (Threat Indicator Match)**: Routes high-risk indicators (`failed password`, `sudo COMMAND`, base64/cmd injections) to local `phi3:latest`.
3. **Bypass / Audit Plane**: Standard heuristic traffic bypasses LLM inference (`0.0s` duration cost) and logs clean structured records.
