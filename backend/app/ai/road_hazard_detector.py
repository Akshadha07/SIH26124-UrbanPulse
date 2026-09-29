"""
Road Hazard Computer Vision Detector
Model: road_hazard_prototype_v1 (1.0.0)

Simulates on-bus edge computer vision (YOLO-nano road defect detector)
processing optical camera frames to detect potholes and surface cracks,
extracting normalized bounding boxes and visual confidence scores.
"""

from typing import Dict, Any, Optional
from app.services.geo import haversine_distance

KNOWN_ROAD_DEFECTS = [
    {"name": "Alkapuri RC Dutt Road Pothole", "lat": 22.3118, "lon": 73.1720, "hazard_class": "pothole", "severity": 4.0},
    {"name": "Sayajigunj Station Road Crack", "lat": 22.3142, "lon": 73.1865, "hazard_class": "road_crack", "severity": 3.2},
]

class RoadHazardDetector:
    def __init__(self, proximity_threshold_meters: float = 45.0):
        self.model_name = "road_hazard_prototype_v1"
        self.model_version = "1.0.0"
        self.proximity_threshold_meters = proximity_threshold_meters

    def analyze(
        self,
        raw_camera_ref: Optional[str],
        bus_id: str = "UNKNOWN",
        lat: float = 0.0,
        lon: float = 0.0,
        raw_event_id: Optional[int] = None,
        simulation_run_id: Optional[str] = None,
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze a camera frame ping.
        Returns detection dict if a road defect is visually detected, else None.
        """
        # If camera reference is absent, no optical analysis possible
        if not raw_camera_ref and not extra_metadata:
            return None

        # Check explicit visual cues in metadata if provided (e.g. test injection or edge tag)
        if extra_metadata and extra_metadata.get("visual_defect_present"):
            hazard_class = extra_metadata.get("hazard_class", "pothole")
            severity = extra_metadata.get("severity", 3.8)
            confidence = extra_metadata.get("confidence", 0.88)
            box = extra_metadata.get("bounding_box", {"ymin": 0.58, "xmin": 0.42, "ymax": 0.74, "xmax": 0.61})
            return {
                "bus_id": bus_id,
                "raw_event_id": raw_event_id,
                "observation_type": "ROAD_HAZARD_CV",
                "hazard_class": hazard_class,
                "confidence": round(confidence, 3),
                "severity_score": round(severity, 2),
                "bounding_box": box,
                "signal_features": None,
                "model_name": self.model_name,
                "model_version": self.model_version,
                "evidence_ref": raw_camera_ref or f"frame_{bus_id}_{lat}_{lon}",
                "lat": lat,
                "lon": lon,
                "simulation_run_id": simulation_run_id,
            }

        # Check proximity to known corridor road defect locations
        for defect in KNOWN_ROAD_DEFECTS:
            dist = haversine_distance(lat, lon, defect["lat"], defect["lon"])
            if dist <= self.proximity_threshold_meters:
                # Defect in camera field of view
                # Bounding box coordinates normalized [0, 1]
                box = {
                    "ymin": 0.58,
                    "xmin": 0.42,
                    "ymax": 0.74,
                    "xmax": 0.61,
                }
                confidence = round(0.85 + (1.0 - (dist / self.proximity_threshold_meters)) * 0.10, 3)
                return {
                    "bus_id": bus_id,
                    "raw_event_id": raw_event_id,
                    "observation_type": "ROAD_HAZARD_CV",
                    "hazard_class": defect["hazard_class"],
                    "confidence": confidence,
                    "severity_score": defect["severity"],
                    "bounding_box": box,
                    "signal_features": None,
                    "model_name": self.model_name,
                    "model_version": self.model_version,
                    "evidence_ref": raw_camera_ref or f"frame_{bus_id}_{lat}_{lon}",
                    "lat": lat,
                    "lon": lon,
                    "simulation_run_id": simulation_run_id,
                }

        # Also support synthetic frame paths containing 'defect' or 'pothole'
        if raw_camera_ref and any(k in raw_camera_ref.lower() for k in ["pothole", "crack", "defect"]):
            box = {"ymin": 0.52, "xmin": 0.38, "ymax": 0.78, "xmax": 0.65}
            return {
                "bus_id": bus_id,
                "raw_event_id": raw_event_id,
                "observation_type": "ROAD_HAZARD_CV",
                "hazard_class": "pothole",
                "confidence": 0.89,
                "severity_score": 4.0,
                "bounding_box": box,
                "signal_features": None,
                "model_name": self.model_name,
                "model_version": self.model_version,
                "evidence_ref": raw_camera_ref,
                "lat": lat,
                "lon": lon,
                "simulation_run_id": simulation_run_id,
            }

        return None

road_hazard_detector = RoadHazardDetector()
