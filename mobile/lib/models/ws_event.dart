class WsEnvelope {
  final String eventType;
  final DateTime timestamp;
  final Map<String, dynamic> data;

  WsEnvelope({
    required this.eventType,
    required this.timestamp,
    required this.data,
  });

  factory WsEnvelope.fromJson(Map<String, dynamic> json) {
    return WsEnvelope(
      eventType: json['event_type'] ?? '',
      timestamp: json['timestamp'] != null
          ? DateTime.tryParse(json['timestamp']) ?? DateTime.now()
          : DateTime.now(),
      data: json['data'] as Map<String, dynamic>? ?? {},
    );
  }
}
