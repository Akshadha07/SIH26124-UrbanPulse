"""
Integration Tests for Phase 2B Sensor Fusion and Priority Engine
Verifies:
- Spatio-temporal clustering within 35m radius
- Multi-modal cross-verification (Camera + IMU)
- Multi-bus confirmation (Bus 1 + Bus 2)
- Dynamic Priority Scorer explainable breakdown
- Waterlogging emergency escalation (ESCALATED_DISASTER)
- Road Health scoring (0-100)
- Endpoints: /api/v1/incidents/fuse, /api/v1/incidents/{id}/evidence, /api/v1/road-health
"""

import json
import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal, init_db
from app.models.raw_event import RawEvent
from app.models.ai_observation import AIObservation
from app.models.hazard import Hazard
from app.services.priority_scorer import calculate_priority_score
from app.services.fusion_engine import fuse_pending_observations
from app.services.road_health_service import calculate_all_road_health

@pytest.fixture(scope="module")
def client():
    init_db()
    with TestClient(app) as c:
        yield c

def test_priority_scorer_deterministic_explainability():
    """Verify priority score formula components and transparent rationale."""
    score, explanation = calculate_priority_score(
        severity=4.5,
        confidence=0.92,
        distinct_bus_count=2,
        sensor_sources=["camera", "imu"],
        hazard_type="pothole",
    )
    # Severity (4.5/5.0 * 30 = 27.0)
    # Confidence (0.92 * 20 = 18.4)
    # Multi-bus (2 * 12.5 = 25.0)
    # Multi-sensor camera+imu (15.0)
    # Total = 27.0 + 18.4 + 25.0 + 15.0 = 85.4
    assert score >= 80.0
    assert "breakdown" in explanation
    assert explanation["breakdown"]["severity_component"] == 27.0
    assert explanation["breakdown"]["multi_bus_component"] == 25.0
    assert explanation["breakdown"]["multi_sensor_component"] == 15.0
    assert "Corroborated by 2 independent buses" in explanation["rationale"]
    assert "Cross-verified by camera defect detection and IMU shockwave" in explanation["rationale"]

def test_waterlogging_critical_emergency_priority():
    """Verify critical flood conditions guarantee priority score >= 95.0 and emergency rationale."""
    score, explanation = calculate_priority_score(
        severity=5.0,
        confidence=0.95,
        distinct_bus_count=1,
        sensor_sources=["water_sensor"],
        hazard_type="WATERLOGGING_CRITICAL",
        waterlogging_severity="CRITICAL",
    )
    assert score >= 95.0
    assert explanation["breakdown"]["waterlogging_bonus"] == 25.0
    assert "EMERGENCY: Critical waterlogging detected" in explanation["rationale"]

def test_multi_modal_sensor_fusion_cam_plus_imu():
    """Verify camera observation + IMU anomaly at same location (< 35m) fuses into confirmed incident."""
    db = SessionLocal()
    test_run_id = "TEST-FUSION-CAM-IMU-01"
    try:
        # Clear existing test hazards with this run_id
        db.query(Hazard).filter(Hazard.simulation_run_id == test_run_id).delete()
        db.query(AIObservation).filter(AIObservation.simulation_run_id == test_run_id).delete()
        db.commit()

        # Observation 1: Camera detection from Bus 101 at Alkapuri
        obs_cam = AIObservation(
            bus_id="GJ-06-BT-101",
            observation_type="ROAD_HAZARD_CV",
            hazard_class="pothole",
            confidence=0.86,
            severity_score=3.8,
            bounding_box=json.dumps({"ymin": 0.58, "xmin": 0.42, "ymax": 0.74, "xmax": 0.61}),
            model_name="road_hazard_prototype_v1",
            model_version="1.0.0",
            lat=22.31180,
            lon=73.17200,
            is_simulated=True,
            simulation_run_id=test_run_id,
            fusion_status="pending",
        )
        db.add(obs_cam)

        # Observation 2: IMU shockwave from Bus 101 at Alkapuri (12m away)
        obs_imu = AIObservation(
            bus_id="GJ-06-BT-101",
            observation_type="IMU_ANOMALY",
            hazard_class="pothole",
            confidence=0.91,
            severity_score=4.2,
            signal_features=json.dumps({"peak_z_g": 2.45, "peak_z_ms2": 24.0}),
            model_name="imu_statistical_v1",
            model_version="1.0.0",
            lat=22.31188,  # ~10m delta
            lon=73.17205,
            is_simulated=True,
            simulation_run_id=test_run_id,
            fusion_status="pending",
        )
        db.add(obs_imu)
        db.commit()

        # Execute fusion cycle
        result = fuse_pending_observations(db, simulation_run_id=test_run_id)
        assert result["status"] == "fusion_cycle_complete"
        assert result["processed_observations_count"] >= 2

        # Verify fused incident in DB
        fused = db.query(Hazard).filter(
            Hazard.simulation_run_id == test_run_id,
            Hazard.hazard_type == "pothole",
        ).first()

        assert fused is not None
        assert fused.is_confirmed is True, "Incident should be confirmed by multi-modal Camera+IMU agreement"
        assert fused.status == "confirmed"
        sources = json.loads(fused.sources)
        assert "camera" in sources
        assert "imu" in sources
        assert fused.priority_score >= 50.0

    finally:
        db.close()

