"""
Road Health Intelligence Service
Calculates segment-level Road Health Scores (0-100), International Roughness
Index (IRI) equivalents, and defect densities for municipal prioritization.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.road_health import RoadSegment, RoadHealthScore
from app.models.hazard import Hazard
from app.models.ai_observation import AIObservation
from app.services.geo import haversine_distance

VADODARA_SEGMENTS = [
    {
        "segment_code": "SEG-101-1",
        "corridor_name": "Sayajigunj Central Corridor",
        "ward_number": 4,
        "start_lat": 22.3108,
        "start_lon": 73.1812,
        "end_lat": 22.3160,
        "end_lon": 73.1905,
        "length_meters": 1200.0,
        "traffic_tier": 1,
    },
    {
        "segment_code": "SEG-102-1",
        "corridor_name": "Alkapuri Commercial Corridor",
        "ward_number": 2,
        "start_lat": 22.3115,
        "start_lon": 73.1710,
        "end_lat": 22.3175,
        "end_lon": 73.1650,
        "length_meters": 1400.0,
        "traffic_tier": 1,
    },
    {
        "segment_code": "SEG-103-1",
        "corridor_name": "Akota - Mujmahuda Radial",
        "ward_number": 6,
        "start_lat": 22.2980,
        "start_lon": 73.1765,
        "end_lat": 22.2890,
        "end_lon": 73.1680,
        "length_meters": 1500.0,
        "traffic_tier": 2,
    },
    {
        "segment_code": "SEG-104-1",
        "corridor_name": "Fatehgunj University Line",
        "ward_number": 3,
        "start_lat": 22.3210,
        "start_lon": 73.1880,
        "end_lat": 22.3350,
        "end_lon": 73.1840,
        "length_meters": 1800.0,
        "traffic_tier": 2,
    },
    {
        "segment_code": "SEG-105-1",
        "corridor_name": "Makarpura Industrial Line",
        "ward_number": 8,
        "start_lat": 22.2650,
        "start_lon": 73.1950,
        "end_lat": 22.2450,
        "end_lon": 73.2050,
        "length_meters": 2400.0,
        "traffic_tier": 1,
    },
    {
        "segment_code": "SEG-106-1",
        "corridor_name": "Waghodia Road Arterial",
        "ward_number": 5,
        "start_lat": 22.2950,
        "start_lon": 73.2200,
        "end_lat": 22.2980,
        "end_lon": 73.2550,
        "length_meters": 3200.0,
        "traffic_tier": 2,
    },
]

def init_road_segments(db: Session):
    """Seed canonical Vadodara transit corridor segments if not present."""
    count = db.query(RoadSegment).count()
    if count == 0:
        for seg_data in VADODARA_SEGMENTS:
            seg = RoadSegment(**seg_data)
            db.add(seg)
        db.commit()

def point_near_segment(lat: float, lon: float, seg: RoadSegment, threshold_meters: float = 250.0) -> bool:
    """Check if a coordinate point is within threshold distance of segment bounds."""
    d_start = haversine_distance(lat, lon, seg.start_lat, seg.start_lon)
    d_end = haversine_distance(lat, lon, seg.end_lat, seg.end_lon)
    # Midpoint approximation
    mid_lat = (seg.start_lat + seg.end_lat) / 2.0
    mid_lon = (seg.start_lon + seg.end_lon) / 2.0
    d_mid = haversine_distance(lat, lon, mid_lat, mid_lon)

    return min(d_start, d_end, d_mid) <= threshold_meters

def calculate_all_road_health(db: Session, simulation_run_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Recalculate road health scores for all segments based on active incidents and IMU observations.
    """
    init_road_segments(db)
    segments = db.query(RoadSegment).all()
    hazards = db.query(Hazard).filter(
        Hazard.status.notin_(["resolved", "VERIFIED_CLOSED"])
    ).all()

    results: List[Dict[str, Any]] = []

    for seg in segments:
        seg_hazards = [h for h in hazards if point_near_segment(h.lat, h.lon, seg)]
        confirmed_count = sum(1 for h in seg_hazards if h.is_confirmed)
        length_km = max(0.5, seg.length_meters / 1000.0)
        defect_density = confirmed_count / length_km

        # Roughness index: 1.0 (smooth) baseline, scales with defects and severity
        roughness = 1.0
        if seg_hazards:
            avg_sev = sum(h.severity for h in seg_hazards) / float(len(seg_hazards))
            roughness = round(1.0 + (confirmed_count * 0.45) + (avg_sev - 2.0) * 0.35, 2)
        roughness = max(1.0, min(5.0, roughness))

        # Health score: 0 to 100 (100 = pristine)
        penalty = (defect_density * 14.0) + ((roughness - 1.0) * 12.0)
        health_score = round(max(0.0, min(100.0, 100.0 - penalty)), 1)

        # Rating label
        if health_score >= 80.0:
            rating = "Good"
        elif health_score >= 60.0:
            rating = "Fair"
        elif health_score >= 40.0:
            rating = "Poor"
        else:
            rating = "Critical"

        # Upsert RoadHealthScore in DB
        health_rec = db.query(RoadHealthScore).filter(
            RoadHealthScore.segment_code == seg.segment_code
        ).first()

        now = datetime.now(timezone.utc)
        if not health_rec:
            health_rec = RoadHealthScore(
                segment_code=seg.segment_code,
                health_score=health_score,
                roughness_index=roughness,
                defect_density=round(defect_density, 2),
                confirmed_defects_count=confirmed_count,
                repeat_failure_rate=0.0,
                last_assessed_at=now,
                is_simulated=True,
                simulation_run_id=simulation_run_id,
            )
            db.add(health_rec)
        else:
            health_rec.health_score = health_score
            health_rec.roughness_index = roughness
            health_rec.defect_density = round(defect_density, 2)
            health_rec.confirmed_defects_count = confirmed_count
            health_rec.last_assessed_at = now
            if simulation_run_id:
                health_rec.simulation_run_id = simulation_run_id

        results.append({
            "segment_code": seg.segment_code,
            "corridor_name": seg.corridor_name,
            "health_score": health_score,
            "rating": rating,
            "roughness_index": roughness,
            "defect_density": round(defect_density, 2),
            "confirmed_defects_count": confirmed_count,
            "start_lat": seg.start_lat,
            "start_lon": seg.start_lon,
            "end_lat": seg.end_lat,
            "end_lon": seg.end_lon,
            "last_assessed_at": now,
        })

    db.commit()
    return results
