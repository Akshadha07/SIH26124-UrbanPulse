from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class BusLiveResponse(BaseModel):
    bus_id: str
    route_id: str
    route_name: str
    lat: float
    lon: float
    speed: float
    heading: float
    occupancy_level: str
    crowd_count: int
    capacity: int
    status: str
    last_updated: datetime

    class Config:
        from_attributes = True

class Waypoint(BaseModel):
    lat: float
    lon: float
    stop_name: Optional[str] = None

class RouteResponse(BaseModel):
    route_id: str
    route_name: str
    color: str
    stops: List[Waypoint]
    coordinates: List[List[float]]  # [lat, lon] array for polyline rendering
