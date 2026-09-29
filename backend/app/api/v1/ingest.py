"""
Ingestion Endpoints (/api/v1/ingest)
Handles raw edge sensor events and live bus telemetry uploads.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.event import (
    SensorEventCreate,
    SensorEventResponse,
    TelemetryUpdateCreate,
    TelemetryResponse,
    BatchSensorEventsCreate,
)
from app.services.ingest_service import ingest_raw_event, ingest_batch_events, update_bus_telemetry

router = APIRouter(prefix="/ingest", tags=["Ingestion"])

@router.post("/event", response_model=SensorEventResponse, status_code=status.HTTP_201_CREATED)
def post_sensor_event(event: SensorEventCreate, db: Session = Depends(get_db)):
    """Ingest single raw sensor event (camera ping, IMU window, AQI, water proxy)."""
    return ingest_raw_event(db, event)

@router.post("/batch", response_model=List[SensorEventResponse], status_code=status.HTTP_201_CREATED)
def post_batch_events(batch: BatchSensorEventsCreate, db: Session = Depends(get_db)):
    """Ingest batched raw sensor events from bus uplink buffer."""
    return ingest_batch_events(db, batch.events)

@router.post("/telemetry", response_model=TelemetryResponse, status_code=status.HTTP_200_OK)
def post_telemetry(telemetry: TelemetryUpdateCreate, db: Session = Depends(get_db)):
    """Update live bus GPS, speed, bearing, and passenger occupancy."""
    return update_bus_telemetry(db, telemetry)
