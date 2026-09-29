class CrowdPredictionModel {
  final String routeId;
  final String routeName;
  final String? busId;
  final String currentOccupancyLevel;
  final int currentCrowdCount;
  final int capacity;
  final String predictedOccupancyLevel;
  final double predictionConfidence;
  final String trend;
  final int? etaMinutes;
  final String? nextStop;

  CrowdPredictionModel({
    required this.routeId,
    required this.routeName,
    this.busId,
    required this.currentOccupancyLevel,
    required this.currentCrowdCount,
    required this.capacity,
    required this.predictedOccupancyLevel,
    required this.predictionConfidence,
    required this.trend,
    this.etaMinutes,
    this.nextStop,
  });

  factory CrowdPredictionModel.fromJson(Map<String, dynamic> json) {
    return CrowdPredictionModel(
      routeId: json['route_id'] ?? '',
      routeName: json['route_name'] ?? 'Transit Corridor',
      busId: json['bus_id'],
      currentOccupancyLevel: json['current_occupancy_level'] ?? 'low',
      currentCrowdCount: (json['current_crowd_count'] as num?)?.toInt() ?? 0,
      capacity: (json['capacity'] as num?)?.toInt() ?? 40,
      predictedOccupancyLevel: json['predicted_occupancy_level'] ?? 'low',
      predictionConfidence:
          (json['prediction_confidence'] as num?)?.toDouble() ?? 0.9,
      trend: json['trend'] ?? 'STABLE',
      etaMinutes: (json['eta_minutes'] as num?)?.toInt(),
      nextStop: json['next_stop'],
    );
  }
}
