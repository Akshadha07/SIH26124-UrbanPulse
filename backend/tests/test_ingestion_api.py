"""
Integration Tests for Phase 2A Ingestion and Simulation APIs
Tests FastAPI endpoints using TestClient:
- Event ingestion (single & batch)
- Telemetry updates
- Scenario triggering
- Simulator tick execution
- Fleet live view and routes
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db

@pytest.fixture(scope="module")
def client():
    init_db()
    with TestClient(app) as c:
        yield c

def test_ingest_single_raw_sensor_event(client):
    """Test POST /api/v1/ingest/event with raw IMU window."""
    payload = {
        "bus_id": "GJ-06-BT-101",
        "type": "imu_stream_window",
        "lat": 22.3108,
        "lon": 73.1812,
        "confidence": 1.0,
        "value": 14.5,
        "sensor_source": "imu",
        "imu_window": {
            "ax": 0.05,
            "ay": -0.02,
            "az": 14.5,
            "peak_z": 14.5,
            "samples": [[0.05, -0.02, 14.5, 0.0]],
        },
        "is_simulated": True,
    }
    response = client.post("/api/v1/ingest/event", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "ingested"
    assert data["bus_id"] == "GJ-06-BT-101"
    assert data["raw_event_id"] > 0
    assert data["is_simulated"] is True

def test_ingest_batch_sensor_events(client):
    """Test POST /api/v1/ingest/batch with multiple raw events."""
    payload = {
        "events": [
            {
                "bus_id": "GJ-06-BT-102",
                "type": "camera_frame_ping",
                "lat": 22.3115,
                "lon": 73.1750,
                "sensor_source": "camera",
                "raw_camera_ref": "assets/frames/vadodara_test_01.jpg",
                "is_simulated": True,
            },
            {
                "bus_id": "GJ-06-BT-103",
                "type": "water_proxy_reading",
                "lat": 22.2965,
                "lon": 73.1750,
                "sensor_source": "water_sensor",
                "water_proxy": {
                    "water_reflection_index": 0.85,
                    "wheel_drag_coefficient": 0.70,
                    "rainfall_rate_mm_hr": 60.0,
                },
                "is_simulated": True,
            },
        ]
    }
    response = client.post("/api/v1/ingest/batch", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert len(data) == 2
    assert data[0]["event_type"] == "camera_frame_ping"
    assert data[1]["event_type"] == "water_proxy_reading"

def test_update_telemetry(client):
    """Test POST /api/v1/ingest/telemetry."""
    payload = {
        "bus_id": "GJ-06-BT-104",
        "lat": 22.3255,
        "lon": 73.1905,
        "speed": 34.2,
        "heading": 45.0,
        "crowd_count": 28,
        "capacity": 60,
        "is_simulated": True,
    }
    response = client.post("/api/v1/ingest/telemetry", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "updated"
    assert data["bus_id"] == "GJ-06-BT-104"
    assert data["occupancy_level"] == "medium"  # 28 / 60 = 0.46 -> medium

def test_scenario_trigger_and_simulation_tick(client):
    """Test POST /api/v1/simulate/scenario/{name} and POST /api/v1/simulate/tick."""
    # 1. Trigger monsoon flood scenario
    scen_resp = client.post("/api/v1/simulate/scenario/monsoon_flood", json={"intensity": 1.5})
    assert scen_resp.status_code == 200
    scen_data = scen_resp.json()
    assert scen_data["scenario_name"] == "monsoon_flood"
    assert scen_data["active"] is True

    # 2. Advance 1 tick
    tick_resp = client.post("/api/v1/simulate/tick")
    assert tick_resp.status_code == 200
    tick_data = tick_resp.json()
    assert tick_data["status"] == "tick_processed"
    assert tick_data["telemetry_count"] == 12
    assert tick_data["raw_events_count"] > 0
    assert tick_data["aqi_count"] == 12

def test_fleet_live_and_routes(client):
    """Test GET /api/v1/fleet/live and GET /api/v1/fleet/routes."""
    live_resp = client.get("/api/v1/fleet/live")
    assert live_resp.status_code == 200
    live_data = live_resp.json()
    assert len(live_data) >= 12

    routes_resp = client.get("/api/v1/fleet/routes")
    assert routes_resp.status_code == 200
    routes_data = routes_resp.json()
    assert len(routes_data) == 6
    route_ids = [r["route_id"] for r in routes_data]
    assert "ROUTE-101" in route_ids
    assert "ROUTE-103" in route_ids

def test_simulation_reset_endpoint(client):
    """Test POST /api/v1/simulate/reset."""
    resp = client.post("/api/v1/simulate/reset")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "reset_complete"
    assert data["new_simulation_run_id"].startswith("SIM-")
    assert data["active_buses_count"] == 12
