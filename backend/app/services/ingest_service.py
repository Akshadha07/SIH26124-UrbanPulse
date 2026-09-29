"""
Ingestion Service for Phase 2A
Handles storing raw sensor events, bus telemetry updates, batch ingestion,
and executing simulation run resets with data isolation.
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import delete

from app.models.raw_event import RawEvent
from app.models.bus import BusLiveState, Bus
from app.models.hazard import Hazard
from app.models.aqi import AQIReading
from app.models.ai_observation import AIObservation, IncidentObservationLink
from app.models.road_health import RoadHealthScore
from app.models.work_order import WorkOrder, VerificationAudit
from app.schemas.event import SensorEventCreate, SensorEventResponse, TelemetryUpdateCreate, TelemetryResponse
from app.schemas.simulate import ResetResponse
from app.simulator.engine import simulator_engine
from app.simulator.routes import VADODARA_ROUTES

def serialize_json_field(val: Any) -> Optional[str]:
    if val is None:
        return None
    if isinstance(val, (dict, list)):
        return json.dumps(val)
    return str(val)

def ingest_raw_event(db: Session, event_in: SensorEventCreate) -> SensorEventResponse:
    """Store raw sensor event evidence."""
    imu_json = serialize_json_field(event_in.imu_window)
    water_json = serialize_json_field(event_in.water_proxy)
    meta_json = serialize_json_field(event_in.extra_metadata)

    raw_event = RawEvent(
        bus_id=event_in.bus_id,
        event_type=event_in.type,
        lat=event_in.lat,
        lon=event_in.lon,
        timestamp=event_in.timestamp or datetime.now(timezone.utc),
        confidence=event_in.confidence or 1.0,
        value=event_in.value or 0.0,
        sensor_source=event_in.sensor_source or "sensor",
        raw_camera_ref=event_in.raw_camera_ref,
        imu_window=imu_json,
        water_proxy=water_json,
        extra_metadata=meta_json,
        is_simulated=event_in.is_simulated,
        simulation_run_id=event_in.simulation_run_id or simulator_engine.simulation_run_id,
    )
    db.add(raw_event)
    db.commit()
    db.refresh(raw_event)

    return SensorEventResponse(
        status="ingested",
        raw_event_id=raw_event.id,
        bus_id=raw_event.bus_id,
        event_type=raw_event.event_type,
        is_simulated=raw_event.is_simulated,
        simulation_run_id=raw_event.simulation_run_id,
        message="Raw sensor event ingested successfully",
    )

def ingest_batch_events(db: Session, events: List[SensorEventCreate]) -> List[SensorEventResponse]:
    """Store a batch of raw sensor events."""
    responses: List[SensorEventResponse] = []
    for evt in events:
        responses.append(ingest_raw_event(db, evt))
    return responses

def update_bus_telemetry(db: Session, telemetry_in: TelemetryUpdateCreate) -> TelemetryResponse:
    """Upsert bus live GPS telemetry state."""
    bus_state = db.query(BusLiveState).filter(BusLiveState.bus_id == telemetry_in.bus_id).first()
    
    # Infer occupancy level if not provided
    occupancy = telemetry_in.occupancy_level
    if not occupancy:
        ratio = telemetry_in.crowd_count / float(max(1, telemetry_in.capacity))
        if ratio < 0.35:
            occupancy = "low"
        elif ratio < 0.70:
            occupancy = "medium"
        elif ratio < 0.90:
            occupancy = "high"
        else:
            occupancy = "full"

    if not bus_state:
        bus_state = BusLiveState(
            bus_id=telemetry_in.bus_id,
            lat=telemetry_in.lat,
            lon=telemetry_in.lon,
            speed=telemetry_in.speed,
            heading=telemetry_in.heading,
            crowd_count=telemetry_in.crowd_count,
            capacity=telemetry_in.capacity,
            occupancy_level=occupancy,
            is_simulated=telemetry_in.is_simulated,
            simulation_run_id=telemetry_in.simulation_run_id or simulator_engine.simulation_run_id,
            last_updated=datetime.now(timezone.utc),
        )
        db.add(bus_state)
    else:
        bus_state.lat = telemetry_in.lat
        bus_state.lon = telemetry_in.lon
        bus_state.speed = telemetry_in.speed
        bus_state.heading = telemetry_in.heading
        bus_state.crowd_count = telemetry_in.crowd_count
        bus_state.capacity = telemetry_in.capacity
        bus_state.occupancy_level = occupancy
        bus_state.is_simulated = telemetry_in.is_simulated
        bus_state.simulation_run_id = telemetry_in.simulation_run_id or simulator_engine.simulation_run_id
        bus_state.last_updated = datetime.now(timezone.utc)

    db.commit()

    return TelemetryResponse(
        status="updated",
        bus_id=bus_state.bus_id,
        lat=bus_state.lat,
        lon=bus_state.lon,
        speed=bus_state.speed,
        heading=bus_state.heading,
        crowd_count=bus_state.crowd_count,
        occupancy_level=bus_state.occupancy_level,
        is_simulated=bus_state.is_simulated,
        simulation_run_id=bus_state.simulation_run_id,
        message="Bus telemetry updated successfully",
    )

def execute_simulation_reset(db: Session) -> ResetResponse:
    """
    Performs clean simulation run isolation and reset:
    1. Resets simulator bus positions/state & clock.
    2. Removes or archives simulated records associated with the active simulation_run_id (or is_simulated=True).
    3. Strictly preserves real/non-simulated records (is_simulated=False).
    4. Starts a fresh simulation run with a new simulation_run_id.
    """
    reset_info = simulator_engine.reset()
    prev_run_id = reset_info["previous_simulation_run_id"]
    new_run_id = reset_info["new_simulation_run_id"]

    # Delete simulated raw events
    del_events = db.query(RawEvent).filter(
        RawEvent.is_simulated == True
    ).delete(synchronize_session=False)

    # Delete simulated AQI readings
    db.query(AQIReading).filter(
        AQIReading.is_simulated == True
    ).delete(synchronize_session=False)

    # Delete simulated hazards/incidents
    db.query(Hazard).filter(
        Hazard.is_simulated == True
    ).delete(synchronize_session=False)

    # Delete simulated AI observations and links
    db.query(AIObservation).filter(
        AIObservation.is_simulated == True
    ).delete(synchronize_session=False)
    db.query(IncidentObservationLink).delete(synchronize_session=False)

    # Delete simulated road health scores
    db.query(RoadHealthScore).filter(
        RoadHealthScore.is_simulated == True
    ).delete(synchronize_session=False)

    # Delete simulated work orders and audits
    db.query(WorkOrder).filter(
        WorkOrder.is_simulated == True
    ).delete(synchronize_session=False)
    db.query(VerificationAudit).delete(synchronize_session=False)

    # Reset simulated bus live states to new initial positions
    del_telemetry = db.query(BusLiveState).filter(
        BusLiveState.is_simulated == True
    ).delete(synchronize_session=False)

    db.commit()

    # Re-seed fresh bus live states for all 12 simulator buses
    for bus_id, sim_bus in simulator_engine.buses.items():
        fresh_state = BusLiveState(
            bus_id=bus_id,
            route_id=sim_bus.route_id,
            route_name=sim_bus.route_data["route_name"],
            lat=sim_bus.lat,
            lon=sim_bus.lon,
            speed=sim_bus.speed,
            heading=sim_bus.heading,
            crowd_count=sim_bus.crowd_count,
            capacity=sim_bus.capacity,
            occupancy_level="low",
            is_simulated=True,
            simulation_run_id=new_run_id,
            last_updated=datetime.now(timezone.utc),
        )
        db.add(fresh_state)
    db.commit()

    return ResetResponse(
        status="reset_complete",
        previous_simulation_run_id=prev_run_id,
        new_simulation_run_id=new_run_id,
        archived_simulated_events_count=del_events,
        archived_simulated_telemetry_count=del_telemetry,
        active_buses_count=len(simulator_engine.buses),
        message="Simulation environment reset successfully. Non-simulated records preserved.",
    )
