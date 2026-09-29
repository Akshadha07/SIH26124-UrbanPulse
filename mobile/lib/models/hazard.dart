class HazardModel {
  final int id;
  final String hazardType;
  final double lat;
  final double lon;
  final double distanceMeters;
  final double severity;
  final double confidence;
  final double priorityScore;
  final int confirmationCount;
  final int distinctBusCount;
  final bool isConfirmed;
  final String status;
  final String? waterloggingSeverity;
  final String? addressHint;

  HazardModel({
    required this.id,
    required this.hazardType,
    required this.lat,
    required this.lon,
    required this.distanceMeters,
    required this.severity,
    required this.confidence,
    required this.priorityScore,
    required this.confirmationCount,
    required this.distinctBusCount,
    required this.isConfirmed,
    required this.status,
    this.waterloggingSeverity,
    this.addressHint,
  });

  factory HazardModel.fromJson(Map<String, dynamic> json) {
    return HazardModel(
      id: json['id'] ?? 0,
      hazardType: json['hazard_type'] ?? 'pothole',
      lat: (json['lat'] as num?)?.toDouble() ?? 0.0,
      lon: (json['lon'] as num?)?.toDouble() ?? 0.0,
      distanceMeters: (json['distance_meters'] as num?)?.toDouble() ?? 0.0,
      severity: (json['severity'] as num?)?.toDouble() ?? 1.0,
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0.8,
      priorityScore: (json['priority_score'] as num?)?.toDouble() ?? 50.0,
      confirmationCount: (json['confirmation_count'] as num?)?.toInt() ?? 1,
      distinctBusCount: (json['distinct_bus_count'] as num?)?.toInt() ?? 1,
      isConfirmed: json['is_confirmed'] ?? false,
      status: json['status'] ?? 'reported',
      waterloggingSeverity: json['waterlogging_severity'],
      addressHint: json['address_hint'],
    );
  }

  bool get isCriticalWaterlogging =>
      hazardType.toUpperCase().contains('WATERLOGGING') &&
      (waterloggingSeverity == 'CRITICAL' ||
          status.toUpperCase().contains('DISASTER') ||
          priorityScore >= 90.0);

  bool get isCorroborated => distinctBusCount > 1 || isConfirmed;
}
