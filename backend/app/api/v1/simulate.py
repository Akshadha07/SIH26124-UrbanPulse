"""
Simulation Control Endpoints (/api/v1/simulate)
Handles starting scenarios, advancing simulation ticks, checking status,
and executing deterministic run resets with data isolation.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database import get_db
from app.schemas.simulate import (
    ScenarioTriggerRequest,
    ScenarioResponse,
    ResetResponse,
    SimulationStatusResponse,
)
from app.schemas.event import SensorEventCreate, TelemetryUpdateCreate
from app.simulator.engine import simulator_engine
from app.services.ingest_service import (
    execute_simulation_reset,
    update_bus_telemetry,
    ingest_raw_event,
)
from app.models.aqi import AQIReading

router = APIRouter(prefix="/simulate", tags=["Simulation"])

@router.post("/scenario/{name}", response_model=ScenarioResponse)
def trigger_scenario(name: str, payload: ScenarioTriggerRequest = ScenarioTriggerRequest()):
    """
    Trigger one of the approved deterministic scenarios:
    - monsoon_flood (flooding proxies at Akota Underpass)
    - pothole_cluster (vibration shocks along Alkapuri / Sayajigunj)
    - high_crowd_rush (passenger spike at Central Station)
    - sensor_failure (packet drop / blackout for Bus-107)
    """
    valid_scenarios = ["monsoon_flood", "pothole_cluster", "high_crowd_rush", "sensor_failure"]
    if name not in valid_scenarios:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid scenario '{name}'. Supported scenarios: {valid_scenarios}",
        )

    res = simulator_engine.set_scenario(name, intensity=payload.intensity)
    return ScenarioResponse(**res)

@router.post("/reset", response_model=ResetResponse)
def reset_simulation(db: Session = Depends(get_db)):
    """
    Reset simulator bus positions, speeds, clock, and active scenario state.
    Removes/archives simulated records for the active run_id while strictly
    preserving real/non-simulated records (is_simulated = False).
    Starts a fresh simulation run with a new simulation_run_id.
    """
    return execute_simulation_reset(db)

@router.post("/tick")
def advance_tick(db: Session = Depends(get_db)):
    """
    Manually advance the simulation by 1 step.
    Processes all 12 buses, saves live telemetry, and saves generated raw sensor events.
    """
    step_data = simulator_engine.step()

    # Ingest telemetry
    for t in step_data["telemetry"]:
        tel_in = TelemetryUpdateCreate(
            bus_id=t["bus_id"],
            lat=t["lat"],
            lon=t["lon"],
            speed=t["speed"],
            heading=t["heading"],
            crowd_count=t["crowd_count"],
            capacity=t["capacity"],
            occupancy_level=t["occupancy_level"],
            is_simulated=t["is_simulated"],
            simulation_run_id=t["simulation_run_id"],
        )
        update_bus_telemetry(db, tel_in)

    # Ingest raw sensor events
    for e in step_data["raw_events"]:
        evt_in = SensorEventCreate(
            bus_id=e["bus_id"],
            type=e["event_type"],
            lat=e["lat"],
            lon=e["lon"],
            timestamp=e["timestamp"],
            confidence=e["confidence"],
            value=e["value"],
            sensor_source=e["sensor_source"],
            raw_camera_ref=e.get("raw_camera_ref"),
            imu_window=e.get("imu_window"),
            water_proxy=e.get("water_proxy"),
            is_simulated=e["is_simulated"],
            simulation_run_id=e["simulation_run_id"],
        )
        ingest_raw_event(db, evt_in)

    # Ingest AQI readings
    for a in step_data["aqi_readings"]:
        aqi_rec = AQIReading(
            bus_id=a["bus_id"],
            lat=a["lat"],
            lon=a["lon"],
            pm2_5=a["pm2_5"],
            pm10=a["pm10"],
            co2=a["co2"],
            aqi_value=a["aqi_value"],
            category=a["category"],
            is_simulated=a["is_simulated"],
            simulation_run_id=a["simulation_run_id"],
            timestamp=a["timestamp"],
        )
        db.add(aqi_rec)
    db.commit()

    return {
        "status": "tick_processed",
        "tick": step_data["tick"],
        "simulation_run_id": step_data["simulation_run_id"],
        "telemetry_count": len(step_data["telemetry"]),
        "raw_events_count": len(step_data["raw_events"]),
        "aqi_count": len(step_data["aqi_readings"]),
    }

@router.get("/status", response_model=SimulationStatusResponse)
def get_simulation_status():
    """Retrieve current simulator status, run ID, and active scenario."""
    return SimulationStatusResponse(
        simulation_run_id=simulator_engine.simulation_run_id,
        is_running=simulator_engine.is_running,
        bus_count=len(simulator_engine.buses),
        interval_seconds=simulator_engine.interval_seconds,
        active_scenario=simulator_engine.active_scenario,
        seed=simulator_engine.seed,
        total_ticks=simulator_engine.tick_count,
    )
