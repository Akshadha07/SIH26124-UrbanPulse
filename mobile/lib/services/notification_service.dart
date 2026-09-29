import 'dart:async';
import '../models/hazard.dart';

class ProximityAlert {
  final HazardModel hazard;
  final String title;
  final String message;
  final bool isCritical;
  final DateTime timestamp;

  ProximityAlert({
    required this.hazard,
    required this.title,
    required this.message,
    required this.isCritical,
    required this.timestamp,
  });
}

class NotificationService {
  static final NotificationService _instance = NotificationService._internal();
  factory NotificationService() => _instance;
  NotificationService._internal();

  final StreamController<ProximityAlert> _alertController =
      StreamController<ProximityAlert>.broadcast();
  Stream<ProximityAlert> get alertStream => _alertController.stream;

  ProximityAlert? _latestAlert;
  ProximityAlert? get latestAlert => _latestAlert;

  void triggerProximityWarning(HazardModel hazard) {
    final bool isDisaster = hazard.isCriticalWaterlogging;
    final String title = isDisaster
        ? '🚨 CRITICAL ROAD SUBMERSION AHEAD'
        : '⚠️ ROAD HAZARD WARNING';
    final String message = isDisaster
        ? 'Flash waterlogging detected ' +
            hazard.distanceMeters.round().toString() +
            'm ahead at ' +
            (hazard.addressHint ?? 'current corridor') +
            '. VMC emergency response activated.'
        : hazard.hazardType.toUpperCase() +
            ' reported ' +
            hazard.distanceMeters.round().toString() +
            'm ahead. Confirmed by ' +
            hazard.distinctBusCount.toString() +
            ' transit passes.';

    final alert = ProximityAlert(
      hazard: hazard,
      title: title,
      message: message,
      isCritical: isDisaster,
      timestamp: DateTime.now(),
    );

    _latestAlert = alert;
    _alertController.add(alert);
  }

  void dismissAlert() {
    _latestAlert = null;
  }
}
