from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean
from datetime import datetime, timezone
from app.database import Base

class AQIReading(Base):
    __tablename__ = "aqi_readings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    bus_id = Column(String(50), nullable=False, index=True)
    lat = Column(Float, nullable=False, index=True)
    lon = Column(Float, nullable=False, index=True)
    pm2_5 = Column(Float, nullable=False)
    pm10 = Column(Float, nullable=True)
    co2 = Column(Float, nullable=True)
    aqi_value = Column(Float, nullable=False, index=True)
    category = Column(String(40), nullable=False) # Good, Moderate, Unhealthy, etc.
    is_simulated = Column(Boolean, default=True, nullable=False, index=True)
    simulation_run_id = Column(String(50), nullable=True, index=True)
    timestamp = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

AQIPoint = AQIReading
