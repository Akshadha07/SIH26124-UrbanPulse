from sqlalchemy import Column, Integer, Float, String, DateTime, Text, Boolean
from datetime import datetime, timezone
from app.database import Base

class RawEvent(Base):
    __tablename__ = "raw_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    bus_id = Column(String(50), nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)  # camera_frame_ping, imu_stream_window, aqi_reading, water_proxy_reading, door_occupancy_tick, pothole, etc.
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    confidence = Column(Float, default=1.0)
    value = Column(Float, default=0.0)  # e.g., AQI value, crowd count, IMU g-force
    sensor_source = Column(String(50), default="camera")  # camera, imu, aqi_sensor, door_sensor, water_sensor
    raw_camera_ref = Column(String(255), nullable=True)  # Mock/local image asset path (zero ground-truth labels)
    imu_window = Column(Text, nullable=True)  # JSON-encoded array of numeric [ax, ay, az, gz] measurements (zero anomaly flags)
    water_proxy = Column(Text, nullable=True)  # JSON-encoded physical proxies: reflection, drag, rain (zero severity labels)
    extra_metadata = Column(Text, nullable=True)  # JSON-encoded extra diagnostic details
    is_simulated = Column(Boolean, default=True, nullable=False, index=True)
    simulation_run_id = Column(String(50), nullable=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

# Alias for canonical architecture nomenclature
RawSensorEvent = RawEvent
