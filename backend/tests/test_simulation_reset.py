"""
Tests for Phase 2A Simulation Run Isolation and Reset
Verifies:
- POST /api/v1/simulate/reset creates a fresh simulation_run_id.
- Cleans/archives simulated records.
- Strictly PRESERVES real/non-simulated records (is_simulated = False).
- Re-seeds 12 buses into initial state with new run ID.
"""

import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.raw_event import RawEvent
from app.models.bus import BusLiveState
from app.models.hazard import Hazard
from app.models.aqi import AQIReading
from app.services.ingest_service import execute_simulation_reset
from app.simulator.engine import simulator_engine

@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_simulation_reset_data_isolation(test_db):
    """
    Verify reset removes simulated data for active run while preserving non-simulated data.
    """
    initial_run_id = simulator_engine.simulation_run_id

    # 1. Seed simulated raw event
    sim_event = RawEvent(
        bus_id="GJ-06-BT-101",
        event_type="imu_stream_window",
        lat=22.3108,
        lon=73.1812,
        is_simulated=True,
        simulation_run_id=initial_run_id,
    )
    test_db.add(sim_event)

    # 2. Seed NON-SIMULATED (real/field test) raw event
    real_event = RawEvent(
        bus_id="FIELD-TEST-BUS-01",
        event_type="imu_stream_window",
        lat=22.3115,
        lon=73.1750,
        is_simulated=False,  # REAL DATA
        simulation_run_id=None,
    )
    test_db.add(real_event)

    # 3. Seed simulated AQI reading
    sim_aqi = AQIReading(
        bus_id="GJ-06-BT-101",
        lat=22.3108,
        lon=73.1812,
        pm2_5=85.0,
        aqi_value=85.0,
        category="Moderate",
        is_simulated=True,
        simulation_run_id=initial_run_id,
    )
    test_db.add(sim_aqi)

    # 4. Seed NON-SIMULATED real AQI reading
    real_aqi = AQIReading(
        bus_id="CPCB-STATION-01",
        lat=22.3120,
        lon=73.1740,
        pm2_5=62.0,
        aqi_value=62.0,
        category="Satisfactory",
        is_simulated=False,  # REAL DATA
        simulation_run_id=None,
    )
    test_db.add(real_aqi)

    test_db.commit()

    # Pre-reset sanity check
    assert test_db.query(RawEvent).count() == 2
    assert test_db.query(AQIReading).count() == 2

    # 5. Execute Simulation Reset
    res = execute_simulation_reset(test_db)

    assert res.status == "reset_complete"
    assert res.previous_simulation_run_id == initial_run_id
    assert res.new_simulation_run_id != initial_run_id
    assert res.new_simulation_run_id.startswith("SIM-")
    assert res.active_buses_count == 12

    # 6. Verify Simulated Data Removed
    sim_events_remaining = test_db.query(RawEvent).filter(RawEvent.is_simulated == True).all()
    assert len(sim_events_remaining) == 0

    sim_aqi_remaining = test_db.query(AQIReading).filter(AQIReading.is_simulated == True).all()
    assert len(sim_aqi_remaining) == 0

    # 7. CRITICAL: Verify Non-Simulated Real Data Intact!
    real_events_remaining = test_db.query(RawEvent).filter(RawEvent.is_simulated == False).all()
    assert len(real_events_remaining) == 1
    assert real_events_remaining[0].bus_id == "FIELD-TEST-BUS-01"

    real_aqi_remaining = test_db.query(AQIReading).filter(AQIReading.is_simulated == False).all()
    assert len(real_aqi_remaining) == 1
    assert real_aqi_remaining[0].bus_id == "CPCB-STATION-01"

    # 8. Verify all 12 buses re-seeded in fresh state
    live_buses = test_db.query(BusLiveState).all()
    assert len(live_buses) == 12
    for b in live_buses:
        assert b.is_simulated is True
        assert b.simulation_run_id == res.new_simulation_run_id
