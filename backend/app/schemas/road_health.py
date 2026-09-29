from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class RoadSegmentResponse(BaseModel):
    id: int
    segment_code: str
    corridor_name: str
    ward_number: int
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float
    length_meters: float
    traffic_tier: int

    class Config:
        from_attributes = True

class RoadHealthScoreResponse(BaseModel):
    id: int
    segment_code: str
    health_score: float
    roughness_index: float
    defect_density: float
    confirmed_defects_count: int
    repeat_failure_rate: float
    last_assessed_at: datetime
    is_simulated: bool
    simulation_run_id: Optional[str] = None

    class Config:
        from_attributes = True

class RoadHealthSegmentOverview(BaseModel):
    segment_code: str
    corridor_name: str
    health_score: float
    rating: str  # Good (80-100), Fair (60-79), Poor (40-59), Critical (<40)
    roughness_index: float
    defect_density: float
    confirmed_defects_count: int
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float
    last_assessed_at: datetime

class RoadHealthOverviewResponse(BaseModel):
    city: str = "Vadodara, Gujarat"
    overall_city_index: float
    total_segments_monitored: int
    segments: List[RoadHealthSegmentOverview]
