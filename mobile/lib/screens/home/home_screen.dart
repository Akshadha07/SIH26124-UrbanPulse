import 'package:flutter/material.dart';
import '../../models/bus.dart';
import '../../models/hazard.dart';
import '../../models/aqi.dart';
import '../../services/api_service.dart';
import '../../services/location_service.dart';
import '../../services/notification_service.dart';
import '../../services/websocket_service.dart';
import '../../theme/app_colors.dart';
import '../../widgets/simulation_badge.dart';
import '../../widgets/bus_card.dart';
import '../../widgets/hazard_card.dart';
import '../../widgets/aqi_card.dart';
import '../../widgets/empty_state.dart';
import '../../widgets/proximity_banner.dart';
import '../journey/journey_screen.dart';
import '../aqi/aqi_screen.dart';
import '../settings/settings_screen.dart';

class HomeScreen extends StatefulWidget {
  final Function(int) onNavigateTab;

  const HomeScreen({Key? key, required this.onNavigateTab}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final ApiService _api = ApiService();
  final LocationService _location = LocationService();
  final WebSocketService _ws = WebSocketService();
  final NotificationService _notifications = NotificationService();

  bool _loading = true;
  String? _error;
  List<BusModel> _buses = [];
  List<HazardModel> _hazards = [];
  List<AqiPointModel> _aqiPoints = [];
  ProximityAlert? _activeBanner;

  @override
  void initState() {
    super.initState();
    _fetchData();

    // Subscribe to WebSocket events
    _ws.stream.listen((envelope) {
      if (envelope.eventType == 'bus_moved') {
        _refreshBusesSilently();
      } else if (envelope.eventType == 'incident_detected' ||
          envelope.eventType == 'incident_confirmed') {
        _refreshHazardsSilently();
      } else if (envelope.eventType == 'waterlogging_alert') {
        _handleWaterloggingEmergency(envelope.data);
      }
    });

    // Subscribe to proximity alerts
    _notifications.alertStream.listen((alert) {
      if (mounted) {
        setState(() {
          _activeBanner = alert;
        });
      }
    });
  }

  void _handleWaterloggingEmergency(Map<String, dynamic> data) {
    _refreshHazardsSilently();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        backgroundColor: AppColors.danger,
        content: Row(
          children: const [
            Icon(Icons.flood, color: Colors.white, size: 20),
            SizedBox(width: 10),
            Expanded(
              child: Text(
                'CRITICAL FLASH WATERLOGGING: Disaster protocol activated at Akota Underpass!',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
              ),
            ),
          ],
        ),
        duration: const Duration(seconds: 5),
      ),
    );
  }

  Future<void> _fetchData() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final results = await Future.wait([
        _api.getLiveBuses(),
        _api.getNearbyHazards(lat: _location.currentLat, lon: _location.currentLon),
        _api.getLiveAqi(limit: 5),
      ]);

      if (mounted) {
        setState(() {
          _buses = results[0] as List<BusModel>;
          _hazards = results[1] as List<HazardModel>;
          _aqiPoints = results[2] as List<AqiPointModel>;
          _loading = false;
        });

        // Check if any nearby hazard is within warning range (< 500m or disaster)
        for (var h in _hazards) {
          if (h.isCriticalWaterlogging || h.distanceMeters < 400.0) {
            _notifications.triggerProximityWarning(h);
            break;
          }
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _loading = false;
        });
      }
    }
  }

  Future<void> _refreshBusesSilently() async {
    try {
      final buses = await _api.getLiveBuses();
      if (mounted) {
        setState(() {
          _buses = buses;
        });
      }
    } catch (_) {}
  }

  Future<void> _refreshHazardsSilently() async {
    try {
      final hazards = await _api.getNearbyHazards(
        lat: _location.currentLat,
        lon: _location.currentLon,
      );
      if (mounted) {
        setState(() {
          _hazards = hazards;
        });
      }
    } catch (_) {}
  }

  String _getTimeGreeting() {
    final hour = DateTime.now().hour;
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Scaffold(
        body: Center(
          child: CircularProgressIndicator(color: AppColors.primaryLight),
        ),
      );
    }

    if (_error != null) {
      return Scaffold(
        body: ErrorStateWidget(
          message: _error!,
          onRetry: _fetchData,
        ),
      );
    }

    final BusModel? nextBus = _buses.isNotEmpty ? _buses.first : null;
    final HazardModel? topHazard = _hazards.isNotEmpty ? _hazards.first : null;
    final AqiPointModel? topAqi = _aqiPoints.isNotEmpty ? _aqiPoints.first : null;

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Text('BEL UrbanPulse'),
                const SizedBox(width: 8),
                const SimulationBadge(),
              ],
            ),
            Row(
              children: [
                const Icon(Icons.location_on, size: 11, color: AppColors.cyan),
                const SizedBox(width: 3),
                Text(
                  _location.locationName,
                  style: const TextStyle(
                    fontSize: 11,
                    color: AppColors.textSecondary,
                    fontWeight: FontWeight.normal,
                  ),
                ),
              ],
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings_outlined, size: 20),
            tooltip: 'Settings & System Info',
            onPressed: () {
              Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => const SettingsScreen()),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.refresh, size: 20),
            tooltip: 'Refresh',
            onPressed: _fetchData,
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _fetchData,
        color: AppColors.primaryLight,
        child: ListView(
          padding: const EdgeInsets.only(bottom: 24),
          children: [
            // Floating Proximity Alert Banner if active
            if (_activeBanner != null)
              ProximityBanner(
                alert: _activeBanner!,
                onDismiss: () {
                  setState(() {
                    _activeBanner = null;
                  });
                },
                onTap: () {
                  widget.onNavigateTab(2); // Jump to Hazard alerts
                },
              ),

            // Greeting Header
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Text(
                _getTimeGreeting() + ', Vadodara commuter',
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: AppColors.textPrimary,
                ),
              ),
            ),

            // Quick Actions Bar
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Row(
                children: [
                  _buildQuickAction(
                    icon: Icons.directions_bus,
                    label: 'Live Buses',
                    color: AppColors.primaryLight,
                    onTap: () => widget.onNavigateTab(1),
                  ),
                  const SizedBox(width: 10),
                  _buildQuickAction(
                    icon: Icons.alt_route,
                    label: 'Journey',
                    color: AppColors.cyan,
                    onTap: () {
                      Navigator.of(context).push(
                        MaterialPageRoute(builder: (_) => const JourneyScreen()),
                      );
                    },
                  ),
                  const SizedBox(width: 10),
                  _buildQuickAction(
                    icon: Icons.warning_amber_rounded,
                    label: 'Hazards',
                    color: AppColors.warning,
                    onTap: () => widget.onNavigateTab(2),
                  ),
                  const SizedBox(width: 10),
                  _buildQuickAction(
                    icon: Icons.camera_alt_outlined,
                    label: 'Report',
                    color: AppColors.success,
                    onTap: () => widget.onNavigateTab(3),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 12),

            // Next Bus Section
            _buildSectionHeader(
              title: 'NEXT ARRIVING BUS',
              actionLabel: 'View All (' + _buses.length.toString() + ')',
              onAction: () => widget.onNavigateTab(1),
            ),
            if (nextBus != null)
              BusCard(
                bus: nextBus,
                onTap: () => widget.onNavigateTab(1),
              )
            else
              const Padding(
                padding: EdgeInsets.symmetric(horizontal: 16),
                child: Text('No buses currently active on this corridor.'),
              ),

            const SizedBox(height: 16),

            // Hazards Along Commute Section
            _buildSectionHeader(
              title: 'ROAD HAZARD ALERTS NEARBY',
              actionLabel: 'View All (' + _hazards.length.toString() + ')',
              onAction: () => widget.onNavigateTab(2),
            ),
            if (topHazard != null)
              HazardCard(
                hazard: topHazard,
                onTap: () => widget.onNavigateTab(2),
              )
            else
              const Padding(
                padding: EdgeInsets.symmetric(horizontal: 16),
                child: Text(
                  'No hazards reported within 3 km. Road conditions nominal.',
                  style: TextStyle(color: AppColors.textMuted, fontSize: 12),
                ),
              ),

            const SizedBox(height: 16),

            // Air Quality Section
            _buildSectionHeader(
              title: 'AIR QUALITY INDEX (AQI)',
              actionLabel: 'Clean Commute',
              onAction: () {
                Navigator.of(context).push(
                  MaterialPageRoute(builder: (_) => const AqiScreen()),
                );
              },
            ),
            if (topAqi != null)
              InkWell(
                onTap: () {
                  Navigator.of(context).push(
                    MaterialPageRoute(builder: (_) => const AqiScreen()),
                  );
                },
                child: AqiCard(aqi: topAqi),
              )
            else
              const Padding(
                padding: EdgeInsets.symmetric(horizontal: 16),
                child: Text(
                  'Air quality sensors updating...',
                  style: TextStyle(color: AppColors.textMuted, fontSize: 12),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildQuickAction({
    required IconData icon,
    required String label,
    required Color color,
    required VoidCallback onTap,
  }) {
    return Expanded(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 12),
          decoration: BoxDecoration(
            color: AppColors.surface,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: AppColors.border),
          ),
          child: Column(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.12),
                  shape: BoxShape.circle,
                ),
                child: Icon(icon, size: 20, color: color),
              ),
              const SizedBox(height: 6),
              Text(
                label,
                style: const TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w600,
                  color: AppColors.textPrimary,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSectionHeader({
    required String title,
    required String actionLabel,
    required VoidCallback onAction,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            title,
            style: const TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w700,
              color: AppColors.textMuted,
              letterSpacing: 0.8,
            ),
          ),
          InkWell(
            onTap: onAction,
            child: Text(
              actionLabel,
              style: const TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                color: AppColors.primaryLight,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
