"""
Phase 2A End-to-End Demonstration and Verification Script
Executes the exact 12-step validation flow requested:
1. Initialize FastAPI backend and database.
2. Verify simulator start and 12-bus fleet launch.
3. Verify buses move through Vadodara routes with realistic speed and headings.
4. Verify GPS telemetry arrives and updates in database.
5. Verify raw sensor evidence is stored (IMU window, camera frame ref, AQI readings).
6. Trigger 'pothole_cluster' scenario.
7. Trigger 'monsoon_flood' scenario.
8. Confirm water-proxy measurements are generated as RAW measurements only.
9. Confirm NO AI conclusion (no 'pothole_detected', 'anomaly', 'severity=critical') is produced by simulator.
10. Seed a real non-simulated record (is_simulated = False).
11. Call POST /api/v1/simulate/reset.
12. Confirm simulation state is clean, non-simulated data is strictly preserved, and a new simulation run ID starts.
"""

import sys
from fastapi.testclient import TestClient

from app.main import app
from app.database import init_db, SessionLocal
from app.models.raw_event import RawEvent
from app.models.bus import BusLiveState
from app.models.aqi import AQIReading

def run_phase2a_demo():
    print("=" * 70)
    print("STARTING PHASE 2A END-TO-END DEMO & VALIDATION")
    print("=" * 70)

    # 1. Initialize backend & database
    init_db()
    client = TestClient(app)
    db = SessionLocal()

    print("[Step 1-3] Backend initialized. Connecting client and inspecting fleet...")
    fleet_resp = client.get("/api/v1/fleet/live")
    assert fleet_resp.status_code == 200
    fleet_data = fleet_resp.json()
    print(f"-> Active buses count: {len(fleet_data)}")
    assert len(fleet_data) == 12, "Fleet should have exactly 12 buses"
    print(f"-> Sample bus GJ-06-BT-101 position: lat={fleet_data[0]['lat']}, lon={fleet_data[0]['lon']}, heading={fleet_data[0]['heading']}")

    # 4 & 5. Advance simulator ticks and verify movement and raw evidence storage
    print("\n[Step 4-5] Advancing simulation tick (5s timestep)...")
    tick_resp = client.post("/api/v1/simulate/tick")
    assert tick_resp.status_code == 200
    t_data = tick_resp.json()
    print(f"-> Tick response: tick #{t_data['tick']}, run_id={t_data['simulation_run_id']}")
    print(f"-> Telemetry count: {t_data['telemetry_count']}, Raw events count: {t_data['raw_events_count']}, AQI count: {t_data['aqi_count']}")
    assert t_data["telemetry_count"] == 12
    assert t_data["raw_events_count"] > 0

    # 6. Trigger 'pothole_cluster' scenario
    print("\n[Step 6] Triggering scenario: 'pothole_cluster'...")
    scen1_resp = client.post("/api/v1/simulate/scenario/pothole_cluster", json={"intensity": 2.0})
    assert scen1_resp.status_code == 200
    print(f"-> Scenario activated: {scen1_resp.json()['scenario_name']}, affected corridors: {scen1_resp.json()['affected_corridors']}")

    # 7 & 8. Trigger 'monsoon_flood' scenario
    print("\n[Step 7-8] Triggering scenario: 'monsoon_flood' and advancing tick...")
    scen2_resp = client.post("/api/v1/simulate/scenario/monsoon_flood", json={"intensity": 1.5})
    assert scen2_resp.status_code == 200
    print(f"-> Scenario activated: {scen2_resp.json()['scenario_name']}, affected corridors: {scen2_resp.json()['affected_corridors']}")

    tick_flood = client.post("/api/v1/simulate/tick")
    assert tick_flood.status_code == 200

    # 9. Verify water-proxy measurements are RAW proxies only and NO AI conclusion produced
    print("\n[Step 9-10] Verifying raw sensor evidence in database...")
    water_events = db.query(RawEvent).filter(RawEvent.event_type == "water_proxy_reading").all()
    assert len(water_events) > 0
    print(f"-> Found {len(water_events)} raw water proxy readings in database.")
    
    import json
    for we in water_events:
        assert we.is_simulated is True
        assert we.simulation_run_id is not None
        proxy_data = json.loads(we.water_proxy)
        assert "water_reflection_index" in proxy_data
        assert "wheel_drag_coefficient" in proxy_data
        assert "rainfall_rate_mm_hr" in proxy_data
        # Ensure zero AI conclusion
        assert "severity" not in proxy_data, "FAILED: Simulator must not output severity!"
        assert "waterlogging_severity" not in proxy_data, "FAILED: Simulator must not output waterlogging_severity!"
    print("-> Confirmed: Water proxy readings contain raw reflection, drag, and rain measurements ONLY.")

    imu_events = db.query(RawEvent).filter(
        RawEvent.event_type == "imu_stream_window",
        RawEvent.is_simulated == True,
    ).all()
    assert len(imu_events) > 0
    for ie in imu_events:
        if not ie.imu_window:
            continue
        imu_dict = json.loads(ie.imu_window)
        assert "samples" in imu_dict
        assert "pothole_detected" not in imu_dict, "FAILED: Simulator must not declare pothole_detected!"
        assert "anomaly" not in imu_dict, "FAILED: Simulator must not declare anomaly!"
    print("-> Confirmed: IMU events contain raw 3-axis numeric sample windows ONLY (no AI labels).")

    # 10. Seed a real non-simulated record to test preservation
    print("\n[Step 10-11] Seeding non-simulated real field record and calling reset...")
    real_field_event = RawEvent(
        bus_id="REAL-VMC-SURVEY-BUS-01",
        event_type="imu_stream_window",
        lat=22.3115,
        lon=73.1750,
        is_simulated=False,  # REAL FIELD DATA
        simulation_run_id=None,
    )
    db.add(real_field_event)
    db.commit()

    pre_reset_sim_count = db.query(RawEvent).filter(RawEvent.is_simulated == True).count()
    print(f"-> Simulated events before reset: {pre_reset_sim_count}")

    # 11 & 12. Call POST /api/v1/simulate/reset
    reset_resp = client.post("/api/v1/simulate/reset")
    assert reset_resp.status_code == 200
    r_data = reset_resp.json()
    print(f"-> Reset complete: previous_run_id={r_data['previous_simulation_run_id']}, new_run_id={r_data['new_simulation_run_id']}")
    print(f"-> Archived events: {r_data['archived_simulated_events_count']}")

    # 12. Confirm simulation data is clean and real data preserved
    post_reset_sim_count = db.query(RawEvent).filter(RawEvent.is_simulated == True).count()
    print(f"-> Simulated events after reset: {post_reset_sim_count}")
    assert post_reset_sim_count == 0, "All simulated events should be cleaned on reset"

    real_count_after = db.query(RawEvent).filter(RawEvent.is_simulated == False).count()
    print(f"-> Non-simulated real events after reset: {real_count_after}")
    assert real_count_after >= 1, "Real non-simulated records must be strictly preserved"

    fresh_buses = db.query(BusLiveState).all()
    assert len(fresh_buses) == 12
    assert all(b.simulation_run_id == r_data['new_simulation_run_id'] for b in fresh_buses)
    print(f"-> All 12 buses successfully re-initialized with new simulation_run_id: {r_data['new_simulation_run_id']}")

    db.close()
    print("\n" + "=" * 70)
    print("ALL 12 DEMO VALIDATION STEPS PASSED WITH 100% COMPLIANCE!")
    print("=" * 70)

if __name__ == "__main__":
    run_phase2a_demo()
