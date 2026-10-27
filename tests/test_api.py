from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    assert client.get("/health").json()["status"] == "ok"

def test_evaluation():
    response = client.post("/evaluate", json={
        "source": "olx", "url": "https://www.olx.ro/example", "title": "Camera",
        "category": "foto", "price_ron": 600, "reference_price_ron": 1000,
        "confidence": 0.9
    })
    assert response.status_code == 200
    assert response.json()["discount_pct"] == 40

def test_no_live_feed():
    assert client.get("/deals").json()["status"] == "no_authorized_olx_feed"
