from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class WorkOrderCreate(BaseModel):
    incident_id: int
    title: Optional[str] = None
    department: str = Field(default="VMC Roads & Infrastructure")
    assigned_to: str = Field(default="Road Maintenance Team 3")
    priority: str = Field(default="HIGH")
    notes: Optional[str] = None

class WorkOrderStatusUpdate(BaseModel):
    status: str = Field(..., description="Status transition: ASSIGNED, IN_REPAIR, RESOLVED, VERIFIED")
    notes: Optional[str] = None

class WorkOrderResponse(BaseModel):
    id: int
    incident_id: int
    title: str
    department: str
    assigned_to: str
    location_hint: Optional[str] = None
    lat: float
    lon: float
    priority: str
    status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_simulated: bool
    simulation_run_id: Optional[str] = None

    class Config:
        from_attributes = True

class VerificationAuditResponse(BaseModel):
    id: int
    work_order_id: int
    incident_id: int
    bus_id: str
    verification_timestamp: datetime
    vibration_peak_g: float
    visual_defect_detected: bool
    verdict: str
    notes: Optional[str] = None

    class Config:
        from_attributes = True
