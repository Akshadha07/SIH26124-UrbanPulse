import 'dart:math';
import '../config/api_config.dart';

class LocationService {
  static final LocationService _instance = LocationService._internal();
  factory LocationService() => _instance;
  LocationService._internal();

  double _currentLat = ApiConfig.defaultLat;
  double _currentLon = ApiConfig.defaultLon;
  String _locationName = 'Sayajigunj, Vadodara';

  double get currentLat => _currentLat;
  double get currentLon => _currentLon;
  String get locationName => _locationName;

  void setLocation(double lat, double lon, {String? name}) {
    _currentLat = lat;
    _currentLon = lon;
    if (name != null) {
      _locationName = name;
    }
  }

  // Haversine distance in meters
  static double calculateDistanceMeters(
    double lat1,
    double lon1,
    double lat2,
    double lon2,
  ) {
    const double r = 6371000.0; // Earth radius in meters
    final double phi1 = lat1 * pi / 180.0;
    final double phi2 = lat2 * pi / 180.0;
    final double dPhi = (lat2 - lat1) * pi / 180.0;
    final double dLambda = (lon2 - lon1) * pi / 180.0;

    final double a = sin(dPhi / 2.0) * sin(dPhi / 2.0) +
        cos(phi1) * cos(phi2) * sin(dLambda / 2.0) * sin(dLambda / 2.0);
    final double c = 2.0 * atan2(sqrt(a), sqrt(1.0 - a));

    return r * c;
  }

  static String formatDistance(double meters) {
    if (meters < 1000.0) {
      return meters.round().toString() + ' m';
    } else {
      return (meters / 1000.0).toStringAsFixed(1) + ' km';
    }
  }
}
