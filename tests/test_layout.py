import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"

def test_get_catalog():
    response = client.get("/api/layout/catalog")
    assert response.status_code == 200
    data = response.json()
    assert "catalog" in data
    assert len(data["catalog"]) > 0

def test_generate_layout():
    payload = {
        "prompt": "Konser musik jazz kapasitas 200 orang ada panggung dan meja VIP",
        "venue_name": "Test Grand Ballroom",
        "venue_width": 30.0,
        "venue_length": 20.0
    }
    response = client.post("/api/layout/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) > 0
    assert data["venue_name"] == "Test Grand Ballroom"

def test_save_and_retrieve_layout():
    # 1. Generate
    payload = {
        "prompt": "Pameran teknologi 5 booth pameran",
        "venue_name": "Tech Hall"
    }
    gen_res = client.post("/api/layout/generate", json=payload)
    layout = gen_res.json()

    # 2. Save
    save_res = client.post("/api/layout/save", json={"layout": layout})
    assert save_res.status_code == 200
    save_data = save_res.json()
    assert "layout_id" in save_data

    # 3. Retrieve
    layout_id = save_data["layout_id"]
    get_res = client.get(f"/api/layout/{layout_id}")
    assert get_res.status_code == 200
    retrieved = get_res.json()
    assert retrieved["venue_name"] == "Tech Hall"

