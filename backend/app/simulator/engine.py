"""
Vadodara Fleet and Multi-Sensor Simulator Engine
Phase 2A Implementation:
- Configurable fleet of 12 buses along 6 Vadodara transit corridors.
- Deterministic and reproducible seed.
- Emits raw sensor evidence, strictly without AI conclusions.
- Supports scenarios: monsoon_flood, pothole_cluster, high_crowd_rush, sensor_failure.
- Supports clean simulation run isolation with simulation_run_id.
"""

import math
import random
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple

from app.config import settings
from app.services.geo import calculate_heading, interpolate, haversine_distance
from app.simulator.routes import VADODARA_ROUTES, get_all_routes

class SimulatedBus:
    def __init__(
        self,
        bus_id: str,
        route_id: str,
        initial_waypoint_idx: int = 0,
        fraction: float = 0.0,
        speed_kmh: float = 30.0,
        capacity: int = 60,
    ):
        self.bus_id = bus_id
        self.route_id = route_id
        self.route_data = VADODARA_ROUTES[route_id]
        self.waypoints: List[Tuple[float, float]] = self.route_data["waypoints"]
        self.current_idx = initial_waypoint_idx % len(self.waypoints)
        self.fraction = fraction  # Progress between waypoint[idx] and waypoint[idx+1]
        self.speed = speed_kmh
        self.capacity = capacity
        self.crowd_count = 18
        self.heading = 0.0
        self.lat, self.lon = self.waypoints[self.current_idx]
        self.is_active = True
        self.sensor_failure_active = False

    def update_position(self, delta_seconds: float):
        """Advance bus along its route based on speed and delta_seconds."""
        if not self.is_active or self.sensor_failure_active:
            return

        next_idx = (self.current_idx + 1) % len(self.waypoints)
        p1 = self.waypoints[self.current_idx]
        p2 = self.waypoints[next_idx]
        seg_distance = haversine_distance(p1[0], p1[1], p2[0], p2[1])

        # Distance moved in meters
        speed_mps = (self.speed * 1000.0) / 3600.0
        dist_moved = speed_mps * delta_seconds

        if seg_distance > 0.0:
            step_frac = dist_moved / seg_distance
            self.fraction += step_frac

            while self.fraction >= 1.0:
                self.fraction -= 1.0
                self.current_idx = next_idx
                next_idx = (self.current_idx + 1) % len(self.waypoints)
                p1 = self.waypoints[self.current_idx]
                p2 = self.waypoints[next_idx]

            self.lat, self.lon = interpolate(p1, p2, self.fraction)
            self.heading = calculate_heading(p1[0], p1[1], p2[0], p2[1])


