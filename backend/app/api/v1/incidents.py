"""
Incidents Endpoints (/api/v1/incidents)
Provides access to city road defects, hazards, waterlogging alerts,
sensor fusion execution, and underlying AI evidence traces.
"""

import json
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.hazard import Hazard
from app.models.ai_observation import AIObservation, IncidentObservationLink
from app.schemas.hazard import (
    HazardResponse,
    HazardStatusUpdate,
    IncidentEvidenceResponse,
    EvidenceItemResponse,
)
from app.services.fusion_engine import fuse_pending_observations

router = APIRouter(prefix="/incidents", tags=["Incidents"])

@router.get("", response_model=List[HazardResponse])
@router.get("/", response_model=List[HazardResponse], include_in_schema=False)
def get_incidents(
    incident_type: Optional[str] = Query(None, description="Filter by hazard type (e.g. pothole, WATERLOGGING_CRITICAL)"),
    status: Optional[str] = Query(None, description="Filter by status (e.g. reported, confirmed, in_progress, resolved, ESCALATED_DISASTER)"),
    severity_min: Optional[float] = Query(None, ge=1.0, le=5.0, description="Minimum severity threshold"),
    priority_min: Optional[float] = Query(None, ge=0.0, le=100.0, description="Minimum dynamic priority score"),
    waterlogging_severity: Optional[str] = Query(None, description="Filter by waterlogging level: MINOR, MODERATE, SEVERE, CRITICAL"),
    is_simulated: Optional[bool] = Query(None, description="Filter by simulated vs real"),
    db: Session = Depends(get_db),
):
    """Retrieve city hazards and incidents with multi-attribute filtering sorted by priority."""
    query = db.query(Hazard)
    if incident_type:
        query = query.filter(Hazard.hazard_type == incident_type)
    if status:
        query = query.filter(Hazard.status == status)
    if severity_min is not None:
        query = query.filter(Hazard.severity >= severity_min)
    if priority_min is not None:
        query = query.filter(Hazard.priority_score >= priority_min)
    if waterlogging_severity:
        query = query.filter(Hazard.waterlogging_severity == waterlogging_severity)
    if is_simulated is not None:
        query = query.filter(Hazard.is_simulated == is_simulated)

    return query.order_by(Hazard.priority_score.desc()).all()

@router.get("/waterlogging-alerts", response_model=List[HazardResponse])
def get_waterlogging_alerts(db: Session = Depends(get_db)):
    """Convenience / read-optimized endpoint for Disaster Management Authority."""
    return db.query(Hazard).filter(
        (Hazard.hazard_type == "WATERLOGGING_CRITICAL") | 
        (Hazard.waterlogging_severity == "CRITICAL") |
        (Hazard.status == "ESCALATED_DISASTER")
    ).order_by(Hazard.priority_score.desc()).all()

@router.post("/fuse")
def run_fusion_cycle(
    simulation_run_id: Optional[str] = Query(None, description="Optional simulation run ID filter"),
    db: Session = Depends(get_db),
):
    """
    Trigger the AI Detection and Sensor Fusion cycle:
    1. Interprets unprocessed raw sensor events through AI models.
    2. Clusters observations spatio-temporally (35m radius).
    3. Fuses multi-modal / multi-bus evidence into canonical incidents.
    4. Computes dynamic priority scores and updates road health.
    """
    result = fuse_pending_observations(db, simulation_run_id=simulation_run_id)
    return result

@router.get("/{incident_id}/evidence", response_model=IncidentEvidenceResponse)
def get_incident_evidence(incident_id: int, db: Session = Depends(get_db)):
    """
    Retrieve underlying raw sensor evidence and AI detection observations
    linked to an incident for full auditability and explainability.
    """
    hazard = db.query(Hazard).filter(Hazard.id == incident_id).first()
    if not hazard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with ID {incident_id} not found",
        )

    observations = db.query(AIObservation).filter(AIObservation.incident_id == incident_id).all()
    links = {
        l.observation_id: l
        for l in db.query(IncidentObservationLink).filter(IncidentObservationLink.incident_id == incident_id).all()
    }

    evidence_items = []
    for obs in observations:
        link = links.get(obs.id)
        dist = link.distance_to_centroid_meters if link else 0.0

        bbox = None
        if obs.bounding_box:
            try:
                bbox = json.loads(obs.bounding_box)
            except Exception:
                bbox = None

        sig = None
        if obs.signal_features:
            try:
                sig = json.loads(obs.signal_features)
            except Exception:
                sig = None

        evidence_items.append(
            EvidenceItemResponse(
                observation_id=obs.id,
                observation_type=obs.observation_type,
                hazard_class=obs.hazard_class,
                confidence=obs.confidence,
                severity_score=obs.severity_score,
                bus_id=obs.bus_id,
                model_name=obs.model_name,
                model_version=obs.model_version,
                evidence_ref=obs.evidence_ref,
                bounding_box=bbox,
                signal_features=sig,
                distance_to_centroid_meters=dist,
                timestamp=obs.timestamp,
                raw_event_id=obs.raw_event_id,
            )
        )

    # Parse explanation
    explanation = None
    if hazard.priority_explanation:
        try:
            explanation = json.loads(hazard.priority_explanation)
        except Exception:
            explanation = {"raw": hazard.priority_explanation}

    # Parse buses and sources
    buses = []
    if hazard.detected_by_buses:
        try:
            buses = json.loads(hazard.detected_by_buses)
        except Exception:
            buses = [hazard.detected_by_buses]

    sources = []
    if hazard.sources:
        try:
            sources = json.loads(hazard.sources)
        except Exception:
            sources = [hazard.sources]

    return IncidentEvidenceResponse(
        incident_id=hazard.id,
        hazard_type=hazard.hazard_type,
        lat=hazard.lat,
        lon=hazard.lon,
        severity=hazard.severity,
        confidence=hazard.confidence,
        is_confirmed=hazard.is_confirmed,
        status=hazard.status,
        priority_score=hazard.priority_score,
        priority_explanation=explanation,
        distinct_bus_count=hazard.distinct_bus_count,
        detected_by_buses=buses,
        sources=sources,
        observations_count=len(evidence_items),
        evidence=evidence_items,
    )

@router.get("/{incident_id}", response_model=HazardResponse)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    """Retrieve details for a single incident."""
    hazard = db.query(Hazard).filter(Hazard.id == incident_id).first()
    if not hazard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with ID {incident_id} not found",
        )
    return hazard

@router.patch("/{incident_id}/status", response_model=HazardResponse)
def update_incident_status(incident_id: int, update_in: HazardStatusUpdate, db: Session = Depends(get_db)):
    """Transition status of an incident (reported, confirmed, in_progress, resolved, etc.)."""
    hazard = db.query(Hazard).filter(Hazard.id == incident_id).first()
    if not hazard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with ID {incident_id} not found",
        )

    hazard.status = update_in.status
    if update_in.status.lower() in ["resolved", "verified_closed"]:
        hazard.resolved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(hazard)
    return hazard
