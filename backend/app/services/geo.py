import math
from typing import Tuple

EARTH_RADIUS_METERS = 6371000.0

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on the Earth
    in meters using the Haversine formula.
    """
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return EARTH_RADIUS_METERS * c

def calculate_heading(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate forward compass heading (0-360 degrees) from point 1 to point 2."""
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_lambda = math.radians(lon2 - lon1)

    y = math.sin(delta_lambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda)
    initial_bearing = math.atan2(y, x)
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360.0) % 360.0
    return round(compass_bearing, 1)

def interpolate(p1: Tuple[float, float], p2: Tuple[float, float], fraction: float) -> Tuple[float, float]:
    """Interpolate between two (lat, lon) coordinates by fraction [0.0, 1.0]."""
    lat = p1[0] + (p2[0] - p1[0]) * fraction
    lon = p1[1] + (p2[1] - p1[1]) * fraction
    return (lat, lon)
