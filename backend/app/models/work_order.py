from sqlalchemy import Column, Integer, Float, String, DateTime, Text, Boolean
from datetime import datetime, timezone
from app.database import Base

class WorkOrder(Base):
    __tablename__ = "work_orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    incident_id = Column(Integer, nullable=False, index=True)
    title = Column(String(150), nullable=False)
    department = Column(String(100), default="VMC Roads & Infrastructure", nullable=False)
    assigned_to = Column(String(100), default="Road Maintenance Team 3", nullable=False)
    location_hint = Column(String(255), nullable=True)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    priority = Column(String(20), default="HIGH", nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String(40), default="CREATED", nullable=False) # CREATED, ASSIGNED, IN_REPAIR, RESOLVED, VERIFIED
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    is_simulated = Column(Boolean, default=True, nullable=False, index=True)
    simulation_run_id = Column(String(50), nullable=True, index=True)

class VerificationAudit(Base):
    __tablename__ = "verification_audits"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    work_order_id = Column(Integer, nullable=False, index=True)
    incident_id = Column(Integer, nullable=False, index=True)
    bus_id = Column(String(50), nullable=False)
    verification_timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    vibration_peak_g = Column(Float, default=1.02, nullable=False) # Normal smooth road vibration post-repair (< 1.2g)
    visual_defect_detected = Column(Boolean, default=False, nullable=False)
    verdict = Column(String(40), default="VERIFIED_PASS", nullable=False) # VERIFIED_PASS, REPAIR_DEFECT_PERSISTS
    notes = Column(Text, nullable=True)
