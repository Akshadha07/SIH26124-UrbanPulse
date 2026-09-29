import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db, SessionLocal
from app.models.hazard import Hazard
from app.models.bus import BusLiveState

@pytest.fixture(scope="module")
def client():
    init_db()
    with TestClient(app) as c:
        yield c

def test_citizen_nearby_hazards(client):
    # Seed a test hazard near Sayajigunj (22.3108, 73.1812)
    db = SessionLocal()
    try:
        test_hazard = Hazard(
            hazard_type="pothole",
            lat=22.3120,
            lon=73.1820,
            severity=4.0,
            confidence=0.92,
            is_confirmed=True,
            status="confirmed",
            priority_score=78.5,
            address_hint="Sayajigunj Near Station",
        )
        db.add(test_hazard)
        db.commit()
    finally:
        db.close()

    # Query within 2km of (22.3108, 73.1812)
    response = client.get("/api/v1/citizen/hazards/nearby?lat=22.3108&lon=73.1812&radius_meters=2000")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    # Verify distance is computed in meters and fields match citizen response schema
    item = next(h for h in data if h["address_hint"] == "Sayajigunj Near Station")
    assert item["distance_meters"] > 0.0
    assert item["distance_meters"] < 500.0  # Approx 150-200m away
    assert item["priority_score"] == 78.5
    assert item["is_confirmed"] is True

def test_citizen_crowd_prediction(client):
    response = client.get("/api/v1/citizen/bus/crowd-prediction")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    
    first_bus = data[0]
    assert "route_id" in first_bus
    assert "current_occupancy_level" in first_bus
    assert "predicted_occupancy_level" in first_bus
    assert "trend" in first_bus
    assert first_bus["trend"] in ["STABLE", "INCREASING", "DECREASING"]
    assert first_bus["capacity"] > 0

def test_citizen_submit_report_and_retrieve(client):
    payload = {
        "category": "pothole",
        "lat": 22.3142,
        "lon": 73.1865,
        "description": "Deep pothole near Sayaji Baug Gate 1 causing traffic slowdown",
        "photo_url": "https://example.com/photos/pothole1.jpg",
        "device_id_hash": "test-device-sha256-hash-001",
    }

    # Submit
    post_res = client.post("/api/v1/citizen/report", json=payload)
    assert post_res.status_code == 201
    created = post_res.json()
    assert created["id"] > 0
    assert created["category"] == "pothole"
    assert created["status"] == "SUBMITTED"
    assert created["description"] == payload["description"]

    # Retrieve via /api/v1/citizen/reports
    get_res = client.get(f"/api/v1/citizen/reports?device_id_hash={payload['device_id_hash']}")
    assert get_res.status_code == 200
    reports = get_res.json()
    assert len(reports) >= 1
    assert reports[0]["id"] == created["id"]
