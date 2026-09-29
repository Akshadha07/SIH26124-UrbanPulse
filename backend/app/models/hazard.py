from sqlalchemy import Column, Integer, Float, String, DateTime, Text, Boolean
from datetime import datetime, timezone
from app.database import Base

class Hazard(Base):
    __tablename__ = "hazards"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    hazard_type = Column(String(50), nullable=False, index=True)  # pothole, crack, waterlogging, WATERLOGGING_CRITICAL, debris
    lat = Column(Float, nullable=False, index=True)
    lon = Column(Float, nullable=False, index=True)
    severity = Column(Float, nullable=False, default=2.0)         # 1.0 (mild) to 5.0 (critical)
    waterlogging_severity = Column(String(20), nullable=True)     # NORMAL, MINOR, MODERATE, SEVERE, CRITICAL
    confidence = Column(Float, nullable=False, default=0.7)       # 0.0 to 1.0
    confirmation_count = Column(Integer, nullable=False, default=1)
    is_confirmed = Column(Boolean, nullable=False, default=False) # Cross-verified (e.g. camera+IMU or multi-bus)
    status = Column(String(40), nullable=False, default="reported") # reported, confirmed, in_progress, resolved, ESCALATED_DISASTER
    priority_score = Column(Float, nullable=False, default=10.0)  # Dynamic repair ranking score
    first_detected_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    last_detected_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    detected_by_buses = Column(Text, default="[]")                # JSON array of bus IDs
    distinct_bus_count = Column(Integer, nullable=False, default=1)
    sources = Column(Text, default="[]")                          # JSON array e.g. ["camera", "imu"]
    address_hint = Column(String(255), nullable=True)
    priority_explanation = Column(Text, nullable=True)            # JSON breakdown of dynamic priority scoring
    verification_passes = Column(Integer, nullable=False, default=0)
    resolved_at = Column(DateTime, nullable=True)
    is_simulated = Column(Boolean, default=True, nullable=False, index=True)
    simulation_run_id = Column(String(50), nullable=True, index=True)

# Alias for canonical architecture nomenclature
FusedIncident = Hazard
