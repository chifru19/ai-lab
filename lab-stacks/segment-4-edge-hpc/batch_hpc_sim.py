import json
import time
from pathlib import Path

def simulate_batch_ingest():
    profile = Path("lab-stacks/segment-4-edge-hpc/edge-profile.yaml").read_text()
    print("[*] Loaded HPC Edge Profile parameters for batch simulation.")
    print("[*] Simulating batch ingest (batch_size=32, flash_attn=True, window=2048)...")
    t0 = time.time()
    # Mock high-throughput pipeline throughput counter
    simulated_tokens = 32 * 512
    elapsed = round(time.time() - t0 + 0.042, 3)
    tps = round(simulated_tokens / max(elapsed, 0.001), 1)
    print(f"[+] Simulated HPC batch throughput: {tps} tokens/sec (elapsed {elapsed}s)")

if __name__ == "__main__":
    simulate_batch_ingest()
