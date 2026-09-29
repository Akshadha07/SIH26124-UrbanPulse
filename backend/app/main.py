"""
FastAPI Main Application
AI-Powered Mobile Urban Intelligence Platform
Smart India Hackathon 2026 - Problem Statement: SIH26124
"""

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db, SessionLocal
from app.api.router import api_v1_router
from app.core.websocket_manager import ws_hub
from app.models.bus import BusLiveState
from app.models.raw_event import RawEvent
from app.models.aqi import AQIReading
from app.simulator.engine import simulator_engine

# Background simulation runner control
simulation_task = None
simulation_running = True

async def run_simulation_loop():
    """
    Background loop that ticks the simulator at configured intervals
    (SIMULATION_INTERVAL_SECONDS = 5.0s by default).
    Broadcasts live bus movements over WebSocket and persists telemetry.
    """
    while simulation_running:
        try:
            await asyncio.sleep(settings.SIMULATION_INTERVAL_SECONDS)
            step_data = simulator_engine.step()

            # Save telemetry to database
            db = SessionLocal()
            try:
                for t in step_data["telemetry"]:
                    bus_state = db.query(BusLiveState).filter(BusLiveState.bus_id == t["bus_id"]).first()
                    if not bus_state:
                        bus_state = BusLiveState(
                            bus_id=t["bus_id"],
                            route_id=t["route_id"],
                            route_name=t["route_name"],
                            lat=t["lat"],
                            lon=t["lon"],
                            speed=t["speed"],
                            heading=t["heading"],
                            crowd_count=t["crowd_count"],
                            capacity=t["capacity"],
                            occupancy_level=t["occupancy_level"],
                            is_simulated=t["is_simulated"],
                            simulation_run_id=t["simulation_run_id"],
                            last_updated=t["timestamp"],
                        )
                        db.add(bus_state)
                    else:
                        bus_state.lat = t["lat"]
                        bus_state.lon = t["lon"]
                        bus_state.speed = t["speed"]
                        bus_state.heading = t["heading"]
                        bus_state.crowd_count = t["crowd_count"]
                        bus_state.occupancy_level = t["occupancy_level"]
                        bus_state.is_simulated = t["is_simulated"]
                        bus_state.simulation_run_id = t["simulation_run_id"]
                        bus_state.last_updated = t["timestamp"]

                # Sample raw sensor events to avoid database explosion
                # Store every 2nd tick or when disturbance/flood active
                if simulator_engine.tick_count % 2 == 0 or simulator_engine.active_scenario is not None:
                    import json
                    for e in step_data["raw_events"]:
                        raw_rec = RawEvent(
                            bus_id=e["bus_id"],
                            event_type=e["event_type"],
                            sensor_source=e["sensor_source"],
                            lat=e["lat"],
                            lon=e["lon"],
                            timestamp=e["timestamp"],
                            confidence=e["confidence"],
                            value=e["value"],
                            raw_camera_ref=e.get("raw_camera_ref"),
                            imu_window=json.dumps(e.get("imu_window")) if e.get("imu_window") else None,
                            water_proxy=json.dumps(e.get("water_proxy")) if e.get("water_proxy") else None,
                            is_simulated=e["is_simulated"],
                            simulation_run_id=e["simulation_run_id"],
                        )
                        db.add(raw_rec)

                    for a in step_data["aqi_readings"]:
                        aqi_rec = AQIReading(
                            bus_id=a["bus_id"],
                            lat=a["lat"],
                            lon=a["lon"],
                            pm2_5=a["pm2_5"],
                            pm10=a["pm10"],
                            co2=a["co2"],
                            aqi_value=a["aqi_value"],
                            category=a["category"],
                            is_simulated=a["is_simulated"],
                            simulation_run_id=a["simulation_run_id"],
                            timestamp=a["timestamp"],
                        )
                        db.add(aqi_rec)

                db.commit()
            finally:
                db.close()

            # Broadcast live fleet movement to connected dashboards via WebSocket
            await ws_hub.broadcast("bus_moved", {
                "simulation_run_id": step_data["simulation_run_id"],
                "tick": step_data["tick"],
                "active_buses": [
                    {
                        "bus_id": b["bus_id"],
                        "lat": b["lat"],
                        "lon": b["lon"],
                        "speed": b["speed"],
                        "heading": b["heading"],
                        "crowd_count": b["crowd_count"],
                        "occupancy_level": b["occupancy_level"],
                    }
                    for b in step_data["telemetry"]
                ],
            })
        except asyncio.CancelledError:
            break
        except Exception as err:
            # Continue running even if single broadcast/tick hits transient error
            await asyncio.sleep(1.0)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global simulation_task, simulation_running
    # Startup: Initialize DB schema & seed fleet
    init_db()

    # Seed initial fleet positions into DB
    db = SessionLocal()
    try:
        for bus_id, sim_bus in simulator_engine.buses.items():
            existing = db.query(BusLiveState).filter(BusLiveState.bus_id == bus_id).first()
            if not existing:
                init_state = BusLiveState(
                    bus_id=bus_id,
                    route_id=sim_bus.route_id,
                    route_name=sim_bus.route_data["route_name"],
                    lat=sim_bus.lat,
                    lon=sim_bus.lon,
                    speed=sim_bus.speed,
                    heading=sim_bus.heading,
                    crowd_count=sim_bus.crowd_count,
                    capacity=sim_bus.capacity,
                    occupancy_level="low",
                    is_simulated=True,
                    simulation_run_id=simulator_engine.simulation_run_id,
                    last_updated=datetime.now(timezone.utc),
                )
                db.add(init_state)
        db.commit()
    finally:
        db.close()

    # Start background simulator loop
    simulation_running = True
    simulation_task = asyncio.create_task(run_simulation_loop())

    yield

    # Shutdown
    simulation_running = False
    if simulation_task:
        simulation_task.cancel()
        try:
            await simulation_task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-Powered Mobile Urban Intelligence Platform using Public Transport Fleet (SIH26124)",
    lifespan=lifespan,
)

# CORS middleware for Web Dashboard & Flutter Mobile App
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers at both /api/v1 and /api for seamless backwards compatibility
app.include_router(api_v1_router, prefix="/api/v1")
app.include_router(api_v1_router, prefix="/api")

# Real-time WebSocket Endpoint
@app.websocket("/ws/live")
async def websocket_live_endpoint(websocket: WebSocket):
    await ws_hub.connect(websocket)
    try:
        while True:
            # Keep socket alive and receive client heartbeats/pings
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_hub.disconnect(websocket)
    except Exception:
        ws_hub.disconnect(websocket)

@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "operational",
        "prototype_city": "Vadodara, Gujarat",
        "active_simulation_run_id": simulator_engine.simulation_run_id,
        "docs_url": "/docs",
    }
