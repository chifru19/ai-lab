import os
import time

def evaluate(severity: str, threat_score: float, ip: str) -> dict:
    mode = os.getenv("SOAR_ENFORCEMENT_MODE", "dry_run")
    should_mitigate = severity in ("HIGH", "CRITICAL") or threat_score > 0.8
    
    action_str = f"Blocked IP {ip} via firewall hook." if should_mitigate else "Monitor/No action."
    status = "AUTO_MITIGATED" if (should_mitigate and mode == "active") else ("DRY_RUN_MITIGATE" if should_mitigate else "NO_ACTION")
    
    if should_mitigate and mode == "active":
        os.makedirs("data", exist_ok=True)
        with open("data/containment_actions.log", "a") as f:
            f.write(f"{time.time()}|{ip}|{severity}|{threat_score}|MITIGATED\n")
            
    return {"status": status, "action": action_str, "mode": mode}
