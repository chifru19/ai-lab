# AI-Lab: Multi-Segment Hybrid AI Inference Stack

Architected for multi-tier local and hybrid AI experimentation, quantization validation, and telemetry tracking on Apple Silicon / edge hardware.

## Repository Structure
- `lab-stacks/segment-1-foundations/`: Core baseline container topologies.
- `lab-stacks/segment-3-hybrid-sync/`: Local LLM integration, API testing, and experiment telemetry logging.
- `lab-stacks/segment-4-edge-hpc/`: Edge profile configurations tuned for Apple Metal quantization (`Q4_K_M`).
- `run_lab.sh`: Orchestration entrypoint.

## Quick Start
```bash
./run_lab.sh
python3 lab-stacks/segment-3-hybrid-sync/track-experiment.py
```
