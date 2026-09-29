class AqiPointModel {
  final int id;
  final String busId;
  final double lat;
  final double lon;
  final double pm25;
  final double? pm10;
  final double? co2;
  final double aqiValue;
  final String category;
  final DateTime timestamp;

  AqiPointModel({
    required this.id,
    required this.busId,
    required this.lat,
    required this.lon,
    required this.pm25,
    this.pm10,
    this.co2,
    required this.aqiValue,
    required this.category,
    required this.timestamp,
  });

  factory AqiPointModel.fromJson(Map<String, dynamic> json) {
    return AqiPointModel(
      id: json['id'] ?? 0,
      busId: json['bus_id'] ?? '',
      lat: (json['lat'] as num?)?.toDouble() ?? 0.0,
      lon: (json['lon'] as num?)?.toDouble() ?? 0.0,
      pm25: (json['pm2_5'] as num?)?.toDouble() ?? 0.0,
      pm10: (json['pm10'] as num?)?.toDouble(),
      co2: (json['co2'] as num?)?.toDouble(),
      aqiValue: (json['aqi_value'] as num?)?.toDouble() ?? 0.0,
      category: json['category'] ?? 'Good',
      timestamp: json['timestamp'] != null
          ? DateTime.tryParse(json['timestamp']) ?? DateTime.now()
          : DateTime.now(),
    );
  }
}
