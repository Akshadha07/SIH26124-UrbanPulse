"""
Vadodara Transit Corridor Routes Definition
Contains realistic GPS tracks and waypoint sequences for public transit corridors across Vadodara, Gujarat.
Approved Corridors:
1. ROUTE-101: Sayajigunj Station - Central Corridor
2. ROUTE-102: Alkapuri Commercial Corridor (RC Dutt Road)
3. ROUTE-103: Akota Corridor (Includes Akota Underpass)
4. ROUTE-104: Fatehgunj - University Corridor
5. ROUTE-105: Makarpura Industrial Corridor (GIDC)
6. ROUTE-106: Waghodia Road Eastern Corridor
"""

from typing import List, Dict, Any

VADODARA_ROUTES: Dict[str, Dict[str, Any]] = {
    "ROUTE-101": {
        "route_id": "ROUTE-101",
        "route_name": "Sayajigunj Central Corridor",
        "color": "#3B82F6",  # Blue
        "corridor": "Sayajigunj",
        "traffic_tier": 1,
        "stops": [
            {"stop_name": "Vadodara Central Railway Station", "lat": 22.3108, "lon": 73.1812},
            {"stop_name": "Sayaji Baug Gate 1", "lat": 22.3142, "lon": 73.1865},
            {"stop_name": "Kala Ghoda Circle", "lat": 22.3155, "lon": 73.1918},
            {"stop_name": "Dak Bungalow Junction", "lat": 22.3120, "lon": 73.1945},
            {"stop_name": "Sayajigunj Bus Terminal", "lat": 22.3085, "lon": 73.1840},
        ],
        "waypoints": [
            (22.3108, 73.1812),
            (22.3125, 73.1838),
            (22.3142, 73.1865),
            (22.3150, 73.1890),
            (22.3155, 73.1918),
            (22.3140, 73.1932),
            (22.3120, 73.1945),
            (22.3100, 73.1890),
            (22.3085, 73.1840),
            (22.3108, 73.1812),
        ],
    },
    "ROUTE-102": {
        "route_id": "ROUTE-102",
        "route_name": "Alkapuri Commercial Express",
        "color": "#10B981",  # Green
        "corridor": "Alkapuri",
        "traffic_tier": 1,
        "stops": [
            {"stop_name": "Alkapuri Railway Station West", "lat": 22.3112, "lon": 73.1785},
            {"stop_name": "RC Dutt Road Central", "lat": 22.3118, "lon": 73.1720},
            {"stop_name": "Alkapuri Circle", "lat": 22.3125, "lon": 73.1670},
            {"stop_name": "Inorbit Mall Gorwa Rd", "lat": 22.3180, "lon": 73.1645},
            {"stop_name": "Arunachal Building Alkapuri", "lat": 22.3145, "lon": 73.1740},
        ],
        "waypoints": [
            (22.3112, 73.1785),
            (22.3115, 73.1750),
            (22.3118, 73.1720),
            (22.3122, 73.1690),
            (22.3125, 73.1670),
            (22.3150, 73.1655),
            (22.3180, 73.1645),
            (22.3160, 73.1700),
            (22.3145, 73.1740),
            (22.3112, 73.1785),
        ],
    },
    "ROUTE-103": {
        "route_id": "ROUTE-103",
        "route_name": "Akota - Mujmahuda Radial",
        "color": "#F59E0B",  # Amber
        "corridor": "Akota",
        "traffic_tier": 1,
        "stops": [
            {"stop_name": "Akota Stadium Circle", "lat": 22.2985, "lon": 73.1780},
            {"stop_name": "Akota Underpass North", "lat": 22.2965, "lon": 73.1750},
            {"stop_name": "Akota Underpass South", "lat": 22.2950, "lon": 73.1740},
            {"stop_name": "Mujmahuda Circle", "lat": 22.2885, "lon": 73.1725},
            {"stop_name": "Productivity Road Akota", "lat": 22.2940, "lon": 73.1770},
        ],
        "waypoints": [
            (22.2985, 73.1780),
            (22.2975, 73.1765),
            (22.2965, 73.1750),  # Underpass Critical Zone
            (22.2950, 73.1740),  # Underpass Critical Zone
            (22.2920, 73.1732),
            (22.2885, 73.1725),
            (22.2905, 73.1750),
            (22.2940, 73.1770),
            (22.2985, 73.1780),
        ],
    },
    "ROUTE-104": {
        "route_id": "ROUTE-104",
        "route_name": "Fatehgunj University Shuttle",
        "color": "#8B5CF6",  # Purple
        "corridor": "Fatehgunj",
        "traffic_tier": 2,
        "stops": [
            {"stop_name": "Sayaji Gunj North", "lat": 22.3160, "lon": 73.1850},
            {"stop_name": "MS University Pavilion", "lat": 22.3210, "lon": 73.1875},
            {"stop_name": "Fatehgunj Circle", "lat": 22.3255, "lon": 73.1905},
            {"stop_name": "Nizampura Crossing", "lat": 22.3320, "lon": 73.1880},
            {"stop_name": "Rosary High School", "lat": 22.3280, "lon": 73.1860},
        ],
        "waypoints": [
            (22.3160, 73.1850),
            (22.3185, 73.1862),
            (22.3210, 73.1875),
            (22.3235, 73.1890),
            (22.3255, 73.1905),
            (22.3290, 73.1895),
            (22.3320, 73.1880),
            (22.3280, 73.1860),
            (22.3220, 73.1852),
            (22.3160, 73.1850),
        ],
    },
    "ROUTE-105": {
        "route_id": "ROUTE-105",
        "route_name": "Makarpura GIDC Industrial Line",
        "color": "#EC4899",  # Pink
        "corridor": "Makarpura",
        "traffic_tier": 2,
        "stops": [
            {"stop_name": "Manjalpur Junction", "lat": 22.2700, "lon": 73.1920},
            {"stop_name": "Sussen Circle", "lat": 22.2580, "lon": 73.1940},
            {"stop_name": "Makarpura Bus Depot", "lat": 22.2480, "lon": 73.1965},
            {"stop_name": "GIDC Heavy Engineering Zone", "lat": 22.2390, "lon": 73.1980},
            {"stop_name": "Tarsali Bypass", "lat": 22.2550, "lon": 73.2040},
        ],
        "waypoints": [
            (22.2700, 73.1920),
            (22.2640, 73.1930),
            (22.2580, 73.1940),
            (22.2530, 73.1952),
            (22.2480, 73.1965),
            (22.2435, 73.1972),
            (22.2390, 73.1980),
            (22.2470, 73.2010),
            (22.2550, 73.2040),
            (22.2700, 73.1920),
        ],
    },
    "ROUTE-106": {
        "route_id": "ROUTE-106",
        "route_name": "Waghodia Road Eastern Arterial",
        "color": "#EF4444",  # Red
        "corridor": "Waghodia Road",
        "traffic_tier": 2,
        "stops": [
            {"stop_name": "Soma Talav Cross Road", "lat": 22.2980, "lon": 73.2180},
            {"stop_name": "Waghodia Chowkdi", "lat": 22.3020, "lon": 73.2320},
            {"stop_name": "Parul University Transit Stop", "lat": 22.3050, "lon": 73.2450},
            {"stop_name": "Gurukul Cross Road", "lat": 22.3090, "lon": 73.2360},
            {"stop_name": "Bapod Crossing", "lat": 22.3040, "lon": 73.2240},
        ],
        "waypoints": [
            (22.2980, 73.2180),
            (22.3000, 73.2250),
            (22.3020, 73.2320),
            (22.3035, 73.2385),
            (22.3050, 73.2450),
            (22.3070, 73.2405),
            (22.3090, 73.2360),
            (22.3065, 73.2300),
            (22.3040, 73.2240),
            (22.2980, 73.2180),
        ],
    },
}

def get_route(route_id: str) -> Dict[str, Any]:
    r = VADODARA_ROUTES.get(route_id, VADODARA_ROUTES["ROUTE-101"])
    route_dict = dict(r)
    route_dict["coordinates"] = [[lat, lon] for lat, lon in r["waypoints"]]
    return route_dict

def get_all_routes() -> List[Dict[str, Any]]:
    result = []
    for r in VADODARA_ROUTES.values():
        route_dict = dict(r)
        route_dict["coordinates"] = [[lat, lon] for lat, lon in r["waypoints"]]
        result.append(route_dict)
    return result
