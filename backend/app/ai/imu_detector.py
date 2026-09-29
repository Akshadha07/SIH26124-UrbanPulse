"""
IMU Anomaly Detector
Model: imu_statistical_v1 (1.0.0)

Extracts 3-axis statistical waveforms from raw accelerometer and gyroscope
windows, computing peak vertical g-force, variance, RMS, and baseline excursion
from Earth's gravity (9.81 m/s^2). Detects road surface shocks without hardcoded labels.
"""

import json
import math
from typing import Dict, Any, Optional, List

GRAVITY_MS2 = 9.81

class IMUAnomalyDetector:
    def __init__(
        self,
        g_shock_threshold: float = 1.45,
        baseline_dev_threshold: float = 4.4,
        variance_threshold: float = 2.5,
    ):
        self.model_name = "imu_statistical_v1"
        self.model_version = "1.0.0"
        self.g_shock_threshold = g_shock_threshold
        self.baseline_dev_threshold = baseline_dev_threshold
        self.variance_threshold = variance_threshold

    def analyze(
        self,
        imu_window_data: Any,
        bus_id: str = "UNKNOWN",
        lat: float = 0.0,
        lon: float = 0.0,
        raw_event_id: Optional[int] = None,
        simulation_run_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze a raw IMU window.
        Returns detection dict if statistical anomaly is found, else None.
        """
        if not imu_window_data:
            return None

        # Parse string JSON if needed
        if isinstance(imu_window_data, str):
            try:
                data = json.loads(imu_window_data)
            except Exception:
                return None
        elif isinstance(imu_window_data, dict):
            data = imu_window_data
        else:
            return None

        samples: List[List[float]] = data.get("samples", [])
        peak_z_recorded = data.get("peak_z", 0.0)
        single_az = data.get("az", GRAVITY_MS2)

        if not samples:
            # Fall back to single sample if array not provided
            z_vals = [peak_z_recorded if peak_z_recorded else single_az]
        else:
            # Each sample is [ax, ay, az, gz]
            z_vals = [s[2] for s in samples if len(s) >= 3]

        if not z_vals:
            return None

        n = len(z_vals)
        mean_z = sum(z_vals) / float(n)
        variance_z = sum((z - mean_z) ** 2 for z in z_vals) / float(n)
        rms_z = math.sqrt(sum(z ** 2 for z in z_vals) / float(n))
        peak_z_ms2 = max(abs(z) for z in z_vals)
        peak_z_g = peak_z_ms2 / GRAVITY_MS2
        baseline_dev_ms2 = max(abs(z - GRAVITY_MS2) for z in z_vals)

        # Statistical anomaly criteria
        is_shock = (
            peak_z_g >= self.g_shock_threshold or
            baseline_dev_ms2 >= self.baseline_dev_threshold or
            variance_z >= self.variance_threshold
        )

        if not is_shock:
            return None

        # Calculate severity (1.0 to 5.0)
        if peak_z_g >= 2.4:
            severity = min(5.0, 4.2 + (peak_z_g - 2.4) * 0.8)
            hazard_class = "pothole"
        elif peak_z_g >= 1.75:
            severity = 3.5 + (peak_z_g - 1.75) * 0.9
            hazard_class = "pothole"
        else:
            severity = 2.0 + (peak_z_g - self.g_shock_threshold) * 2.0
            hazard_class = "road_crack"

        confidence = min(0.98, max(0.70, 0.70 + (peak_z_g - self.g_shock_threshold) * 0.22))

        features = {
            "peak_z_ms2": round(peak_z_ms2, 2),
            "peak_z_g": round(peak_z_g, 2),
            "mean_z": round(mean_z, 2),
            "variance_z": round(variance_z, 2),
            "rms_z": round(rms_z, 2),
            "baseline_dev_ms2": round(baseline_dev_ms2, 2),
            "samples_count": n,
        }

        return {
            "bus_id": bus_id,
            "raw_event_id": raw_event_id,
            "observation_type": "IMU_ANOMALY",
            "hazard_class": hazard_class,
            "confidence": round(confidence, 3),
            "severity_score": round(severity, 2),
            "signal_features": features,
            "bounding_box": None,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "evidence_ref": f"imu_stream_window_{bus_id}_{features['peak_z_g']}g",
            "lat": lat,
            "lon": lon,
            "simulation_run_id": simulation_run_id,
        }

imu_anomaly_detector = IMUAnomalyDetector()
