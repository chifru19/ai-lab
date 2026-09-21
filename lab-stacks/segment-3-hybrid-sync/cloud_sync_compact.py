import json
import time
from pathlib import Path
import hashlib

def compact_telemetry():
    src_paths = [
        Path("lab-stacks/segment-3-hybrid-sync/experiments.jsonl"),
        Path("soc_triage_audit.jsonl")
    ]
    
    sink_dir = Path("data/cloud_sync_sink")
    sink_dir.mkdir(parents=True, exist_ok=True)
    
    aggregated_records = []
    for p in src_paths:
        if p.exists():
            for line in p.read_text().splitlines():
                line = line.strip()
                if line:
                    try:
                        aggregated_records.append({"source": str(p), "data": json.loads(line)})
                    except json.JSONDecodeError:
                        pass
                        
    compaction_id = hashlib.sha256(f"{time.time()}_{len(aggregated_records)}".encode()).hexdigest()[:12]
    payload_raw = json.dumps(aggregated_records, sort_keys=True)
    digest = hashlib.sha256(payload_raw.encode()).hexdigest()
    
    bundle = {
        "compaction_id": compaction_id,
        "schema_version": "1.0",
        "timestamp": time.time(),
        "record_count": len(aggregated_records),
        "sha256_digest": digest,
        "records": aggregated_records
    }
    
    out_file = sink_dir / f"batch_compaction_{compaction_id}.json"
    out_file.write_text(json.dumps(bundle, indent=2) + "\n")
    
    manifest = {
        "last_sync_timestamp": time.time(),
        "latest_compaction_file": str(out_file),
        "total_records_compacted": len(aggregated_records),
        "latest_digest": digest
    }
    manifest_file = sink_dir / "sync_manifest.json"
    manifest_file.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"[+] Compacted {len(aggregated_records)} records -> {out_file} (digest: {digest[:16]}...)")

if __name__ == "__main__":
    compact_telemetry()
