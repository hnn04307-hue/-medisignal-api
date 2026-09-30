import json
from pathlib import Path

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_signal_endpoint():
    sample = Path(__file__).parents[1] / "data" / "sample_fhir_bundle.json"
    bundle = json.loads(sample.read_text(encoding="utf-8"))
    r = client.post("/v1/signals/from-fhir", json=bundle)
    assert r.status_code == 200
    body = r.json()
    assert body["patient_id"] == "synthetic-patient-001"
    assert body["signal_count"] == 3
    assert body["signal_level"] == "multiple-demo-flags"
    assert "not a diagnosis" in body["disclaimer"]
