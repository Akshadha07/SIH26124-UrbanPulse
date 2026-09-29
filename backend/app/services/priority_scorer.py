"""
Dynamic Priority Scorer and Explainability Engine
Calculates transparent 0-100 repair and disaster priority scores
with an auditable mathematical breakdown.
"""

from typing import Dict, Any, List, Tuple, Optional

def calculate_priority_score(
    severity: float,
    confidence: float,
    distinct_bus_count: int,
    sensor_sources: List[str],
    hazard_type: str = "pothole",
    waterlogging_severity: Optional[str] = None,
) -> Tuple[float, Dict[str, Any]]:
    """
    Calculate dynamic priority score (0.0 to 100.0) with an explainable breakdown.

    Formula Components:
    1. Severity Component (up to 30 pts): (severity / 5.0) * 30.0
    2. Confidence Component (up to 20 pts): confidence * 20.0
    3. Multi-Bus Corroboration (up to 25 pts): min(25.0, distinct_bus_count * 12.5)
    4. Multi-Sensor Agreement (up to 15 pts): 15.0 if camera+imu corroborate, else 5.0
    5. Waterlogging / Disaster Bonus (up to 25 pts):
       - CRITICAL: +25.0 (guarantees score >= 95.0 for flash alerts)
       - SEVERE: +15.0
       - MODERATE: +5.0
    """
    # 1. Severity component
    clamped_sev = max(1.0, min(5.0, severity))
    sev_pts = (clamped_sev / 5.0) * 30.0

    # 2. Confidence component
    clamped_conf = max(0.0, min(1.0, confidence))
    conf_pts = clamped_conf * 20.0

    # 3. Multi-bus corroboration
    bus_pts = min(25.0, max(1, distinct_bus_count) * 12.5)

    # 4. Multi-sensor agreement
    has_camera = any("camera" in s.lower() for s in sensor_sources)
    has_imu = any("imu" in s.lower() for s in sensor_sources)
    if has_camera and has_imu:
        sensor_pts = 15.0
    elif len(sensor_sources) > 1:
        sensor_pts = 10.0
    else:
        sensor_pts = 5.0

    # 5. Waterlogging emergency bonus
    water_pts = 0.0
    wl_upper = (waterlogging_severity or "").upper()
    is_critical_water = (wl_upper == "CRITICAL" or hazard_type == "WATERLOGGING_CRITICAL")

    if is_critical_water:
        water_pts = 25.0
    elif wl_upper == "SEVERE":
        water_pts = 15.0
    elif wl_upper == "MODERATE":
        water_pts = 5.0

    raw_total = sev_pts + conf_pts + bus_pts + sensor_pts + water_pts
    final_score = min(100.0, max(0.0, raw_total))

    # Critical waterlogging emergency override guarantees immediate top triage
    if is_critical_water and final_score < 95.0:
        final_score = 98.0

    # Build human-readable rationale
    rationale_parts = []
    if is_critical_water:
        rationale_parts.append("EMERGENCY: Critical waterlogging detected, immediate flash alert dispatched")
    if distinct_bus_count >= 2:
        rationale_parts.append(f"Corroborated by {distinct_bus_count} independent buses")
    if has_camera and has_imu:
        rationale_parts.append("Cross-verified by camera defect detection and IMU shockwave")
    if clamped_sev >= 4.0:
        rationale_parts.append(f"High structural severity ({clamped_sev}/5.0)")

    if not rationale_parts:
        rationale_parts.append(f"Single-bus observation awaiting multi-corridor corroboration (severity {clamped_sev}/5.0)")

    explanation = {
        "total_score": round(final_score, 1),
        "breakdown": {
            "severity_component": round(sev_pts, 1),
            "confidence_component": round(conf_pts, 1),
            "multi_bus_component": round(bus_pts, 1),
            "multi_sensor_component": round(sensor_pts, 1),
            "waterlogging_bonus": round(water_pts, 1),
        },
        "rationale": " | ".join(rationale_parts),
    }

    return round(final_score, 1), explanation
