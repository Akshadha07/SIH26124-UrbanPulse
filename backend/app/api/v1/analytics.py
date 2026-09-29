"""
Predictive Analytics & Maintenance Intelligence API Endpoints (/api/v1/analytics)
Phase 5 Implementation:
- Segment-level predictive road health deterioration.
- Prioritized predictive maintenance signals with explainable drivers.
- Route-level hazard density and transit analytics.
- Sensor node health & simulated telemetry status.
- Executive summary for municipal leadership.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.analytics import (
    PredictiveRoadHealthResponse,
    PredictiveMaintenanceResponse,
    FleetRouteAnalyticsResponse,
    SensorHealthResponse,
    ExecutiveAnalyticsSummary,
)
from app.services.predictive_analytics_service import (
    get_predictive_road_health_data,
    get_predictive_maintenance_signals,
    get_fleet_route_analytics,
    get_sensor_health_telemetry,
    get_executive_summary,
)

router = APIRouter(prefix="/analytics", tags=["Predictive Analytics & Intelligence"])

@router.get("/predictive-road-health", response_model=PredictiveRoadHealthResponse)
def get_predictive_road_health(db: Session = Depends(get_db)):
    """
    Retrieve explainable predictive road deterioration risk scores for all monitored Vadodara corridors.
    Combines multi-modal defect evidence, IMU shockwaves, and flood vulnerability.
    """
    return get_predictive_road_health_data(db)

@router.get("/predictive-maintenance", response_model=PredictiveMaintenanceResponse)
def get_predictive_maintenance(db: Session = Depends(get_db)):
    """
    Retrieve prioritized predictive maintenance signals and actionable municipal repair orders.
    Calculated from real stored incident and sensor telemetry history.
    """
    return get_predictive_maintenance_signals(db)

@router.get("/routes", response_model=FleetRouteAnalyticsResponse)
def get_route_analytics(db: Session = Depends(get_db)):
    """
    Retrieve corridor-level transit intelligence: active fleet, hazard density, average speed,
    crowd occupancy, and ambient air quality.
    """
    return get_fleet_route_analytics(db)

@router.get("/sensor-health", response_model=SensorHealthResponse)
def get_sensor_health(db: Session = Depends(get_db)):
    """
    Retrieve telemetry health and operational status for all mobile bus sensor nodes.
    Tracks camera, IMU, AQI, and water level radar sensors with simulated failure detection.
    """
    return get_sensor_health_telemetry(db)

@router.get("/summary", response_model=ExecutiveAnalyticsSummary)
def get_executive_analytics_summary(db: Session = Depends(get_db)):
    """
    Retrieve high-level municipal executive summary synthesizing city road health,
    average maintenance risk, active incidents, and fleet sensor status.
    """
    return get_executive_summary(db)
