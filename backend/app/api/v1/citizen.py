import math
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.hazard import Hazard
from app.models.bus import BusLiveState
from app.models.citizen_report import CitizenReport
from app.schemas.citizen import (
    CitizenNearbyHazardResponse,
    CitizenCrowdPredictionResponse,
    CitizenReportCreate,
    CitizenReportResponse,
)
from app.simulator.routes import VADODARA_ROUTES
from app.simulator.engine import simulator_engine
from app.services.fusion_engine import broadcast_event_safe

router = APIRouter(prefix="/citizen", tags=["Citizen Mobile Experience"])

def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Compute Haversine distance in meters between two coordinates."""
    r = 6371000.0  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = (math.sin(d_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r * c

@router.get("/hazards/nearby", response_model=List[CitizenNearbyHazardResponse])
def get_nearby_hazards(
    lat: float = Query(22.3072, ge=-90.0, le=90.0, description="Citizen current latitude"),
    lon: float = Query(73.1812, ge=-180.0, le=180.0, description="Citizen current longitude"),
    radius_meters: float = Query(3000.0, ge=50.0, le=25000.0, description="Search radius in meters"),
    min_priority: float = Query(0.0, ge=0.0, le=100.0, description="Minimum priority score"),
    db: Session = Depends(get_db),
):
    """
    Retrieve active road defects and flood hazards near the commuter's current or selected position.
    Calculates distance in meters and returns clean citizen-facing details.
    """
    hazards = db.query(Hazard).filter(
        Hazard.status.notin_(["resolved", "verified_closed"])
    ).all()

    results = []
    for h in hazards:
        dist = haversine_distance_meters(lat, lon, h.lat, h.lon)
        if dist <= radius_meters and (h.priority_score >= min_priority):
            results.append(
                CitizenNearbyHazardResponse(
                    id=h.id,
                    hazard_type=h.hazard_type,
                    lat=h.lat,
                    lon=h.lon,
                    distance_meters=round(dist, 1),
                    severity=h.severity,
                    confidence=h.confidence,
                    priority_score=h.priority_score,
                    confirmation_count=h.confirmation_count,
                    distinct_bus_count=h.distinct_bus_count,
                    is_confirmed=h.is_confirmed,
                    status=h.status,
                    waterlogging_severity=h.waterlogging_severity,
                    address_hint=h.address_hint,
                )
            )

    # Sort by proximity first, then priority
    results.sort(key=lambda x: (x.distance_meters, -x.priority_score))
    return results

@router.get("/bus/crowd-prediction", response_model=List[CitizenCrowdPredictionResponse])
def get_bus_crowd_prediction(
    route_id: Optional[str] = Query(None, description="Optional route filter e.g. ROUTE-101"),
    bus_id: Optional[str] = Query(None, description="Optional bus ID filter"),
    db: Session = Depends(get_db),
):
    """
    Retrieve live bus occupancy and deterministic commuter crowding predictions along Vadodara corridors.
    """
    query = db.query(BusLiveState)
    if bus_id:
        query = query.filter(BusLiveState.bus_id == bus_id)
    if route_id:
        query = query.filter(BusLiveState.route_id == route_id)

    buses = query.all()
    predictions = []

    # Check if high crowd rush scenario is active
    is_rush = simulator_engine.active_scenario == "high_crowd_rush"

    for b in buses:
        # Determine next stop and estimated arrival
        route_meta = VADODARA_ROUTES.get(b.route_id, {})
        stops = route_meta.get("stops", [])
        next_stop_name = stops[0]["stop_name"] if stops else "Central Corridor"

        # Calculate estimated arrival in minutes
        speed = max(15.0, b.speed)
        eta_min = max(2, min(15, int(15.0 / (speed / 10.0))))

        # Predicted occupancy
        pred_level = b.occupancy_level
        trend = "STABLE"
        if is_rush:
            pred_level = "high" if b.occupancy_level in ["low", "medium"] else "full"
            trend = "INCREASING"

        predictions.append(
            CitizenCrowdPredictionResponse(
                route_id=b.route_id,
                route_name=b.route_name,
                bus_id=b.bus_id,
                current_occupancy_level=b.occupancy_level,
                current_crowd_count=b.crowd_count,
                capacity=b.capacity,
                predicted_occupancy_level=pred_level,
                prediction_confidence=0.88 if is_rush else 0.94,
                trend=trend,
                eta_minutes=eta_min,
                next_stop=next_stop_name,
            )
        )

    return predictions

@router.post("/report", response_model=CitizenReportResponse, status_code=status.HTTP_201_CREATED)
def submit_citizen_report(
    payload: CitizenReportCreate,
    db: Session = Depends(get_db),
):
    """
    Submit a citizen road or infrastructure report with GPS coordinates and optional photo reference.
    Stores report and alerts VMC control center via real-time WebSocket.
    """
    photo_path = payload.photo_url
    if payload.photo_base64 and not photo_path:
        photo_path = "/assets/citizen_reports/report_sample.jpg"

    report = CitizenReport(
        category=payload.category.lower(),
        lat=payload.lat,
        lon=payload.lon,
        description=payload.description,
        photo_url=photo_path,
        device_id_hash=payload.device_id_hash,
        status="SUBMITTED",
        created_at=datetime.now(timezone.utc),
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    broadcast_event_safe("citizen_report_created", {
        "report_id": report.id,
        "category": report.category,
        "lat": report.lat,
        "lon": report.lon,
        "timestamp": report.created_at.isoformat(),
    })

    return report

@router.get("/reports", response_model=List[CitizenReportResponse])
def get_citizen_reports(
    device_id_hash: Optional[str] = Query(None, description="Optional device ID hash filter for My Reports"),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Retrieve submitted reports for citizen history tracking."""
    query = db.query(CitizenReport)
    if device_id_hash:
        query = query.filter(CitizenReport.device_id_hash == device_id_hash)
    return query.order_by(CitizenReport.created_at.desc()).limit(limit).all()
