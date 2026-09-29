"""
Aggregated API Router
Mounts all versioned v1 sub-routers.
"""

from fastapi import APIRouter
from app.api.v1.ingest import router as ingest_router
from app.api.v1.simulate import router as simulate_router
from app.api.v1.fleet import router as fleet_router
from app.api.v1.incidents import router as incidents_router
from app.api.v1.aqi import router as aqi_router
from app.api.v1.road_health import router as road_health_router
from app.api.v1.work_orders import router as work_orders_router
from app.api.v1.citizen import router as citizen_router
from app.api.v1.analytics import router as analytics_router

api_v1_router = APIRouter()
api_v1_router.include_router(ingest_router)
api_v1_router.include_router(simulate_router)
api_v1_router.include_router(fleet_router)
api_v1_router.include_router(incidents_router)
api_v1_router.include_router(aqi_router)
api_v1_router.include_router(road_health_router)
api_v1_router.include_router(work_orders_router)
api_v1_router.include_router(citizen_router)
api_v1_router.include_router(analytics_router)
