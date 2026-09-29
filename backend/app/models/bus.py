from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean
from datetime import datetime, timezone
from app.database import Base

class Bus(Base):
    __tablename__ = "buses"

    id = Column(String(50), primary_key=True, index=True)
    route_id = Column(String(50), nullable=False)
    route_name = Column(String(100), nullable=False)
    depot = Column(String(50), default="Sayajigunj Central Depot")
    hardware_kit_version = Column(String(30), default="BEL-UrbanEdge-V1")
    is_active = Column(Boolean, default=True)

class BusLiveState(Base):
    __tablename__ = "bus_live_state"

    bus_id = Column(String(50), primary_key=True, index=True)
    route_id = Column(String(50), nullable=False, default="ROUTE-101")
    route_name = Column(String(100), nullable=False, default="Central Corridor")
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    speed = Column(Float, default=30.0)             # km/h
    heading = Column(Float, default=0.0)            # 0-360 degrees
    occupancy_level = Column(String(20), default="low")  # low, medium, high, full
    crowd_count = Column(Integer, default=15)
    capacity = Column(Integer, default=60)
    status = Column(String(20), default="active")   # active, idle, maintenance
    is_simulated = Column(Boolean, default=True, nullable=False, index=True)
    simulation_run_id = Column(String(50), nullable=True, index=True)
    last_updated = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
