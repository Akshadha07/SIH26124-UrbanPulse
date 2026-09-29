from sqlalchemy import Column, Integer, Float, String, DateTime, Text, Boolean
from datetime import datetime, timezone
from app.database import Base

class AIObservation(Base):
    __tablename__ = "ai_observations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    raw_event_id = Column(Integer, nullable=True, index=True)
    bus_id = Column(String(50), nullable=False, index=True)
    observation_type = Column(String(50), nullable=False, index=True)  # ROAD_HAZARD_CV, IMU_ANOMALY, AQI_ANOMALY, WATERLOGGING_SEVERITY
    hazard_class = Column(String(50), nullable=False, index=True)       # pothole, road_crack, vibration_shock, waterlogging, WATERLOGGING_CRITICAL, high_pm25
    confidence = Column(Float, nullable=False, default=0.8)             # 0.0 to 1.0
    severity_score = Column(Float, nullable=False, default=2.0)         # 1.0 (minor) to 5.0 (critical)
    bounding_box = Column(Text, nullable=True)                          # JSON: {"ymin": ..., "xmin": ..., "ymax": ..., "xmax": ...}
    signal_features = Column(Text, nullable=True)                       # JSON: {"peak_z_ms2": ..., "peak_z_g": ..., "variance_z": ...}
    model_name = Column(String(50), nullable=False)                     # e.g. road_hazard_prototype_v1, imu_statistical_v1
    model_version = Column(String(30), default="1.0.0")
    evidence_ref = Column(String(255), nullable=True)                   # Frame path or telemetry ref
    lat = Column(Float, nullable=False, index=True)
    lon = Column(Float, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    is_simulated = Column(Boolean, default=True, nullable=False, index=True)
    simulation_run_id = Column(String(50), nullable=True, index=True)
    fusion_status = Column(String(30), default="pending", nullable=False, index=True) # pending, fused, discarded
    incident_id = Column(Integer, nullable=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class IncidentObservationLink(Base):
    __tablename__ = "incident_observation_links"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    incident_id = Column(Integer, nullable=False, index=True)
    observation_id = Column(Integer, nullable=False, index=True)
    distance_to_centroid_meters = Column(Float, default=0.0)
    time_delta_seconds = Column(Float, default=0.0)
    fusion_weight = Column(Float, default=1.0)
    linked_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
