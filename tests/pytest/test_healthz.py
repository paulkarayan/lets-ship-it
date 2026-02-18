import httpx
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_healthz():
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}

def test_healthz_integration():
    resp = httpx.get("http://localhost:8000/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
