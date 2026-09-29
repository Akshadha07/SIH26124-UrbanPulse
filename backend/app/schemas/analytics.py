from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class RoadRiskSignal(BaseModel):
    signal_type: str
    weight: float
    description: str
    observation_count: int

class PredictiveRoadHealthSegment(BaseModel):
    segment_code: str
    corridor_name: str
    health_score: float
    predicted_risk_score: float = Field(..., ge=0.0, le=100.0, description="Predictive risk score (0=pristine, 100=critical breakdown)")
    risk_level: str = Field(..., description="LOW, MODERATE, ELEVATED, CRITICAL")
    deterioration_trend: str = Field(..., description="STABLE, DEGRADING, RAPID_DETERIORATION, INSUFFICIENT_DATA")
    data_sufficiency: str = Field(..., description="SUFFICIENT, LIMITED, INSUFFICIENT_HISTORICAL_OBSERVATIONS")
    total_historical_events: int
    unresolved_incidents: int
    confirmed_defects: int
    waterlogging_events: int
    risk_drivers: List[str]
    recommended_action: str
    confidence_score: float

class PredictiveRoadHealthResponse(BaseModel):
    city: str = "Vadodara, Gujarat"
    generated_at: datetime
    total_corridors_analyzed: int
    high_risk_segments_count: int
    methodology_note: str
    segments: List[PredictiveRoadHealthSegment]

class MaintenanceRiskItem(BaseModel):
    segment_code: str
    corridor_name: str
    priority_rank: int
    risk_score: float
    urgency: str = Field(..., description="ROUTINE, PLANNED, URGENT, IMMEDIATE_DISPATCH")
    primary_defect_type: str
    drivers: List[str]
    recommended_action: str
    estimated_work_type: str
    last_repair_verified_at: Optional[datetime] = None

class PredictiveMaintenanceResponse(BaseModel):
    city: str = "Vadodara, Gujarat"
    generated_at: datetime
    total_recommendations: int
    items: List[MaintenanceRiskItem]

class RouteAnalyticsItem(BaseModel):
    route_id: str
    route_name: str
    total_buses_assigned: int
    active_buses: int
    corridor_length_km: float
    incident_count: int
    unresolved_incident_count: int
    hazard_density_per_km: float
    avg_speed_kmh: float
    avg_crowd_occupancy_percent: float
    recent_aqi_avg: Optional[float] = None
    dominant_hazard_type: Optional[str] = None

class FleetRouteAnalyticsResponse(BaseModel):
    generated_at: datetime
    total_routes: int
    total_active_fleet: int
    routes: List[RouteAnalyticsItem]

class SensorNodeHealth(BaseModel):
    bus_id: str
    route_id: str
    status: str = Field(..., description="ONLINE, DEGRADED, OFFLINE")
    is_simulated: bool = True
    last_telemetry_timestamp: Optional[datetime] = None
    sensors: Dict[str, Dict[str, Any]]
    missing_data_warning: bool
    notes: str

class SensorHealthResponse(BaseModel):
    generated_at: datetime
    total_monitored_nodes: int
    healthy_nodes_count: int
    degraded_nodes_count: int
    offline_nodes_count: int
    nodes: List[SensorNodeHealth]

class ExecutiveAnalyticsSummary(BaseModel):
    city: str = "Vadodara, Gujarat"
    generated_at: datetime
    overall_road_health_index: float
    average_maintenance_risk: float
    critical_segments_count: int
    total_active_incidents: int
    total_active_buses: int
    total_sensor_nodes_monitored: int
    degraded_sensor_nodes: int
    top_corridor_at_risk: Optional[str] = None
    primary_citywide_hazard: str = "pothole"

# Canonical alias
AnalyticsSummary = ExecutiveAnalyticsSummary
