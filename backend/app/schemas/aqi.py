from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class AQIPointResponse(BaseModel):
    id: int
    bus_id: str
    lat: float
    lon: float
    pm2_5: float
    pm10: Optional[float] = None
    co2: Optional[float] = None
    aqi_value: float
    category: str
    timestamp: datetime

    class Config:
        from_attributes = True

class AQIHeatmapPoint(BaseModel):
    lat: float
    lon: float
    intensity: float  # Normalized 0.0 to 1.0 or raw AQI
    aqi: float
    category: str

class AQIHeatmapResponse(BaseModel):
    total_points: int
    city_average_aqi: float
    overall_category: str
    readings: List[AQIPointResponse]
