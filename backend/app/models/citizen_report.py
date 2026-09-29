from sqlalchemy import Column, Integer, Float, String, DateTime, Text
from datetime import datetime, timezone
from app.database import Base

class CitizenReport(Base):
    __tablename__ = "citizen_reports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category = Column(String(50), nullable=False, index=True)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    photo_url = Column(String(255), nullable=True)
    device_id_hash = Column(String(64), nullable=True, index=True)
    status = Column(String(50), default="SUBMITTED", nullable=False, index=True)  # SUBMITTED, UNDER_REVIEW, CONFIRMED, RESOLVED
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
