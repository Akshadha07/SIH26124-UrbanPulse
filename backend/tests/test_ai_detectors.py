"""
Unit Tests for Phase 2B AI Detectors
Tests:
- IMU Anomaly Detector (statistical shockwave filter)
- Road Hazard CV Detector (edge vision inference)
- Waterlogging Detector (multi-modal physical proxy rules)
- AQI Anomaly Detector (spatial particulate hotspot detection)
"""

import pytest
from app.ai.imu_detector import IMUAnomalyDetector
from app.ai.road_hazard_detector import RoadHazardDetector
from app.ai.waterlogging_detector import WaterloggingDetector
from app.ai.aqi_detector import AQIAnomalyDetector

def test_imu_detector_normal_road_no_anomaly():
    """Verify normal road surface with standard gravity does not trigger an anomaly."""
    detector = IMUAnomalyDetector()
    normal_window = {
        "ax": 0.05,
        "ay": -0.02,
        "az": 9.82,
        "peak_z": 9.95,
        "samples": [
            [0.02, -0.01, 9.80, 0.1],
            [-0.01, 0.02, 9.83, -0.1],
            [0.04, -0.02, 9.85, 0.2],
            [0.01, 0.01, 9.78, 0.0],
            [-0.03, -0.01, 9.82, -0.2],
        ],
    }
    result = detector.analyze(normal_window, bus_id="GJ-06-BT-101", lat=22.31, lon=73.18)
    assert result is None, "Normal road window should produce no anomaly observation"

def test_imu_detector_pothole_shock_detected():
    """Verify transient vertical shock excursion (> 1.45g) triggers an IMU anomaly."""
    detector = IMUAnomalyDetector()
    shock_window = {
        "ax": 0.5,
        "ay": -0.3,
        "az": 23.5,
        "peak_z": 23.5,
        "samples": [
            [0.02, -0.01, 9.81, 0.1],
            [0.10, -0.05, 10.20, 0.5],
            [1.50, -1.20, 23.50, 4.5],  # 2.4g shock impact
            [0.80, -0.40, 16.20, 2.1],
            [-0.03, 0.01, 9.85, -0.2],
        ],
    }
    result = detector.analyze(shock_window, bus_id="GJ-06-BT-101", lat=22.3118, lon=73.1720)
    assert result is not None
    assert result["observation_type"] == "IMU_ANOMALY"
    assert result["hazard_class"] == "pothole"
    assert result["severity_score"] >= 4.0
    assert result["confidence"] >= 0.85
    assert result["signal_features"]["peak_z_g"] >= 2.3
    assert result["signal_features"]["peak_z_ms2"] == 23.50
    assert result["model_name"] == "imu_statistical_v1"

def test_cv_detector_proximity_to_defect():
    """Verify camera detector identifies defect near known defect coordinate."""
    detector = RoadHazardDetector(proximity_threshold_meters=45.0)
    # Alkapuri defect is at (22.3118, 73.1720)
    # Query within 10 meters
    result = detector.analyze(
        raw_camera_ref="assets/frames/vadodara_route-102_f0042.jpg",
        bus_id="GJ-06-BT-103",
        lat=22.31185,
        lon=73.17205,
    )
    assert result is not None
    assert result["observation_type"] == "ROAD_HAZARD_CV"
    assert result["hazard_class"] == "pothole"
    assert result["confidence"] >= 0.80
    assert result["bounding_box"] is not None
    assert "ymin" in result["bounding_box"]
    assert result["model_name"] == "road_hazard_prototype_v1"

def test_cv_detector_normal_location_no_defect():
    """Verify camera detector returns None when bus is away from defects."""
    detector = RoadHazardDetector(proximity_threshold_meters=45.0)
    result = detector.analyze(
        raw_camera_ref="assets/frames/vadodara_route-102_f0042.jpg",
        bus_id="GJ-06-BT-103",
        lat=22.3500,  # Far away
        lon=73.2000,
    )
    assert result is None

def test_waterlogging_detector_critical_flood():
    """Verify extreme specular reflection and drag proxies trigger CRITICAL waterlogging."""
    detector = WaterloggingDetector()
    proxy = {
        "water_reflection_index": 0.89,
        "wheel_drag_coefficient": 0.82,
        "rainfall_rate_mm_hr": 65.0,
    }
    result = detector.analyze(proxy, bus_id="GJ-06-BT-105", lat=22.2965, lon=73.1750)
    assert result is not None
    assert result["observation_type"] == "WATERLOGGING_SEVERITY"
    assert result["hazard_class"] == "WATERLOGGING_CRITICAL"
    assert result["severity_score"] == 5.0
    assert result["confidence"] >= 0.95
    assert result["signal_features"]["waterlogging_severity"] == "CRITICAL"

def test_waterlogging_detector_dry_baseline():
    """Verify dry road proxies produce no waterlogging observation."""
    detector = WaterloggingDetector()
    dry_proxy = {
        "water_reflection_index": 0.08,
        "wheel_drag_coefficient": 0.04,
        "rainfall_rate_mm_hr": 0.0,
    }
    result = detector.analyze(dry_proxy, bus_id="GJ-06-BT-105", lat=22.2965, lon=73.1750)
    assert result is None

def test_aqi_detector_hotspot():
    """Verify PM2.5 exceedance triggers an AQI anomaly."""
    detector = AQIAnomalyDetector(pm25_hotspot_threshold=120.0)
    # Normal AQI reading
    assert detector.analyze(pm2_5=55.0) is None

    # Hotspot spike
    result = detector.analyze(pm2_5=175.0, pm10=260.0, co2=580.0, bus_id="GJ-06-BT-109", lat=22.26, lon=73.19)
    assert result is not None
    assert result["observation_type"] == "AQI_ANOMALY"
    assert result["hazard_class"] == "high_pm25"
    assert result["severity_score"] >= 4.0
    assert result["signal_features"]["exceedance_pm25"] == 55.0
