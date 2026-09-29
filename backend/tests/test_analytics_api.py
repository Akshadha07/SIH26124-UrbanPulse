import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_analytics_summary_endpoint():
    response = client.get("/api/v1/analytics/summary")
    assert response.status_code == 200
    data = response.json()
    assert "city" in data
    assert "Vadodara" in data["city"]
    assert "overall_road_health_index" in data
    assert "average_maintenance_risk" in data
    assert "total_sensor_nodes_monitored" in data
    assert data["total_sensor_nodes_monitored"] >= 12

def test_sensor_health_endpoint():
    response = client.get("/api/v1/analytics/sensor-health")
    assert response.status_code == 200
    data = response.json()
    assert "total_monitored_nodes" in data
    assert data["total_monitored_nodes"] >= 12
    assert "nodes" in data
    assert len(data["nodes"]) >= 12
    # Check first node structure
    first_node = data["nodes"][0]
    assert "bus_id" in first_node
    assert "status" in first_node
    assert first_node["status"] in ["ONLINE", "DEGRADED", "OFFLINE"]
    assert "sensors" in first_node
    assert "camera" in first_node["sensors"]
    assert "imu" in first_node["sensors"]
    assert "aqi" in first_node["sensors"]
    assert "water_proxy" in first_node["sensors"]
    assert first_node["is_simulated"] is True

def test_predictive_road_health_endpoint():
    response = client.get("/api/v1/analytics/predictive-road-health")
    assert response.status_code == 200
    data = response.json()
    assert "total_corridors_analyzed" in data
    assert data["total_corridors_analyzed"] == 6
    assert "segments" in data
    assert len(data["segments"]) == 6
    for seg in data["segments"]:
        assert "segment_code" in seg
        assert "predicted_risk_score" in seg
        assert 0.0 <= seg["predicted_risk_score"] <= 100.0
        assert "risk_level" in seg
        assert seg["risk_level"] in ["LOW", "MODERATE", "ELEVATED", "CRITICAL"]
        assert "data_sufficiency" in seg
        assert seg["data_sufficiency"] in [
            "SUFFICIENT",
            "LIMITED",
            "INSUFFICIENT_HISTORICAL_OBSERVATIONS",
        ]
        assert "recommended_action" in seg
        assert len(seg["recommended_action"]) > 0

def test_predictive_maintenance_endpoint():
    response = client.get("/api/v1/analytics/predictive-maintenance")
    assert response.status_code == 200
    data = response.json()
    assert "total_recommendations" in data
    assert "items" in data
    assert len(data["items"]) == 6
    for item in data["items"]:
        assert "segment_code" in item
        assert "risk_score" in item
        assert "urgency" in item
        assert item["urgency"] in ["ROUTINE", "PLANNED", "URGENT", "IMMEDIATE_DISPATCH"]
        assert "recommended_action" in item

def test_route_analytics_endpoint():
    response = client.get("/api/v1/analytics/routes")
    assert response.status_code == 200
    data = response.json()
    assert "total_routes" in data
    assert data["total_routes"] == 6
    assert "routes" in data
    assert len(data["routes"]) == 6
    for r in data["routes"]:
        assert "route_id" in r
        assert "route_name" in r
        assert "corridor_length_km" in r
        assert "hazard_density_per_km" in r
