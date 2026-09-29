"""
Tests for Phase 2A Vadodara Fleet Simulator Engine
Verifies:
- Fleet starts with 12 buses across 6 corridors.
- Deterministic seed produces reproducible results.
- GPS telemetry and raw sensor events are generated.
- is_simulated = True and simulation_run_id are present.
- NO simulator event contains AI conclusions (no 'pothole_detected', 'anomaly', 'severity=critical').
- Configurable emission timing.
- All approved scenarios activate correctly.
"""

import pytest
from app.simulator.engine import FleetSimulator
from app.simulator.routes import VADODARA_ROUTES

def test_simulator_fleet_initialization():
    """Verify simulator starts with exactly 12 buses across the 6 approved corridors."""
    sim = FleetSimulator(seed=100)
    assert len(sim.buses) == 12

    # Verify each route has 2 buses
    route_counts = {}
    for bus in sim.buses.values():
        route_counts[bus.route_id] = route_counts.get(bus.route_id, 0) + 1
        assert bus.is_active is True
        assert bus.speed > 0
        assert bus.capacity == 60

    assert len(route_counts) == 6
    for route_id, count in route_counts.items():
        assert count == 2, f"Route {route_id} should have 2 buses"
        assert route_id in VADODARA_ROUTES

def test_deterministic_seed_reproducibility():
    """Verify that using the same seed produces identical bus positions and sensor measurements."""
    sim1 = FleetSimulator(seed=42)
    step1_sim1 = sim1.step(delta_seconds=5.0)

    sim2 = FleetSimulator(seed=42)
    step1_sim2 = sim2.step(delta_seconds=5.0)

    for b1, b2 in zip(step1_sim1["telemetry"], step1_sim2["telemetry"]):
        assert b1["bus_id"] == b2["bus_id"]
        assert b1["lat"] == b2["lat"]
        assert b1["lon"] == b2["lon"]
        assert b1["heading"] == b2["heading"]
        assert b1["crowd_count"] == b2["crowd_count"]

    for e1, e2 in zip(step1_sim1["raw_events"], step1_sim2["raw_events"]):
        assert e1["bus_id"] == e2["bus_id"]
        assert e1["event_type"] == e2["event_type"]
        assert e1["value"] == e2["value"]

def test_raw_sensor_evidence_separation_no_ai_conclusions():
    """
    CRITICAL ARCHITECTURAL TEST:
    Verify simulator generates raw sensor evidence ONLY and does NOT output AI conclusions.
    """
    sim = FleetSimulator(seed=123)
    step_data = sim.step(delta_seconds=5.0)

    for event in step_data["raw_events"]:
        # Verify metadata
        assert event["is_simulated"] is True
        assert event["simulation_run_id"].startswith("SIM-")

        # Verify NO AI conclusions leaked into raw events
        assert "pothole_detected" not in event, "Simulator must not output pothole_detected"
        assert "anomaly" not in event, "Simulator must not output anomaly label"
        assert "is_anomaly" not in event
        assert "severity" not in event

        if event["event_type"] == "imu_stream_window":
            imu = event["imu_window"]
            assert "samples" in imu
            assert len(imu["samples"]) == 10  # 10 discrete samples
            assert "pothole_detected" not in imu
            assert "anomaly" not in imu

        if event["event_type"] == "water_proxy_reading":
            wp = event["water_proxy"]
            assert "water_reflection_index" in wp
            assert "wheel_drag_coefficient" in wp
            assert "rainfall_rate_mm_hr" in wp
            # Verify no severity label emitted
            assert "severity" not in wp
            assert "waterlogging_severity" not in wp

        if event["event_type"] == "camera_frame_ping":
            assert event.get("raw_camera_ref") is not None
            assert "pothole" not in event
            assert "ground_truth_defect" not in event

def test_configurable_emission_interval():
    """Verify emission interval is respected."""
    sim = FleetSimulator(seed=50, interval_seconds=10.0)
    assert sim.interval_seconds == 10.0
    step_data = sim.step()
    assert step_data["tick"] == 1
    assert len(step_data["telemetry"]) == 12

def test_all_scenarios_activation():
    """Verify all 4 approved scenarios can be triggered and adjust simulator parameters."""
    sim = FleetSimulator(seed=77)

    # 1. Monsoon Flood
    res = sim.set_scenario("monsoon_flood", intensity=1.5)
    assert res["active"] is True
    assert "Akota Underpass" in res["affected_corridors"]
    flood_step = sim.step(delta_seconds=5.0)
    water_events = [e for e in flood_step["raw_events"] if e["event_type"] == "water_proxy_reading"]
    assert len(water_events) > 0
    # Rainfall proxy should be elevated during monsoon scenario
    assert any(e["water_proxy"]["rainfall_rate_mm_hr"] > 30.0 for e in water_events)

    # 2. Pothole Cluster
    res = sim.set_scenario("pothole_cluster", intensity=2.0)
    assert res["active"] is True
    assert "Alkapuri" in res["affected_corridors"]

    # 3. High Crowd Rush
    res = sim.set_scenario("high_crowd_rush", intensity=1.5)
    assert res["active"] is True
    assert "Central Station" in res["affected_corridors"]

    # 4. Sensor Failure
    res = sim.set_scenario("sensor_failure")
    assert res["active"] is True
    assert "GJ-06-BT-107" in res["affected_corridors"]
    assert sim.buses["GJ-06-BT-107"].sensor_failure_active is True
    fail_step = sim.step(delta_seconds=5.0)
    # GJ-06-BT-107 should NOT emit sensor events during blackout
    bus_107_sensor_events = [e for e in fail_step["raw_events"] if e["bus_id"] == "GJ-06-BT-107"]
    assert len(bus_107_sensor_events) == 0
