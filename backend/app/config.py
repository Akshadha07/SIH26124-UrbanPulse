import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Mobile Urban Intelligence Platform"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    
    # Database: SQLite for fast zero-config prototype, PostgreSQL+PostGIS ready
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./urban_intelligence.db")
    
    # CORS Origins for Frontend Dashboard and Citizen App
    CORS_ORIGINS: List[str] = ["*"]
    
    # Sensor Fusion Parameters
    FUSION_DISTANCE_THRESHOLD_METERS: float = 35.0  # cluster within ~35m radius
    FUSION_TIME_WINDOW_SECONDS: float = 600.0       # within 10 minutes
    
    # Fleet Simulator Parameters
    SIMULATOR_BUS_COUNT: int = 12
    SIMULATION_INTERVAL_SECONDS: float = 5.0        # Default 5.0 seconds emission rate
    SIMULATOR_TICK_SECONDS: float = 5.0
    SIMULATOR_SEED: int = 42                        # Deterministic reproducible seed

    class Config:
        case_sensitive = True

settings = Settings()
