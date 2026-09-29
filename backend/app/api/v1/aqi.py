"""
Air Quality Endpoints (/api/v1/aqi)
Provides access to mobile air quality sensor readings and interpolated heatmap points.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.aqi import AQIReading
from app.schemas.aqi import AQIPointResponse, AQIHeatmapResponse, AQIHeatmapPoint

router = APIRouter(prefix="/aqi", tags=["Air Quality"])

@router.get("/live", response_model=List[AQIPointResponse])
def get_live_aqi(
    limit: int = Query(50, ge=1, le=500),
    is_simulated: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
):
    """Retrieve recent mobile AQI readings across Vadodara."""
    query = db.query(AQIReading).order_by(AQIReading.timestamp.desc())
    if is_simulated is not None:
        query = query.filter(AQIReading.is_simulated == is_simulated)
    return query.limit(limit).all()

@router.get("/grid", response_model=AQIHeatmapResponse)
def get_aqi_grid(db: Session = Depends(get_db)):
    """Retrieve spatial grid points for GIS heatmap rendering."""
    readings = db.query(AQIReading).order_by(AQIReading.timestamp.desc()).limit(100).all()
    points = [
        AQIHeatmapPoint(
            lat=r.lat,
            lon=r.lon,
            aqi=r.aqi_value,
            pm2_5=r.pm2_5,
            intensity=min(1.0, max(0.1, r.aqi_value / 250.0)),
        )
        for r in readings
    ]
    return AQIHeatmapResponse(points=points, count=len(points))

@router.get("/hotspots", response_model=List[AQIPointResponse])
def get_aqi_hotspots(
    threshold_pm25: float = Query(100.0, description="Minimum PM2.5 for hotspot classification"),
    limit: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Retrieve localized sustained high-pollution hotspot points."""
    return db.query(AQIReading).filter(
        (AQIReading.pm2_5 >= threshold_pm25) | 
        (AQIReading.category.in_(["Poor", "Very Poor", "Severe"]))
    ).order_by(AQIReading.pm2_5.desc()).limit(limit).all()
