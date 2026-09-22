import re

def evaluate(log_line: str) -> dict:
    noise_patterns = [r"CRON\[\d+\]: (pam_unix|session)"]
    is_noise = any(re.search(p, log_line) for p in noise_patterns)
    return {"drop": is_noise, "reason": "deterministic_noise" if is_noise else "retained"}
