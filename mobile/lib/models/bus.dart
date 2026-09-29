class BusModel {
  final String busId;
  final String routeId;
  final String routeName;
  final double lat;
  final double lon;
  final double speed;
  final double heading;
  final String occupancyLevel;
  final int crowdCount;
  final int capacity;
  final String status;
  final DateTime lastUpdated;

  BusModel({
    required this.busId,
    required this.routeId,
    required this.routeName,
    required this.lat,
    required this.lon,
    required this.speed,
    required this.heading,
    required this.occupancyLevel,
    required this.crowdCount,
    required this.capacity,
    required this.status,
    required this.lastUpdated,
  });

  factory BusModel.fromJson(Map<String, dynamic> json) {
    return BusModel(
      busId: json['bus_id'] ?? '',
      routeId: json['route_id'] ?? '',
      routeName: json['route_name'] ?? 'Transit Route',
      lat: (json['lat'] as num?)?.toDouble() ?? 0.0,
      lon: (json['lon'] as num?)?.toDouble() ?? 0.0,
      speed: (json['speed'] as num?)?.toDouble() ?? 0.0,
      heading: (json['heading'] as num?)?.toDouble() ?? 0.0,
      occupancyLevel: json['occupancy_level'] ?? 'low',
      crowdCount: (json['crowd_count'] as num?)?.toInt() ?? 0,
      capacity: (json['capacity'] as num?)?.toInt() ?? 40,
      status: json['status'] ?? 'active',
      lastUpdated: json['last_updated'] != null
          ? DateTime.tryParse(json['last_updated']) ?? DateTime.now()
          : DateTime.now(),
    );
  }

  double get occupancyPercentage =>
      capacity > 0 ? (crowdCount / capacity).clamp(0.0, 1.0) : 0.0;
}

class RouteWaypoint {
  final double lat;
  final double lon;
  final String? stopName;

  RouteWaypoint({required this.lat, required this.lon, this.stopName});

  factory RouteWaypoint.fromJson(Map<String, dynamic> json) {
    return RouteWaypoint(
      lat: (json['lat'] as num?)?.toDouble() ?? 0.0,
      lon: (json['lon'] as num?)?.toDouble() ?? 0.0,
      stopName: json['stop_name'],
    );
  }
}

class RouteModel {
  final String routeId;
  final String routeName;
  final String color;
  final List<RouteWaypoint> stops;
  final List<List<double>> coordinates;

  RouteModel({
    required this.routeId,
    required this.routeName,
    required this.color,
    required this.stops,
    required this.coordinates,
  });

  factory RouteModel.fromJson(Map<String, dynamic> json) {
    var rawStops = json['stops'] as List? ?? [];
    var rawCoords = json['coordinates'] as List? ?? [];

    return RouteModel(
      routeId: json['route_id'] ?? '',
      routeName: json['route_name'] ?? '',
      color: json['color'] ?? '#3B82F6',
      stops: rawStops.map((s) => RouteWaypoint.fromJson(s)).toList(),
      coordinates: rawCoords.map((c) {
        var coordList = c as List;
        return [
          (coordList[0] as num).toDouble(),
          (coordList[1] as num).toDouble()
        ];
      }).toList(),
    );
  }
}
