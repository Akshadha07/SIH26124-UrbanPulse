"""
AQI Anomaly Detector
Model: aqi_baseline_v1 (1.0.0)

Monitors spatial mobile particulate readings (PM2.5, PM10, CO2) against
localized historical baselines, flagging air pollution hotspot anomalies.
"""

from typing import Dict, Any, Optional

class AQIAnomalyDetector:
    def __init__(self, pm25_hotspot_threshold: float = 120.0):
        self.model_name = "aqi_baseline_v1"
        self.model_version = "1.0.0"
        self.pm25_hotspot_threshold = pm25_hotspot_threshold

    def analyze(
        self,
        pm2_5: float,
        pm10: Optional[float] = None,
        co2: Optional[float] = None,
        bus_id: str = "UNKNOWN",
        lat: float = 0.0,
        lon: float = 0.0,
        raw_event_id: Optional[int] = None,
        simulation_run_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze particulate reading. Returns detection dict if hotspot threshold exceeded.
        """
        if pm2_5 < self.pm25_hotspot_threshold:
            return None

        severity = min(5.0, 2.5 + (pm2_5 - self.pm25_hotspot_threshold) / 25.0)
        confidence = min(0.95, 0.80 + (pm2_5 - self.pm25_hotspot_threshold) / 100.0)

        features = {
            "pm2_5": round(pm2_5, 1),
            "pm10": round(pm10, 1) if pm10 is not None else None,
            "co2": round(co2, 1) if co2 is not None else None,
            "exceedance_pm25": round(pm2_5 - self.pm25_hotspot_threshold, 1),
        }

        return {
            "bus_id": bus_id,
            "raw_event_id": raw_event_id,
            "observation_type": "AQI_ANOMALY",
            "hazard_class": "high_pm25",
            "confidence": round(confidence, 3),
            "severity_score": round(severity, 2),
            "bounding_box": None,
            "signal_features": features,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "evidence_ref": f"aqi_sensor_{bus_id}_{pm2_5}ugm3",
            "lat": lat,
            "lon": lon,
            "simulation_run_id": simulation_run_id,
        }

aqi_anomaly_detector = AQIAnomalyDetector()
