from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean
from datetime import datetime, timezone
from app.database import Base

class RoadSegment(Base):
    __tablename__ = "road_segments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    segment_code = Column(String(50), unique=True, index=True, nullable=False)
    corridor_name = Column(String(100), nullable=False)
    ward_number = Column(Integer, default=1, nullable=False)
    start_lat = Column(Float, nullable=False)
    start_lon = Column(Float, nullable=False)
    end_lat = Column(Float, nullable=False)
    end_lon = Column(Float, nullable=False)
    length_meters = Column(Float, default=1000.0, nullable=False)
    traffic_tier = Column(Integer, default=1, nullable=False)

class RoadHealthScore(Base):
    __tablename__ = "road_health_scores"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    segment_code = Column(String(50), nullable=False, index=True)
    health_score = Column(Float, default=100.0, nullable=False)  # 0.0 to 100.0 (100 = pristine, < 40 = severely deteriorated)
    roughness_index = Column(Float, default=1.0, nullable=False) # IRI vibration equivalent
    defect_density = Column(Float, default=0.0, nullable=False)  # Defects per km
    confirmed_defects_count = Column(Integer, default=0, nullable=False)
    repeat_failure_rate = Column(Float, default=0.0, nullable=False)
    last_assessed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    is_simulated = Column(Boolean, default=True, nullable=False, index=True)
    simulation_run_id = Column(String(50), nullable=True, index=True)
