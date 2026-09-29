from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

class SensorEventCreate(BaseModel):
    bus_id: str = Field(..., example="GJ-06-BT-101", description="Identifier of the reporting bus")
    type: str = Field(..., example="imu_stream_window", description="Event type: camera_frame_ping, imu_stream_window, aqi_reading, water_proxy_reading, door_occupancy_tick, pothole, etc.")
    lat: float = Field(..., ge=-90.0, le=90.0, example=22.3072, description="Latitude")
    lon: float = Field(..., ge=-180.0, le=180.0, example=73.1812, description="Longitude")
    timestamp: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc), description="Detection/sample timestamp")
    confidence: Optional[float] = Field(default=1.0, ge=0.0, le=1.0, example=1.0, description="Confidence")
    value: Optional[float] = Field(default=0.0, example=0.0, description="Scalar reading (AQI, crowd count, or peak value)")
    sensor_source: Optional[str] = Field(default="imu", example="imu", description="Source sensor: camera, imu, aqi_sensor, door_counter, water_sensor")
    raw_camera_ref: Optional[str] = Field(default=None, description="Local or mock image frame asset reference (no ground truth defect label)")
    imu_window: Optional[Any] = Field(default=None, description="Compact array or structured numeric window of [ax, ay, az, gz] measurements (no anomaly label)")
    water_proxy: Optional[Any] = Field(default=None, description="Compact raw physical proxies: water_reflection_index, wheel_drag_coefficient, rainfall_rate_mm_hr")
    extra_metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional diagnostic metadata")
    is_simulated: bool = Field(default=True, description="True for simulated events, False for real hardware")
    simulation_run_id: Optional[str] = Field(default=None, description="Active simulation session identifier")

class TelemetryUpdateCreate(BaseModel):
    bus_id: str = Field(..., example="GJ-06-BT-101")
    lat: float = Field(..., ge=-90.0, le=90.0, example=22.3072)
    lon: float = Field(..., ge=-180.0, le=180.0, example=73.1812)
    speed: float = Field(default=30.0, ge=0.0, le=120.0, description="Speed in km/h")
    heading: float = Field(default=0.0, ge=0.0, le=360.0, description="Heading in degrees")
    crowd_count: int = Field(default=15, ge=0, description="Passenger count")
    capacity: int = Field(default=60, ge=1, description="Bus passenger capacity")
    occupancy_level: Optional[str] = Field(default=None, description="Optional occupancy level tag: low, medium, high, full")
    is_simulated: bool = Field(default=True)
    simulation_run_id: Optional[str] = Field(default=None)

class BatchSensorEventsCreate(BaseModel):
    events: List[SensorEventCreate]

class SensorEventResponse(BaseModel):
    status: str = "ingested"
    raw_event_id: int
    bus_id: str
    event_type: str
    fused_hazard_id: Optional[int] = None
    is_confirmed: Optional[bool] = None
    priority_score: Optional[float] = None
    is_simulated: bool = True
    simulation_run_id: Optional[str] = None
    message: str = "Event ingested successfully"

class TelemetryResponse(BaseModel):
    status: str = "updated"
    bus_id: str
    lat: float
    lon: float
    speed: float
    heading: float
    crowd_count: int
    occupancy_level: str
    is_simulated: bool = True
    simulation_run_id: Optional[str] = None
    message: str = "Bus telemetry updated successfully"
