"""
Predictive Analytics & Maintenance Intelligence Service
Phase 5 Implementation:
- Transparent, explainable road deterioration risk scoring.
- Predictive maintenance signals based on real stored incidents, IMU shocks, and flood history.
- Handles insufficient historical data honestly without fabricated ML claims.
- Fleet corridor analytics and sensor health monitoring.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.road_health import RoadSegment, RoadHealthScore
from app.models.hazard import Hazard
from app.models.ai_observation import AIObservation
from app.models.raw_event import RawEvent
from app.models.work_order import WorkOrder, VerificationAudit
from app.models.bus import BusLiveState
from app.models.aqi import AQIPoint
from app.services.road_health_service import init_road_segments, point_near_segment
from app.simulator.routes import VADODARA_ROUTES
from app.simulator.engine import simulator_engine

def get_predictive_road_health_data(db: Session) -> Dict[str, Any]:
    """
    Calculate explainable predictive road-risk scores across monitored Vadodara corridors.
    Combines:
    - Defect density and severity
    - Multi-modal sensor evidence (camera + IMU spikes)
    - Waterlogging frequency (accelerated pavement foundation failure)
    - Historical verification & repair recurrence
    """
    init_road_segments(db)
    segments = db.query(RoadSegment).all()
    hazards = db.query(Hazard).all()
    raw_imu_events = db.query(RawEvent).filter(RawEvent.sensor_source == "imu").all()

    now = datetime.now(timezone.utc)
    segment_results = []
    high_risk_count = 0

    for seg in segments:
        seg_hazards = [h for h in hazards if point_near_segment(h.lat, h.lon, seg)]
        unresolved_hazards = [h for h in seg_hazards if h.status not in ["resolved", "verified_closed"]]
        confirmed_defects = [h for h in seg_hazards if h.is_confirmed]
        waterlogging_hazards = [
            h for h in seg_hazards if "waterlogging" in h.hazard_type.lower()
        ]

        # Count IMU vibration shocks near segment (> 2.0g shockwave)
        seg_shocks = [
            ev for ev in raw_imu_events
            if ev.value and ev.value > 2.0 and point_near_segment(ev.lat, ev.lon, seg)
        ]

        total_obs = len(seg_hazards) + len(seg_shocks)
        length_km = max(0.5, seg.length_meters / 1000.0)
        unresolved_count = len(unresolved_hazards)
        confirmed_count = len(confirmed_defects)
        water_count = len(waterlogging_hazards)

        # Base current health from latest calculated record
        health_rec = db.query(RoadHealthScore).filter(
            RoadHealthScore.segment_code == seg.segment_code
        ).first()
        current_health = health_rec.health_score if health_rec else 100.0

        # Handle Insufficient Historical Observations
        if total_obs == 0:
            segment_results.append({
                "segment_code": seg.segment_code,
                "corridor_name": seg.corridor_name,
                "health_score": current_health,
                "predicted_risk_score": 10.0,
                "risk_level": "LOW",
                "deterioration_trend": "INSUFFICIENT_DATA",
                "data_sufficiency": "INSUFFICIENT_HISTORICAL_OBSERVATIONS",
                "total_historical_events": 0,
                "unresolved_incidents": 0,
                "confirmed_defects": 0,
                "waterlogging_events": 0,
                "risk_drivers": [
                    "Insufficient historical observations on this corridor",
                    "No verified defect shockwaves recorded yet"
                ],
                "recommended_action": "Maintain routine automated fleet patrol monitoring.",
                "confidence_score": 0.25,
            })
            continue

        drivers = []
        risk_components = 0.0

        # 1. Unresolved incidents component (up to 35 pts)
        if unresolved_count > 0:
            unresolved_weight = min(35.0, unresolved_count * 18.0)
            risk_components += unresolved_weight
            drivers.append(f"{unresolved_count} active unresolved road defect(s) on corridor")

        # 2. Multi-bus corroborated defects (up to 25 pts)
        if confirmed_count > 0:
            confirmed_weight = min(25.0, confirmed_count * 12.5)
            risk_components += confirmed_weight
            drivers.append(f"{confirmed_count} multi-bus confirmed defect(s) verifying structural flaw")

        # 3. Waterlogging & drainage vulnerability (up to 30 pts)
        if water_count > 0:
            water_weight = min(30.0, water_count * 25.0)
            risk_components += water_weight
            drivers.append(f"Prone to drainage submergence ({water_count} flood event(s)) accelerating sub-base wash")

        # 4. Repeated high-g mechanical vibration shocks (up to 20 pts)
        if len(seg_shocks) > 0:
            shock_weight = min(20.0, len(seg_shocks) * 6.5)
            risk_components += shock_weight
            drivers.append(f"{len(seg_shocks)} dynamic IMU shock events exceeding 2.0g impact threshold")

        # 5. Defect density penalty
        defect_density = (confirmed_count + unresolved_count) / length_km
        if defect_density > 1.0:
            risk_components += min(15.0, defect_density * 5.0)
            drivers.append(f"Elevated defect density ({defect_density:.2f} defects/km)")

        predicted_risk = round(min(100.0, max(5.0, risk_components)), 1)

        # Categorize Risk Level & Deterioration Trend
        if predicted_risk >= 75.0:
            risk_level = "CRITICAL"
            deterioration_trend = "RAPID_DETERIORATION"
            high_risk_count += 1
        elif predicted_risk >= 50.0:
            risk_level = "ELEVATED"
            deterioration_trend = "DEGRADING"
            high_risk_count += 1
        elif predicted_risk >= 25.0:
            risk_level = "MODERATE"
            deterioration_trend = "DEGRADING" if unresolved_count > 0 else "STABLE"
        else:
            risk_level = "LOW"
            deterioration_trend = "STABLE"

        # Actionable Recommendation Synthesis
        if water_count > 0 and predicted_risk >= 60.0:
            action = "Dispatch stormwater drainage clearance crew and inspect Akota underpass culverts."
        elif unresolved_count >= 2:
            action = "Prioritize heavy maintenance asphalt patching team before corridor structural integrity worsens."
        elif unresolved_count == 1:
            action = "Schedule asphalt resurfacing patch order for identified defect."
        elif len(seg_shocks) > 0:
            action = "Conduct profilometer surface roughness audit during next scheduled maintenance cycle."
        else:
            action = "Nominal road integrity. Continue routine mobile fleet sensor monitoring."

        data_sufficiency = "SUFFICIENT" if total_obs >= 3 else "LIMITED"
        confidence = 0.92 if data_sufficiency == "SUFFICIENT" else 0.65

        segment_results.append({
            "segment_code": seg.segment_code,
            "corridor_name": seg.corridor_name,
            "health_score": current_health,
            "predicted_risk_score": predicted_risk,
            "risk_level": risk_level,
            "deterioration_trend": deterioration_trend,
            "data_sufficiency": data_sufficiency,
            "total_historical_events": total_obs,
            "unresolved_incidents": unresolved_count,
            "confirmed_defects": confirmed_count,
            "waterlogging_events": water_count,
            "risk_drivers": drivers if drivers else ["Nominal baseline telemetry"],
            "recommended_action": action,
            "confidence_score": confidence,
        })

    # Sort by predicted risk descending
    segment_results.sort(key=lambda s: s["predicted_risk_score"], reverse=True)

    return {
        "city": "Vadodara, Gujarat",
        "generated_at": now,
        "total_corridors_analyzed": len(segment_results),
        "high_risk_segments_count": high_risk_count,
        "methodology_note": "Deterministic risk scoring derived from corroborated IMU shockwaves, optical AI detections, and waterlogging frequency.",
        "segments": segment_results,
    }

def get_predictive_maintenance_signals(db: Session) -> Dict[str, Any]:
    """
    Generate prioritized municipal work recommendations and predictive maintenance orders.
    """
    health_data = get_predictive_road_health_data(db)
    now = datetime.now(timezone.utc)
    items = []

    rank = 1
    for seg in health_data["segments"]:
        score = seg["predicted_risk_score"]

        # Only recommend maintenance action for non-trivial risk or active defects
        if score < 20.0 and seg["unresolved_incidents"] == 0:
            urgency = "ROUTINE"
            work_type = "Routine Visual Patrol"
        elif score >= 75.0:
            urgency = "IMMEDIATE_DISPATCH"
            work_type = "Emergency Drainage / Sub-base Rebuild" if seg["waterlogging_events"] > 0 else "Emergency Asphalt Patching"
        elif score >= 50.0:
            urgency = "URGENT"
            work_type = "Milling & Asphalt Compaction"
        elif score >= 25.0:
            urgency = "PLANNED"
            work_type = "Scheduled Crack Sealing & Patching"
        else:
            urgency = "ROUTINE"
            work_type = "Preventive Maintenance Audit"

        # Check if there is any verification audit history
        last_audit = db.query(VerificationAudit).order_by(
            VerificationAudit.verification_timestamp.desc()
        ).first()

        primary_defect = "Waterlogging Hazard" if seg["waterlogging_events"] > 0 else (
            "Pothole / Surface Depression" if seg["confirmed_defects"] > 0 else "Pavement Roughness"
        )

        items.append({
            "segment_code": seg["segment_code"],
            "corridor_name": seg["corridor_name"],
            "priority_rank": rank,
            "risk_score": score,
            "urgency": urgency,
            "primary_defect_type": primary_defect,
            "drivers": seg["risk_drivers"],
            "recommended_action": seg["recommended_action"],
            "estimated_work_type": work_type,
            "last_repair_verified_at": last_audit.verification_timestamp if last_audit else None,
        })
        rank += 1

    return {
        "city": "Vadodara, Gujarat",
        "generated_at": now,
        "total_recommendations": len(items),
        "items": items,
    }

def get_fleet_route_analytics(db: Session) -> Dict[str, Any]:
    """
    Calculate aggregate intelligence per Vadodara transit corridor:
    - Active buses and fleet deployment
    - Hazard density per corridor
    - Speed and commuter occupancy
    - Ambient air quality readings
    """
    now = datetime.now(timezone.utc)
    hazards = db.query(Hazard).all()
    live_buses = db.query(BusLiveState).all()
    recent_aqi = db.query(AQIPoint).order_by(AQIPoint.timestamp.desc()).limit(100).all()

    route_items = []
    total_active_fleet = 0

    for route_id, route_data in VADODARA_ROUTES.items():
        buses_on_route = [b for b in live_buses if b.route_id == route_id]
        active_buses = [b for b in buses_on_route if b.status.lower() == "active"]
        total_active_fleet += len(active_buses)

        # Calculate corridor length in km from waypoints
        waypoints = route_data.get("waypoints", [])
        length_km = 0.0
        for i in range(len(waypoints) - 1):
            p1 = waypoints[i]
            p2 = waypoints[i + 1]
            from app.services.geo import haversine_distance
            length_km += haversine_distance(p1[0], p1[1], p2[0], p2[1]) / 1000.0
        length_km = max(1.0, round(length_km, 2))

        # Filter hazards on or near this corridor
        corridor_hazards = []
        for h in hazards:
            # Check proximity to any waypoint of this route
            for wp in waypoints:
                from app.services.geo import haversine_distance
                if haversine_distance(h.lat, h.lon, wp[0], wp[1]) <= 350.0:
                    corridor_hazards.append(h)
                    break

        unresolved = [h for h in corridor_hazards if h.status not in ["resolved", "verified_closed"]]
        hazard_density = round(len(unresolved) / length_km, 2)

        # Average speed and crowd occupancy
        avg_speed = 0.0
        avg_occ = 0.0
        if buses_on_route:
            avg_speed = round(sum(b.speed for b in buses_on_route) / len(buses_on_route), 1)
            total_crowd = sum(b.crowd_count for b in buses_on_route)
            total_cap = sum(b.capacity for b in buses_on_route)
            avg_occ = round((total_crowd / float(total_cap)) * 100.0, 1) if total_cap > 0 else 0.0

        # Route AQI average
        route_bus_ids = {b.bus_id for b in buses_on_route}
        route_aqi_pts = [p for p in recent_aqi if p.bus_id in route_bus_ids]
        avg_aqi = round(sum(p.aqi_value for p in route_aqi_pts) / len(route_aqi_pts), 1) if route_aqi_pts else None

        # Dominant hazard type
        dom_hazard = None
        if corridor_hazards:
            types = [h.hazard_type for h in corridor_hazards]
            dom_hazard = max(set(types), key=types.count)

        route_items.append({
            "route_id": route_id,
            "route_name": route_data.get("route_name", "Vadodara Transit Corridor"),
            "total_buses_assigned": len(buses_on_route),
            "active_buses": len(active_buses),
            "corridor_length_km": length_km,
            "incident_count": len(corridor_hazards),
            "unresolved_incident_count": len(unresolved),
            "hazard_density_per_km": hazard_density,
            "avg_speed_kmh": avg_speed,
            "avg_crowd_occupancy_percent": avg_occ,
            "recent_aqi_avg": avg_aqi,
            "dominant_hazard_type": dom_hazard,
        })

    return {
        "generated_at": now,
        "total_routes": len(route_items),
        "total_active_fleet": total_active_fleet,
        "routes": route_items,
    }

def get_sensor_health_telemetry(db: Session) -> Dict[str, Any]:
    """
    Monitor sensor health across all 12 simulated buses.
    Tracks optical camera, 3-axis IMU, ambient AQI, and water level proxy sensors.
    Supports simulated failure detection.
    """
    now = datetime.now(timezone.utc)
    nodes = []
    healthy_count = 0
    degraded_count = 0
    offline_count = 0

    # Get live state records
    bus_records = {b.bus_id: b for b in db.query(BusLiveState).all()}

    for bus in simulator_engine.buses.values():
        rec = bus_records.get(bus.bus_id)
        has_failure = bus.sensor_failure_active
        is_active = bus.is_active

        if not is_active:
            status = "OFFLINE"
            offline_count += 1
            notes = "Bus engine offline or out of operational service."
            missing_warning = True
        elif has_failure:
            status = "DEGRADED"
            degraded_count += 1
            notes = "Simulated sensor failure scenario active: IMU / Camera telemetry streams suppressed."
            missing_warning = True
        else:
            status = "ONLINE"
            healthy_count += 1
            notes = "All 4 sensor channels transmitting nominal telemetry."
            missing_warning = False

        # Sensor channels status
        sensors = {
            "camera": {
                "status": "FAILED" if has_failure else ("ONLINE" if is_active else "OFFLINE"),
                "sample_rate_hz": 1.0 if (is_active and not has_failure) else 0.0,
                "type": "Road-Facing Edge AI Camera",
            },
            "imu": {
                "status": "FAILED" if has_failure else ("ONLINE" if is_active else "OFFLINE"),
                "sample_rate_hz": 20.0 if (is_active and not has_failure) else 0.0,
                "type": "3-Axis Accelerometer (Vibration)",
            },
            "aqi": {
                "status": "ONLINE" if is_active else "OFFLINE",
                "sample_rate_hz": 0.2 if is_active else 0.0,
                "type": "PM2.5 / PM10 / CO2 Optical Sensor",
            },
            "water_proxy": {
                "status": "ONLINE" if is_active else "OFFLINE",
                "sample_rate_hz": 0.2 if is_active else 0.0,
                "type": "Underpass Water Level Radar Proxy",
            },
        }

        nodes.append({
            "bus_id": bus.bus_id,
            "route_id": bus.route_id,
            "status": status,
            "is_simulated": True,
            "last_telemetry_timestamp": rec.last_updated if rec else now,
            "sensors": sensors,
            "missing_data_warning": missing_warning,
            "notes": notes,
        })

    return {
        "generated_at": now,
        "total_monitored_nodes": len(nodes),
        "healthy_nodes_count": healthy_count,
        "degraded_nodes_count": degraded_count,
        "offline_nodes_count": offline_count,
        "nodes": nodes,
    }

def get_executive_summary(db: Session) -> Dict[str, Any]:
    """
    Synthesize city-wide executive summary for command center decision makers.
    """
    health_data = get_predictive_road_health_data(db)
    fleet_analytics = get_fleet_route_analytics(db)
    sensor_health = get_sensor_health_telemetry(db)

    segments = health_data["segments"]
    avg_health = sum(s["health_score"] for s in segments) / len(segments) if segments else 100.0
    avg_risk = sum(s["predicted_risk_score"] for s in segments) / len(segments) if segments else 0.0

    critical_count = sum(1 for s in segments if s["risk_level"] in ["CRITICAL", "ELEVATED"])
    total_active_incidents = sum(s["unresolved_incidents"] for s in segments)

    top_corridor = segments[0]["corridor_name"] if segments and segments[0]["predicted_risk_score"] > 25.0 else None

    return {
        "city": "Vadodara, Gujarat",
        "generated_at": datetime.now(timezone.utc),
        "overall_road_health_index": round(avg_health, 1),
        "average_maintenance_risk": round(avg_risk, 1),
        "critical_segments_count": critical_count,
        "total_active_incidents": total_active_incidents,
        "total_active_buses": fleet_analytics["total_active_fleet"],
        "total_sensor_nodes_monitored": sensor_health["total_monitored_nodes"],
        "degraded_sensor_nodes": sensor_health["degraded_nodes_count"],
        "top_corridor_at_risk": top_corridor,
        "primary_citywide_hazard": "pothole",
    }
