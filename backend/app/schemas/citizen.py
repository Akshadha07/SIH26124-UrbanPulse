from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class CitizenNearbyHazardResponse(BaseModel):
    id: int
    hazard_type: str
    lat: float
    lon: float
    distance_meters: float
    severity: float
    confidence: float
    priority_score: float
    confirmation_count: int
    distinct_bus_count: int
    is_confirmed: bool
    status: str
    waterlogging_severity: Optional[str] = None
    address_hint: Optional[str] = None

class CitizenCrowdPredictionResponse(BaseModel):
    route_id: str
    route_name: str
    bus_id: Optional[str] = None
    current_occupancy_level: str  # low, moderate, high, full
    current_crowd_count: int
    capacity: int
    predicted_occupancy_level: str
    prediction_confidence: float
    trend: str  # INCREASING, STABLE, DECREASING
    eta_minutes: Optional[int] = None
    next_stop: Optional[str] = None

class CitizenReportCreate(BaseModel):
    category: str = Field(..., description="Hazard type: pothole, waterlogging, road_damage, garbage, street_light, other")
    lat: float = Field(..., ge=-90.0, le=90.0)
    lon: float = Field(..., ge=-180.0, le=180.0)
    description: Optional[str] = None
    photo_base64: Optional[str] = None
    photo_url: Optional[str] = None
    device_id_hash: Optional[str] = None

class CitizenReportResponse(BaseModel):
    id: int
    category: str
    lat: float
    lon: float
    description: Optional[str] = None
    photo_url: Optional[str] = None
    status: str  # SUBMITTED, UNDER_REVIEW, CONFIRMED, RESOLVED
    created_at: datetime

    class Config:
        from_attributes = True
