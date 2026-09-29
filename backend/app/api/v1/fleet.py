"""
Fleet Transit Endpoints (/api/v1/fleet)
Provides live vehicle tracking, telemetry status, and Vadodara route geometry.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.bus import BusLiveState
from app.schemas.bus import BusLiveResponse, RouteResponse
from app.simulator.routes import get_all_routes, get_route

router = APIRouter(prefix="/fleet", tags=["Fleet"])

@router.get("/live", response_model=List[BusLiveResponse])
def get_live_fleet(db: Session = Depends(get_db)):
    """Retrieve current GPS, bearing, speed, and crowding for all active buses."""
    buses = db.query(BusLiveState).all()
    return buses

@router.get("/routes", response_model=List[RouteResponse])
def get_transit_routes():
    """Retrieve all Vadodara transit corridors with stops and polyline geometry."""
    return get_all_routes()

@router.get("/{bus_id}", response_model=BusLiveResponse)
def get_bus_telemetry(bus_id: str, db: Session = Depends(get_db)):
    """Retrieve live telemetry for a single bus."""
    bus = db.query(BusLiveState).filter(BusLiveState.bus_id == bus_id).first()
    if not bus:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bus with ID '{bus_id}' not found",
        )
    return bus
