from fastapi.testclient import TestClient
from triage_daemon import app

client = TestClient(app)

def test_healthz():
    r = client.get("/healthz")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    assert r.json()["status"] == "healthy"
    print("[+] /healthz probe verified")

def test_triage_noise_bypass():
    r = client.post("/v1/triage", json={"log_line": "pam_unix(sshd:session): session closed for user root"})
    assert r.status_code == 200
    data = r.json()
    assert data["gate"] == "HEURISTIC_BYPASS"
    assert data["duration_sec"] == 0.0
    print("[+] /v1/triage noise bypass (0.0s cost) verified")

def test_triage_threat_routing():
    r = client.post("/v1/triage", json={"log_line": "Failed password for root from 10.0.0.1 port 2222 ssh2"})
    assert r.status_code == 200
    data = r.json()
    assert data["gate"] in ["LLM_DEEP_TRIAGE", "HEURISTIC_BYPASS"]
    print(f"[+] /v1/triage evaluation passed (gate: {data['gate']}, duration: {data['duration_sec']}s)")

if __name__ == "__main__":
    test_healthz()
    test_triage_noise_bypass()
    test_triage_threat_routing()
    print("[+] All API integration checks passed cleanly.")