def test_multi_bus_corroboration():
    """Verify two independent buses reporting within 35m corroborate defect."""
    db = SessionLocal()
    test_run_id = "TEST-FUSION-MULTIBUS-02"
    try:
        db.query(Hazard).filter(Hazard.simulation_run_id == test_run_id).delete()
        db.query(AIObservation).filter(AIObservation.simulation_run_id == test_run_id).delete()
        db.commit()

        # Bus 103 report at Sayajigunj
        obs1 = AIObservation(
            bus_id="GJ-06-BT-103",
            observation_type="IMU_ANOMALY",
            hazard_class="pothole",
            confidence=0.82,
            severity_score=3.5,
            lat=22.31420,
            lon=73.18650,
            is_simulated=True,
            simulation_run_id=test_run_id,
            fusion_status="pending",
            model_name="imu_statistical_v1",
        )
        db.add(obs1)
        db.commit()

        # Run first fusion: single bus -> reported
        fuse_pending_observations(db, simulation_run_id=test_run_id)
        h1 = db.query(Hazard).filter(Hazard.simulation_run_id == test_run_id).first()
        assert h1 is not None
        assert h1.distinct_bus_count == 1
        assert h1.is_confirmed is False
        assert h1.status == "reported"

        # Bus 104 traverses the same pothole 5 minutes later (15m away)
        obs2 = AIObservation(
            bus_id="GJ-06-BT-104",
            observation_type="IMU_ANOMALY",
            hazard_class="pothole",
            confidence=0.88,
            severity_score=3.7,
            lat=22.31428,
            lon=73.18658,
            is_simulated=True,
            simulation_run_id=test_run_id,
            fusion_status="pending",
            model_name="imu_statistical_v1",
        )
        db.add(obs2)
        db.commit()

        # Run second fusion: 2nd bus -> corroborates!
        fuse_pending_observations(db, simulation_run_id=test_run_id)
        h_updated = db.query(Hazard).filter(Hazard.id == h1.id).first()
        assert h_updated.distinct_bus_count == 2
        assert h_updated.is_confirmed is True
        assert h_updated.status == "confirmed"
        buses = json.loads(h_updated.detected_by_buses)
        assert "GJ-06-BT-103" in buses
        assert "GJ-06-BT-104" in buses

    finally:
        db.close()

def test_waterlogging_disaster_fast_path():
    """Verify waterlogging critical observation triggers ESCALATED_DISASTER status."""
    db = SessionLocal()
    test_run_id = "TEST-WATERLOGGING-03"
    try:
        db.query(Hazard).filter(Hazard.simulation_run_id == test_run_id).delete()
        db.query(AIObservation).filter(AIObservation.simulation_run_id == test_run_id).delete()
        db.commit()

        obs_flood = AIObservation(
            bus_id="GJ-06-BT-105",
            observation_type="WATERLOGGING_SEVERITY",
            hazard_class="WATERLOGGING_CRITICAL",
            confidence=0.96,
            severity_score=5.0,
            signal_features=json.dumps({"water_reflection_index": 0.91, "wheel_drag_coefficient": 0.85, "waterlogging_severity": "CRITICAL"}),
            lat=22.2965,
            lon=73.1750,
            is_simulated=True,
            simulation_run_id=test_run_id,
            fusion_status="pending",
            model_name="waterlogging_rules_v1",
        )
        db.add(obs_flood)
        db.commit()

        result = fuse_pending_observations(db, simulation_run_id=test_run_id)
        assert result["escalated_disasters_count"] >= 1

        flood_hazard = db.query(Hazard).filter(
            Hazard.simulation_run_id == test_run_id,
            Hazard.hazard_type == "WATERLOGGING_CRITICAL",
        ).first()

        assert flood_hazard is not None
        assert flood_hazard.status == "ESCALATED_DISASTER"
        assert flood_hazard.waterlogging_severity == "CRITICAL"
        assert flood_hazard.priority_score >= 95.0

    finally:
        db.close()

def test_road_health_calculation_service():
    """Verify Road Health scores are computed across Vadodara corridor segments."""
    db = SessionLocal()
    try:
        scores = calculate_all_road_health(db)
        assert len(scores) == 6
        for s in scores:
            assert "segment_code" in s
            assert "health_score" in s
            assert 0.0 <= s["health_score"] <= 100.0
            assert "roughness_index" in s
            assert s["roughness_index"] >= 1.0
            assert s["rating"] in ["Good", "Fair", "Poor", "Critical"]
    finally:
        db.close()

def test_fusion_and_evidence_api_endpoints(client):
    """Test POST /api/v1/incidents/fuse and GET /api/v1/incidents/{id}/evidence."""
    # 1. Trigger fusion cycle
    fuse_resp = client.post("/api/v1/incidents/fuse")
    assert fuse_resp.status_code == 200
    fuse_data = fuse_resp.json()
    assert "status" in fuse_data
    assert fuse_data["status"] == "fusion_cycle_complete"

    # 2. Get active incidents
    incidents_resp = client.get("/api/v1/incidents")
    assert incidents_resp.status_code == 200
    incidents = incidents_resp.json()

    if incidents:
        target_id = incidents[0]["id"]
        # 3. Retrieve evidence audit trace
        evidence_resp = client.get(f"/api/v1/incidents/{target_id}/evidence")
        assert evidence_resp.status_code == 200
        ev_data = evidence_resp.json()
        assert ev_data["incident_id"] == target_id
        assert "evidence" in ev_data
        assert "observations_count" in ev_data

def test_road_health_api_endpoints(client):
    """Test GET and POST /api/v1/road-health endpoints."""
    # GET road health overview
    get_resp = client.get("/api/v1/road-health")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["city"] == "Vadodara, Gujarat"
    assert "overall_city_index" in data
    assert len(data["segments"]) == 6

    # POST recalculate road health
    calc_resp = client.post("/api/v1/road-health/calculate")
    assert calc_resp.status_code == 200
    calc_data = calc_resp.json()
    assert len(calc_data["segments"]) == 6
