import json
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

class HazardResponse(BaseModel):
    id: int
    hazard_type: str
    lat: float
    lon: float
    severity: float
    waterlogging_severity: Optional[str] = None
    confidence: float
    confirmation_count: int
    distinct_bus_count: int = 1
    is_confirmed: bool
    status: str
    priority_score: float
    priority_explanation: Optional[Union[Dict[str, Any], str]] = None
    first_detected_at: datetime
    last_detected_at: datetime
    detected_by_buses: Union[List[str], str] = []
    sources: Union[List[str], str] = []
    address_hint: Optional[str] = None
    verification_passes: int = 0
    resolved_at: Optional[datetime] = None
    is_simulated: bool = True
    simulation_run_id: Optional[str] = None

    @field_validator("detected_by_buses", "sources", mode="before")
    @classmethod
    def parse_json_lists(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return [v] if v else []
        return v or []

    @field_validator("priority_explanation", mode="before")
    @classmethod
    def parse_explanation(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return v
        return v

    class Config:
        from_attributes = True

class HazardStatusUpdate(BaseModel):
    status: str = Field(..., description="New status: reported, confirmed, in_progress, resolved, ESCALATED_DISASTER")

class RepairPriorityResponse(BaseModel):
    hazard_id: int
    hazard_type: str
    lat: float
    lon: float
    severity: float
    confirmation_count: int
    is_confirmed: bool
    priority_score: float
    status: str
    first_detected_at: datetime
    last_detected_at: datetime
    hours_unresolved: float
    recommended_action: str

class EvidenceItemResponse(BaseModel):
    observation_id: int
    observation_type: str
    hazard_class: str
    confidence: float
    severity_score: float
    bus_id: str
    model_name: str
    model_version: str
    evidence_ref: Optional[str] = None
    bounding_box: Optional[Dict[str, Any]] = None
    signal_features: Optional[Dict[str, Any]] = None
    distance_to_centroid_meters: float
    timestamp: datetime
    raw_event_id: Optional[int] = None

class IncidentEvidenceResponse(BaseModel):
    incident_id: int
    hazard_type: str
    lat: float
    lon: float
    severity: float
    confidence: float
    is_confirmed: bool
    status: str
    priority_score: float
    priority_explanation: Optional[Dict[str, Any]] = None
    distinct_bus_count: int
    detected_by_buses: List[str]
    sources: List[str]
    observations_count: int
    evidence: List[EvidenceItemResponse]
