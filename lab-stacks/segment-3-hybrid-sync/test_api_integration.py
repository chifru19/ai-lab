import sys
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent))
from triage_daemon import app

client = TestClient(app)

def test_healthz():
    r = client.get("/healthz")
    assert r.status_code == 200
    print("[+] /healthz probe verified")

def test_triage_flow():
    payload = {"log_line": "CRON[123]: session opened for user root"}
    r = client.post("/v1/triage", json=payload)
    assert r.status_code == 200, f"Unexpected status: {r.status_code}"
    data = r.json()
    assert "gate_triggered" in data and "action" in data, f"Schema mismatch: {data}"

if __name__ == "__main__":
    test_healthz()
    test_triage_flow()
    print("[+] All integration tests passed cleanly.")
