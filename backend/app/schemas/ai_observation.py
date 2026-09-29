import json
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, Union
from datetime import datetime

class AIObservationCreate(BaseModel):
    bus_id: str
    raw_event_id: Optional[int] = None
    observation_type: str
    hazard_class: str
    confidence: float = 0.8
    severity_score: float = 2.0
    bounding_box: Optional[Union[Dict[str, Any], str]] = None
    signal_features: Optional[Union[Dict[str, Any], str]] = None
    model_name: str
    model_version: str = "1.0.0"
    evidence_ref: Optional[str] = None
    lat: float
    lon: float
    timestamp: Optional[datetime] = None
    is_simulated: bool = True
    simulation_run_id: Optional[str] = None

class AIObservationResponse(BaseModel):
    id: int
    raw_event_id: Optional[int] = None
    bus_id: str
    observation_type: str
    hazard_class: str
    confidence: float
    severity_score: float
    bounding_box: Optional[Union[Dict[str, Any], str]] = None
    signal_features: Optional[Union[Dict[str, Any], str]] = None
    model_name: str
    model_version: str
    evidence_ref: Optional[str] = None
    lat: float
    lon: float
    timestamp: datetime
    is_simulated: bool
    simulation_run_id: Optional[str] = None
    fusion_status: str
    incident_id: Optional[int] = None
    created_at: datetime

    @field_validator("bounding_box", "signal_features", mode="before")
    @classmethod
    def parse_json_dicts(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return v
        return v

    class Config:
        from_attributes = True
