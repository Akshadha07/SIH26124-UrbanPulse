"""
Road Health API Endpoints (/api/v1/road-health)
Provides municipal engineers with corridor health indices, roughness metrics,
and defect densities derived from mobile fleet vibration data.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.road_health import RoadSegment, RoadHealthScore
from app.schemas.road_health import RoadHealthOverviewResponse, RoadHealthSegmentOverview
from app.services.road_health_service import calculate_all_road_health, init_road_segments

router = APIRouter(prefix="/road-health", tags=["Road Health"])

@router.get("", response_model=RoadHealthOverviewResponse)
@router.get("/", response_model=RoadHealthOverviewResponse, include_in_schema=False)
def get_road_health_overview(db: Session = Depends(get_db)):
    """Retrieve citywide road health indices for all transit corridors."""
    init_road_segments(db)
    segments_data = calculate_all_road_health(db)

    # Compute overall city index
    if segments_data:
        city_index = round(sum(s["health_score"] for s in segments_data) / len(segments_data), 1)
    else:
        city_index = 100.0

    segment_overviews = [
        RoadHealthSegmentOverview(
            segment_code=s["segment_code"],
            corridor_name=s["corridor_name"],
            health_score=s["health_score"],
            rating=s["rating"],
            roughness_index=s["roughness_index"],
            defect_density=s["defect_density"],
            confirmed_defects_count=s["confirmed_defects_count"],
            start_lat=s["start_lat"],
            start_lon=s["start_lon"],
            end_lat=s["end_lat"],
            end_lon=s["end_lon"],
            last_assessed_at=s["last_assessed_at"],
        )
        for s in segments_data
    ]

    return RoadHealthOverviewResponse(
        city="Vadodara, Gujarat",
        overall_city_index=city_index,
        total_segments_monitored=len(segment_overviews),
        segments=segment_overviews,
    )

@router.post("/calculate", response_model=RoadHealthOverviewResponse)
def trigger_road_health_recalculation(
    simulation_run_id: Optional[str] = Query(None, description="Optional run ID"),
    db: Session = Depends(get_db),
):
    """Trigger recalculation of road health scores across all monitored corridors."""
    init_road_segments(db)
    segments_data = calculate_all_road_health(db, simulation_run_id=simulation_run_id)

    city_index = round(sum(s["health_score"] for s in segments_data) / len(segments_data), 1) if segments_data else 100.0

    segment_overviews = [
        RoadHealthSegmentOverview(
            segment_code=s["segment_code"],
            corridor_name=s["corridor_name"],
            health_score=s["health_score"],
            rating=s["rating"],
            roughness_index=s["roughness_index"],
            defect_density=s["defect_density"],
            confirmed_defects_count=s["confirmed_defects_count"],
            start_lat=s["start_lat"],
            start_lon=s["start_lon"],
            end_lat=s["end_lat"],
            end_lon=s["end_lon"],
            last_assessed_at=s["last_assessed_at"],
        )
        for s in segments_data
    ]

    return RoadHealthOverviewResponse(
        city="Vadodara, Gujarat",
        overall_city_index=city_index,
        total_segments_monitored=len(segment_overviews),
        segments=segment_overviews,
    )
