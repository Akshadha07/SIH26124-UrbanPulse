import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';
import '../models/bus.dart';
import '../models/hazard.dart';
import '../models/aqi.dart';
import '../models/crowd_prediction.dart';
import '../models/citizen_report.dart';

class ApiService {
  // Singleton pattern
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  final http.Client _client = http.Client();

  Future<List<BusModel>> getLiveBuses() async {
    final uri = Uri.parse(ApiConfig.baseUrl + '/fleet/live');
    final response = await _client.get(uri);
    if (response.statusCode == 200) {
      final List data = jsonDecode(response.body);
      return data.map((json) => BusModel.fromJson(json)).toList();
    }
    throw Exception('Failed to fetch live fleet telemetry: ' + response.statusCode.toString());
  }

  Future<List<RouteModel>> getRoutes() async {
    final uri = Uri.parse(ApiConfig.baseUrl + '/fleet/routes');
    final response = await _client.get(uri);
    if (response.statusCode == 200) {
      final List data = jsonDecode(response.body);
      return data.map((json) => RouteModel.fromJson(json)).toList();
    }
    throw Exception('Failed to fetch transit routes: ' + response.statusCode.toString());
  }

  Future<List<HazardModel>> getNearbyHazards({
    double lat = ApiConfig.defaultLat,
    double lon = ApiConfig.defaultLon,
    double radiusMeters = 3000.0,
    double minPriority = 0.0,
  }) async {
    final uri = Uri.parse(ApiConfig.baseUrl +
        '/citizen/hazards/nearby?lat=' +
        lat.toString() +
        '&lon=' +
        lon.toString() +
        '&radius_meters=' +
        radiusMeters.toString() +
        '&min_priority=' +
        minPriority.toString());

    final response = await _client.get(uri);
    if (response.statusCode == 200) {
      final List data = jsonDecode(response.body);
      return data.map((json) => HazardModel.fromJson(json)).toList();
    }
    throw Exception('Failed to fetch nearby hazards: ' + response.statusCode.toString());
  }

  Future<List<CrowdPredictionModel>> getCrowdPredictions({
    String? routeId,
    String? busId,
  }) async {
    String query = '';
    if (routeId != null) query += '?route_id=' + routeId;
    if (busId != null) {
      query += (query.isEmpty ? '?' : '&') + 'bus_id=' + busId;
    }

    final uri = Uri.parse(ApiConfig.baseUrl + '/citizen/bus/crowd-prediction' + query);
    final response = await _client.get(uri);
    if (response.statusCode == 200) {
      final List data = jsonDecode(response.body);
      return data.map((json) => CrowdPredictionModel.fromJson(json)).toList();
    }
    throw Exception('Failed to fetch crowd predictions: ' + response.statusCode.toString());
  }

  Future<List<AqiPointModel>> getLiveAqi({int limit = 50}) async {
    final uri = Uri.parse(ApiConfig.baseUrl + '/aqi/live?limit=' + limit.toString());
    final response = await _client.get(uri);
    if (response.statusCode == 200) {
      final List data = jsonDecode(response.body);
      return data.map((json) => AqiPointModel.fromJson(json)).toList();
    }
    throw Exception('Failed to fetch air quality readings: ' + response.statusCode.toString());
  }

  Future<CitizenReportModel> submitCitizenReport({
    required String category,
    required double lat,
    required double lon,
    String? description,
    String? photoBase64,
    String? photoUrl,
    String? deviceIdHash,
  }) async {
    final uri = Uri.parse(ApiConfig.baseUrl + '/citizen/report');
    final payload = {
      'category': category,
      'lat': lat,
      'lon': lon,
      'description': description,
      'photo_base64': photoBase64,
      'photo_url': photoUrl,
      'device_id_hash': deviceIdHash,
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    );

    if (response.statusCode == 201) {
      return CitizenReportModel.fromJson(jsonDecode(response.body));
    }
    throw Exception('Failed to submit citizen report: ' + response.statusCode.toString());
  }

  Future<List<CitizenReportModel>> getCitizenReports({String? deviceIdHash}) async {
    String query = deviceIdHash != null ? '?device_id_hash=' + deviceIdHash : '';
    final uri = Uri.parse(ApiConfig.baseUrl + '/citizen/reports' + query);
    final response = await _client.get(uri);
    if (response.statusCode == 200) {
      final List data = jsonDecode(response.body);
      return data.map((json) => CitizenReportModel.fromJson(json)).toList();
    }
    throw Exception('Failed to fetch report history: ' + response.statusCode.toString());
  }
}