class FleetSimulator:
    def __init__(self, seed: Optional[int] = None, interval_seconds: float = 5.0):
        self.seed = seed or settings.SIMULATOR_SEED
        self.rng = random.Random(self.seed)
        self.interval_seconds = interval_seconds
        self.simulation_run_id = f"SIM-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"
        self.active_scenario: Optional[str] = None
        self.scenario_intensity: float = 1.0
        self.tick_count: int = 0
        self.is_running: bool = True
        self.buses: Dict[str, SimulatedBus] = {}
        self._init_fleet()

    def _init_fleet(self):
        """Initialize 12 buses across 6 Vadodara routes (2 buses per corridor)."""
        self.buses.clear()
        routes = list(VADODARA_ROUTES.keys())
        bus_idx = 1
        for route_id in routes:
            for bus_num in range(1, 3):
                bus_id = f"GJ-06-BT-{100 + bus_idx}"
                # Stagger second bus halfway along route
                initial_waypoint = 0 if bus_num == 1 else len(VADODARA_ROUTES[route_id]["waypoints"]) // 2
                self.buses[bus_id] = SimulatedBus(
                    bus_id=bus_id,
                    route_id=route_id,
                    initial_waypoint_idx=initial_waypoint,
                    speed_kmh=round(self.rng.uniform(25.0, 38.0), 1),
                )
                bus_idx += 1

    def set_scenario(self, scenario_name: Optional[str], intensity: float = 1.0) -> Dict[str, Any]:
        """Activate a deterministic scenario."""
        self.active_scenario = scenario_name
        self.scenario_intensity = intensity

        # Reset any per-scenario temporary bus flags
        for b in self.buses.values():
            b.sensor_failure_active = False

        if scenario_name == "sensor_failure" and "GJ-06-BT-107" in self.buses:
            self.buses["GJ-06-BT-107"].sensor_failure_active = True

        affected = []
        if scenario_name == "monsoon_flood":
            affected = ["ROUTE-103", "Akota Underpass"]
        elif scenario_name == "pothole_cluster":
            affected = ["ROUTE-101", "ROUTE-102", "Sayajigunj", "Alkapuri"]
        elif scenario_name == "high_crowd_rush":
            affected = ["ROUTE-101", "ROUTE-104", "Central Station", "University"]
        elif scenario_name == "sensor_failure":
            affected = ["GJ-06-BT-107"]

        return {
            "scenario_name": scenario_name or "none",
            "active": scenario_name is not None,
            "description": f"Scenario {scenario_name} active with intensity {intensity}",
            "simulation_run_id": self.simulation_run_id,
            "affected_corridors": affected,
            "parameters": {"intensity": intensity, "seed": self.seed},
        }

    def reset(self) -> Dict[str, Any]:
        """Reset simulation state and start a fresh isolated simulation run."""
        previous_run_id = self.simulation_run_id
        # Reseed for reproducible subsequent behavior
        self.seed += 1
        self.rng = random.Random(self.seed)
        self.simulation_run_id = f"SIM-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"
        self.active_scenario = None
        self.scenario_intensity = 1.0
        self.tick_count = 0
        self._init_fleet()

        return {
            "status": "reset_complete",
            "previous_simulation_run_id": previous_run_id,
            "new_simulation_run_id": self.simulation_run_id,
            "active_buses_count": len(self.buses),
            "message": "Simulation environment reset successfully. Non-simulated records preserved.",
        }

    def generate_raw_imu_window(self, bus: SimulatedBus) -> Dict[str, Any]:
        """
        Generate lightweight raw 3-axis IMU sample window (0.5s window).
        Phase 2A requirement: Emits raw numeric accelerometer/gyro samples,
        strictly without 'anomaly=true' or 'pothole_detected=true'.
        """
        # Baseline gravity on z-axis with realistic road noise
        base_az = 9.81
        is_disturbance = False

        # Road disturbance triggers near known ground truth zones
        # E.g. Alkapuri RC Dutt Road (22.3118, 73.1720) or Sayajigunj (22.3142, 73.1865)
        dist_to_alkapuri_defect = haversine_distance(bus.lat, bus.lon, 22.3118, 73.1720)
        dist_to_sayaji_defect = haversine_distance(bus.lat, bus.lon, 22.3142, 73.1865)

        if dist_to_alkapuri_defect < 40.0 or dist_to_sayaji_defect < 40.0:
            is_disturbance = True
        elif self.active_scenario == "pothole_cluster" and bus.route_id in ["ROUTE-101", "ROUTE-102"]:
            # Random defect encounters on target corridors during scenario
            if self.rng.random() < (0.25 * self.scenario_intensity):
                is_disturbance = True

        samples: List[List[float]] = []
        peak_z = base_az

        for i in range(10):  # 10 discrete samples @ 20Hz (500ms window)
            noise_x = self.rng.gauss(0.0, 0.15)
            noise_y = self.rng.gauss(0.0, 0.15)
            noise_gz = self.rng.gauss(0.0, 0.5)

            if is_disturbance and 3 <= i <= 5:
                # Vertical shock excursion spike (e.g. hitting pothole rim)
                shock_z = base_az + self.rng.uniform(10.0, 18.0) * self.scenario_intensity
                noise_x += self.rng.uniform(-2.5, 2.5)
                noise_gz += self.rng.uniform(-8.0, 8.0)
                az = round(shock_z, 3)
            else:
                az = round(base_az + self.rng.gauss(0.0, 0.28), 3)

            if az > peak_z:
                peak_z = az

            samples.append([round(noise_x, 3), round(noise_y, 3), az, round(noise_gz, 3)])

        return {
            "ax": samples[-1][0],
            "ay": samples[-1][1],
            "az": samples[-1][2],
            "peak_z": round(peak_z, 3),
            "sample_window_ms": 500,
            "samples": samples,
            # Note: No 'anomaly' or 'pothole_detected' labels output here.
        }

    def generate_raw_camera_ref(self, bus: SimulatedBus) -> Optional[str]:
        """
        Emits lightweight frame asset reference.
        Phase 2A requirement: Does NOT pass ground-truth defect label to AI.
        """
        frame_idx = (self.tick_count + int(bus.bus_id.split("-")[-1])) % 100
        # Emits local mock frame reference string
        return f"assets/frames/vadodara_{bus.route_id.lower()}_f{frame_idx:04d}.jpg"

    def generate_raw_water_proxy(self, bus: SimulatedBus) -> Dict[str, float]:
        """
        Generate raw physical proxies for water accumulation.
        Phase 2A requirement: Strictly raw proxies, NO 'waterlogging_severity=CRITICAL'.
        """
        # Baseline dry/damp weather
        reflection = round(self.rng.uniform(0.04, 0.14), 3)
        drag = round(self.rng.uniform(0.02, 0.07), 3)
        rainfall = round(self.rng.uniform(0.0, 1.5), 1)

        # Akota Underpass critical zone check (lat: 22.2965, lon: 73.1750)
        dist_to_underpass = haversine_distance(bus.lat, bus.lon, 22.2965, 73.1750)

        if self.active_scenario == "monsoon_flood":
            rainfall = round(self.rng.uniform(45.0, 75.0) * self.scenario_intensity, 1)
            reflection = round(min(1.0, 0.40 + self.rng.uniform(0.1, 0.3) * self.scenario_intensity), 3)
            drag = round(min(2.0, 0.30 + self.rng.uniform(0.1, 0.25) * self.scenario_intensity), 3)

            # High accumulation in low-lying underpass during flood
            if dist_to_underpass < 60.0:
                reflection = round(min(1.0, 0.85 + self.rng.uniform(0.05, 0.12)), 3)
                drag = round(min(2.0, 0.75 + self.rng.uniform(0.10, 0.35) * self.scenario_intensity), 3)

        return {
            "water_reflection_index": reflection,
            "wheel_drag_coefficient": drag,
            "rainfall_rate_mm_hr": rainfall,
        }

    def generate_raw_aqi(self, bus: SimulatedBus) -> Dict[str, Any]:
        """
        Generate raw AQI sensor readings.
        Phase 2A requirement: Raw PM2.5/PM10/CO2, NO 'AQI_ANOMALY'.
        """
        # Baseline depending on traffic tier
        tier = bus.route_data.get("traffic_tier", 1)
        base_pm25 = 85.0 if tier == 1 else 55.0  # Commercial corridors have higher PM2.5

        pm25 = round(max(15.0, self.rng.gauss(base_pm25, 12.0)), 1)
        pm10 = round(pm25 * self.rng.uniform(1.4, 1.8), 1)
        co2 = round(self.rng.uniform(410.0, 520.0), 1)

        category = "Moderate"
        if pm25 <= 30.0:
            category = "Good"
        elif pm25 <= 60.0:
            category = "Satisfactory"
        elif pm25 <= 90.0:
            category = "Moderate"
        elif pm25 <= 120.0:
            category = "Poor"
        else:
            category = "Very Poor"

        return {
            "pm2_5": pm25,
            "pm10": pm10,
            "co2": co2,
            "aqi_value": pm25,  # Proxy AQI index
            "category": category,
        }

    def step(self, delta_seconds: Optional[float] = None) -> Dict[str, Any]:
        """
        Advance all 12 buses by delta_seconds and collect generated telemetry + raw sensor events.
        """
        dt = delta_seconds or self.interval_seconds
        self.tick_count += 1

        telemetry_batch: List[Dict[str, Any]] = []
        raw_events_batch: List[Dict[str, Any]] = []
        aqi_batch: List[Dict[str, Any]] = []

        now = datetime.now(timezone.utc)

        for bus in self.buses.values():
            if not bus.is_active:
                continue

            bus.update_position(dt)

            # Crowd occupancy dynamics
            if self.active_scenario == "high_crowd_rush" and bus.route_id in ["ROUTE-101", "ROUTE-104"]:
                bus.crowd_count = min(bus.capacity, bus.crowd_count + self.rng.randint(2, 6))
            else:
                bus.crowd_count = max(4, min(bus.capacity, bus.crowd_count + self.rng.randint(-2, 2)))

            occ_ratio = bus.crowd_count / float(bus.capacity)
            if occ_ratio < 0.35:
                occ_tag = "low"
            elif occ_ratio < 0.70:
                occ_tag = "medium"
            elif occ_ratio < 0.90:
                occ_tag = "high"
            else:
                occ_tag = "full"

            # 1. GPS Telemetry Record
            telemetry_batch.append({
                "bus_id": bus.bus_id,
                "route_id": bus.route_id,
                "route_name": bus.route_data["route_name"],
                "lat": round(bus.lat, 6),
                "lon": round(bus.lon, 6),
                "speed": bus.speed,
                "heading": bus.heading,
                "crowd_count": bus.crowd_count,
                "capacity": bus.capacity,
                "occupancy_level": occ_tag,
                "is_simulated": True,
                "simulation_run_id": self.simulation_run_id,
                "timestamp": now,
            })

            # If bus has an active sensor failure scenario, skip sensor emissions
            if bus.sensor_failure_active:
                continue

            # 2. Raw IMU measurement window
            imu_data = self.generate_raw_imu_window(bus)
            raw_events_batch.append({
                "bus_id": bus.bus_id,
                "event_type": "imu_stream_window",
                "sensor_source": "imu",
                "lat": round(bus.lat, 6),
                "lon": round(bus.lon, 6),
                "timestamp": now,
                "confidence": 1.0,
                "value": imu_data["peak_z"],
                "imu_window": imu_data,
                "is_simulated": True,
                "simulation_run_id": self.simulation_run_id,
            })

            # 3. Raw Camera frame ping (event-driven or periodic)
            camera_ref = self.generate_raw_camera_ref(bus)
            raw_events_batch.append({
                "bus_id": bus.bus_id,
                "event_type": "camera_frame_ping",
                "sensor_source": "camera",
                "lat": round(bus.lat, 6),
                "lon": round(bus.lon, 6),
                "timestamp": now,
                "confidence": 1.0,
                "value": 0.0,
                "raw_camera_ref": camera_ref,
                "is_simulated": True,
                "simulation_run_id": self.simulation_run_id,
            })

            # 4. Raw Water proxy reading
            water_data = self.generate_raw_water_proxy(bus)
            raw_events_batch.append({
                "bus_id": bus.bus_id,
                "event_type": "water_proxy_reading",
                "sensor_source": "water_sensor",
                "lat": round(bus.lat, 6),
                "lon": round(bus.lon, 6),
                "timestamp": now,
                "confidence": 1.0,
                "value": water_data["rainfall_rate_mm_hr"],
                "water_proxy": water_data,
                "is_simulated": True,
                "simulation_run_id": self.simulation_run_id,
            })

            # 5. Raw AQI Reading
            aqi_data = self.generate_raw_aqi(bus)
            aqi_batch.append({
                "bus_id": bus.bus_id,
                "lat": round(bus.lat, 6),
                "lon": round(bus.lon, 6),
                "pm2_5": aqi_data["pm2_5"],
                "pm10": aqi_data["pm10"],
                "co2": aqi_data["co2"],
                "aqi_value": aqi_data["aqi_value"],
                "category": aqi_data["category"],
                "is_simulated": True,
                "simulation_run_id": self.simulation_run_id,
                "timestamp": now,
            })

        return {
            "tick": self.tick_count,
            "simulation_run_id": self.simulation_run_id,
            "telemetry": telemetry_batch,
            "raw_events": raw_events_batch,
            "aqi_readings": aqi_batch,
        }

# Global simulator singleton
simulator_engine = FleetSimulator(
    seed=settings.SIMULATOR_SEED,
    interval_seconds=settings.SIMULATION_INTERVAL_SECONDS,
)
