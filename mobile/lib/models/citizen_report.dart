class CitizenReportModel {
  final int id;
  final String category;
  final double lat;
  final double lon;
  final String? description;
  final String? photoUrl;
  final String status;
  final DateTime createdAt;

  CitizenReportModel({
    required this.id,
    required this.category,
    required this.lat,
    required this.lon,
    this.description,
    this.photoUrl,
    required this.status,
    required this.createdAt,
  });

  factory CitizenReportModel.fromJson(Map<String, dynamic> json) {
    return CitizenReportModel(
      id: json['id'] ?? 0,
      category: json['category'] ?? 'other',
      lat: (json['lat'] as num?)?.toDouble() ?? 0.0,
      lon: (json['lon'] as num?)?.toDouble() ?? 0.0,
      description: json['description'],
      photoUrl: json['photo_url'],
      status: json['status'] ?? 'SUBMITTED',
      createdAt: json['created_at'] != null
          ? DateTime.tryParse(json['created_at']) ?? DateTime.now()
          : DateTime.now(),
    );
  }
}
