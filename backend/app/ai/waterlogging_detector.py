"""
Waterlogging Severity Detector
Model: waterlogging_rules_v1 (1.0.0)

Evaluates multi-modal physical proxies (optical road surface specular reflection,
wheel hydroplaning drag coefficient, and telemetry rainfall rate) to classify
monsoon waterlogging severity from NORMAL up to CRITICAL emergency levels.
"""

import json
from typing import Dict, Any, Optional

class WaterloggingDetector:
    def __init__(self):
        self.model_name = "waterlogging_rules_v1"
        self.model_version = "1.0.0"

    def analyze(
        self,
        water_proxy_data: Any,
        bus_id: str = "UNKNOWN",
        lat: float = 0.0,
        lon: float = 0.0,
        raw_event_id: Optional[int] = None,
        simulation_run_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze physical water accumulation proxies.
        Returns detection dict if waterlogging exceeds baseline threshold, else None.
        """
        if not water_proxy_data:
            return None

        if isinstance(water_proxy_data, str):
            try:
                data = json.loads(water_proxy_data)
            except Exception:
                return None
        elif isinstance(water_proxy_data, dict):
            data = water_proxy_data
        else:
            return None

        reflection = float(data.get("water_reflection_index", 0.0))
        drag = float(data.get("wheel_drag_coefficient", 0.0))
        rainfall = float(data.get("rainfall_rate_mm_hr", 0.0))

        # Classify severity according to physics thresholds
        if (reflection >= 0.75 and drag >= 0.35 and rainfall >= 25.0) or (reflection >= 0.82 and drag >= 0.45):
            severity = 5.0
            waterlogging_severity = "CRITICAL"
            hazard_class = "WATERLOGGING_CRITICAL"
            confidence = 0.96
        elif (reflection >= 0.55 and drag >= 0.20 and rainfall >= 15.0) or (reflection >= 0.65 and drag >= 0.25):
            severity = 4.0
            waterlogging_severity = "SEVERE"
            hazard_class = "waterlogging"
            confidence = 0.88
        elif reflection >= 0.35 or drag >= 0.12 or rainfall >= 20.0:
            severity = 3.0
            waterlogging_severity = "MODERATE"
            hazard_class = "waterlogging"
            confidence = 0.80
        elif reflection >= 0.18:
            severity = 2.0
            waterlogging_severity = "MINOR"
            hazard_class = "waterlogging"
            confidence = 0.70
        else:
            # Normal dry or damp road
            return None

        features = {
            "water_reflection_index": round(reflection, 3),
            "wheel_drag_coefficient": round(drag, 3),
            "rainfall_rate_mm_hr": round(rainfall, 1),
            "waterlogging_severity": waterlogging_severity,
        }

        return {
            "bus_id": bus_id,
            "raw_event_id": raw_event_id,
            "observation_type": "WATERLOGGING_SEVERITY",
            "hazard_class": hazard_class,
            "confidence": confidence,
            "severity_score": severity,
            "bounding_box": None,
            "signal_features": features,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "evidence_ref": f"water_sensor_{bus_id}_{waterlogging_severity.lower()}",
            "lat": lat,
            "lon": lon,
            "simulation_run_id": simulation_run_id,
        }

waterlogging_detector = WaterloggingDetector()
