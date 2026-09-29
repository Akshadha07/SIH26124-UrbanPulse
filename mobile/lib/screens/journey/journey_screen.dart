import 'package:flutter/material.dart';
import '../../models/bus.dart';
import '../../models/crowd_prediction.dart';
import '../../services/api_service.dart';
import '../../theme/app_colors.dart';
import '../../widgets/simulation_badge.dart';
import '../../widgets/status_badge.dart';
import '../../widgets/empty_state.dart';

class JourneyScreen extends StatefulWidget {
  const JourneyScreen({super.key});

  @override
  State<JourneyScreen> createState() => _JourneyScreenState();
}

class _JourneyScreenState extends State<JourneyScreen> {
  final ApiService _api = ApiService();

  bool _loading = true;
  String? _error;
  List<RouteModel> _routes = [];
  List<BusModel> _buses = [];
  List<CrowdPredictionModel> _predictions = [];
  String? _selectedRouteId;
  String _crowdFilter = 'All';

  @override
  void initState() {
    super.initState();
    _loadJourneyData();
  }

  Future<void> _loadJourneyData() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final results = await Future.wait([
        _api.getRoutes(),
        _api.getLiveBuses(),
        _api.getCrowdPredictions(),
      ]);

      if (!mounted) return;

      final routes = results[0] as List<RouteModel>;
      final buses = results[1] as List<BusModel>;
      final predictions = results[2] as List<CrowdPredictionModel>;

      setState(() {
        _routes = routes;
        _buses = buses;
        _predictions = predictions;
        _loading = false;
        if (_selectedRouteId == null && routes.isNotEmpty) {
          _selectedRouteId = routes.first.routeId;
        }
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString();
        _loading = false;
      });
    }
  }

  Color _parseHexColor(String hex) {
    var cleaned = hex.replaceAll('#', '').trim();
    if (cleaned.length == 6) {
      cleaned = 'FF' + cleaned;
    }
    try {
      return Color(int.parse(cleaned, radix: 16));
    } catch (_) {
      return AppColors.primaryLight;
    }
  }

  RouteModel? get _selectedRoute {
    if (_selectedRouteId == null) return null;
    try {
      return _routes.firstWhere((r) => r.routeId == _selectedRouteId);
    } catch (_) {
      return _routes.isNotEmpty ? _routes.first : null;
    }
  }

  List<BusModel> get _busesOnSelectedRoute {
    if (_selectedRouteId == null) return [];
    return _buses.where((b) => b.routeId == _selectedRouteId).toList();
  }

  CrowdPredictionModel? get _predictionForSelectedRoute {
    if (_selectedRouteId == null) return null;
    try {
      return _predictions.firstWhere((p) => p.routeId == _selectedRouteId);
    } catch (_) {
      return null;
    }
  }

  List<RouteModel> get _filteredRoutes {
    if (_crowdFilter == 'All') return _routes;

    return _routes.where((route) {
      final busesOnRoute = _buses.where((b) => b.routeId == route.routeId);
      if (busesOnRoute.isEmpty) return false;

      final anyMatch = busesOnRoute.any((b) {
        final lvl = b.occupancyLevel.toLowerCase();
        if (_crowdFilter == 'Low') return lvl == 'low';
        if (_crowdFilter == 'Moderate') return lvl == 'moderate' || lvl == 'medium';
        if (_crowdFilter == 'Crowded') return lvl == 'high' || lvl == 'crowded' || lvl == 'full';
        return true;
      });
      return anyMatch;
    }).toList();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.background,
        elevation: 0,
        title: Row(
          children: const [
            Text('Journey Planner'),
            SizedBox(width: 8),
            SimulationBadge(),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Refresh Routes',
            onPressed: _loading ? null : _loadJourneyData,
          ),
        ],
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_loading && _routes.isEmpty) {
      return const Center(
        child: CircularProgressIndicator(color: AppColors.primaryLight),
      );
    }

    if (_error != null && _routes.isEmpty) {
      return ErrorStateWidget(
        message: 'Failed to load transit corridors. Please check backend connection.',
        onRetry: _loadJourneyData,
      );
    }

    final selectedRoute = _selectedRoute;
    final busesOnRoute = _busesOnSelectedRoute;
    final prediction = _predictionForSelectedRoute;

    return RefreshIndicator(
      onRefresh: _loadJourneyData,
      color: AppColors.primaryLight,
      child: ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.fromLTRB(16, 8, 16, 32),
        children: [
          // Corridors Selector Header
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'VADODARA TRANSIT CORRIDORS',
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w700,
                  color: AppColors.textMuted,
                  letterSpacing: 0.8,
                ),
              ),
              Text(
                '${_routes.length} corridors',
                style: const TextStyle(
                  fontSize: 11,
                  color: AppColors.textSecondary,
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),

          // Horizontal Corridor Tabs / Chips
          SizedBox(
            height: 48,
            child: ListView.separated(
              scrollDirection: Axis.horizontal,
              itemCount: _routes.length,
              separatorBuilder: (_, __) => const SizedBox(width: 8),
              itemBuilder: (context, index) {
                final r = _routes[index];
                final isSelected = r.routeId == _selectedRouteId;
                final routeColor = _parseHexColor(r.color);

                return ChoiceChip(
                  avatar: CircleAvatar(
                    backgroundColor: routeColor,
                    radius: 6,
                  ),
                  label: Text(r.routeId),
                  selected: isSelected,
                  onSelected: (val) {
                    if (val) {
                      setState(() {
                        _selectedRouteId = r.routeId;
                      });
                    }
                  },
                  selectedColor: AppColors.primary,
                  backgroundColor: AppColors.surface,
                  side: BorderSide(
                    color: isSelected ? routeColor : AppColors.border,
                    width: isSelected ? 1.5 : 1.0,
                  ),
                  labelStyle: TextStyle(
                    color: isSelected ? AppColors.textPrimary : AppColors.textSecondary,
                    fontWeight: isSelected ? FontWeight.bold : FontWeight.w500,
                    fontSize: 12,
                  ),
                );
              },
            ),
          ),

          const SizedBox(height: 16),

          // Crowd Filter Chips
          _buildFilterChips(),

          const SizedBox(height: 16),

          // Active Corridor Detail Card
          if (selectedRoute != null)
            _buildActiveCorridorCard(selectedRoute, busesOnRoute, prediction)
          else
            const EmptyStateWidget(
              icon: Icons.alt_route,
              title: 'No Corridor Selected',
              description: 'Select a corridor above to view live fleet and stops.',
            ),

          const SizedBox(height: 20),

          // Active Buses on Route Section
          _buildSectionHeader(
            'ACTIVE BUSES ON THIS ROUTE',
            '${busesOnRoute.length} operating',
          ),
          const SizedBox(height: 10),

          if (busesOnRoute.isEmpty)
            Container(
              padding: const EdgeInsets.all(18),
              decoration: BoxDecoration(
                color: AppColors.surface,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: AppColors.border),
              ),
              child: const Row(
                children: [
                  Icon(Icons.info_outline, color: AppColors.textMuted, size: 20),
                  SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      'No buses currently running telemetry on this corridor.',
                      style: TextStyle(color: AppColors.textSecondary, fontSize: 12),
                    ),
                  ),
                ],
              ),
            )
          else
            ...busesOnRoute.map((bus) => _buildBusItem(bus)),

          const SizedBox(height: 20),

          // Stops Timeline Section
          if (selectedRoute != null && selectedRoute.stops.isNotEmpty) ...[
            _buildSectionHeader(
              'CORRIDOR STOPS & WAYPOINTS',
              '${selectedRoute.stops.length} stops',
            ),
            const SizedBox(height: 10),
            _buildStopsTimeline(selectedRoute),
          ],
        ],
      ),
    );
  }

  Widget _buildFilterChips() {
    final filters = ['All', 'Low', 'Moderate', 'Crowded'];

    return Row(
      children: filters.map((f) {
        final isSelected = _crowdFilter == f;
        return Padding(
          padding: const EdgeInsets.only(right: 8),
          child: FilterChip(
            label: Text(f),
            selected: isSelected,
            onSelected: (_) {
              setState(() {
                _crowdFilter = f;
              });
            },
            backgroundColor: AppColors.surfaceElevated,
            selectedColor: AppColors.primary.withValues(alpha: 0.3),
            side: BorderSide(
              color: isSelected ? AppColors.primaryLight : AppColors.border,
            ),
            labelStyle: TextStyle(
              color: isSelected ? AppColors.primaryLight : AppColors.textSecondary,
              fontSize: 11,
              fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
            ),
            padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 0),
          ),
        );
      }).toList(),
    );
  }

  Widget _buildActiveCorridorCard(
    RouteModel route,
    List<BusModel> buses,
    CrowdPredictionModel? prediction,
  ) {
    final routeColor = _parseHexColor(route.color);
    final firstStop = route.stops.isNotEmpty
        ? (route.stops.first.stopName ?? 'Start')
        : 'Origin';
    final lastStop = route.stops.isNotEmpty
        ? (route.stops.last.stopName ?? 'End')
        : 'Destination';

    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: routeColor.withValues(alpha: 0.4), width: 1.2),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.25),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Route Header
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(
                  color: routeColor.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: routeColor, width: 1),
                ),
                child: Text(
                  route.routeId,
                  style: TextStyle(
                    color: routeColor,
                    fontWeight: FontWeight.bold,
                    fontSize: 13,
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      route.routeName,
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: AppColors.textPrimary,
                      ),
                    ),
                    const SizedBox(height: 3),
                    Text(
                      '$firstStop → $lastStop',
                      style: const TextStyle(
                        fontSize: 12,
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),

          const Divider(height: 24, color: AppColors.border),

          // Corridor Statistics Row
          Row(
            children: [
              _buildStatColumn('Total Stops', '${route.stops.length}', Icons.place_outlined),
              _buildStatColumn('Active Fleet', '${buses.length} buses', Icons.directions_bus_outlined),
              if (prediction != null)
                _buildStatColumn(
                  'Crowd Trend',
                  prediction.trend,
                  prediction.trend == 'INCREASING'
                      ? Icons.trending_up
                      : (prediction.trend == 'DECREASING'
                          ? Icons.trending_down
                          : Icons.trending_flat),
                  color: prediction.trend == 'INCREASING'
                      ? AppColors.warning
                      : AppColors.success,
                )
              else
                _buildStatColumn('Status', 'Operational', Icons.check_circle_outline, color: AppColors.success),
            ],
          ),

          // Prediction Banner if available
          if (prediction != null) ...[
            const SizedBox(height: 14),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
              decoration: BoxDecoration(
                color: AppColors.surfaceElevated,
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: AppColors.border),
              ),
              child: Row(
                children: [
                  const Icon(Icons.psychology_outlined, color: AppColors.cyan, size: 18),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            const Text(
                              'AI Occupancy Forecast: ',
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.bold,
                                color: AppColors.textPrimary,
                              ),
                            ),
                            OccupancyBadge(
                              level: prediction.predictedOccupancyLevel,
                              showLabel: true,
                            ),
                          ],
                        ),
                        const SizedBox(height: 3),
                        Text(
                          'Confidence: ${(prediction.predictionConfidence * 100).round()}% | Next Stop: ${prediction.nextStop ?? "In transit"}',
                          style: const TextStyle(
                            fontSize: 10,
                            color: AppColors.textMuted,
                          ),
                        ),
                      ],
                    ),
                  ),
                  if (prediction.etaMinutes != null)
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: AppColors.primary.withValues(alpha: 0.2),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Column(
                        children: [
                          Text(
                            '~${prediction.etaMinutes}m',
                            style: const TextStyle(
                              fontSize: 13,
                              fontWeight: FontWeight.bold,
                              color: AppColors.primaryLight,
                            ),
                          ),
                          const Text(
                            'EST. ARRIVAL',
                            style: TextStyle(fontSize: 7, color: AppColors.textMuted),
                          ),
                        ],
                      ),
                    ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildStatColumn(String label, String value, IconData icon, {Color? color}) {
    final displayColor = color ?? AppColors.textPrimary;
    return Expanded(
      child: Row(
        children: [
          Icon(icon, size: 16, color: displayColor),
          const SizedBox(width: 6),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                value,
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                  color: displayColor,
                ),
              ),
              Text(
                label,
                style: const TextStyle(
                  fontSize: 10,
                  color: AppColors.textMuted,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildBusItem(BusModel bus) {
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: AppColors.border),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: AppColors.primary.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(10),
            ),
            child: const Icon(
              Icons.directions_bus,
              color: AppColors.primaryLight,
              size: 22,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                      bus.busId,
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                        color: AppColors.textPrimary,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 1.5),
                      decoration: BoxDecoration(
                        color: AppColors.success.withValues(alpha: 0.15),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: const Text(
                        'LIVE',
                        style: TextStyle(
                          color: AppColors.success,
                          fontSize: 9,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  'Speed: ${bus.speed.toStringAsFixed(1)} km/h • Pax: ${bus.crowdCount}/${bus.capacity}',
                  style: const TextStyle(
                    fontSize: 11,
                    color: AppColors.textSecondary,
                  ),
                ),
              ],
            ),
          ),
          OccupancyBadge(level: bus.occupancyLevel),
        ],
      ),
    );
  }

  Widget _buildStopsTimeline(RouteModel route) {
    final routeColor = _parseHexColor(route.color);

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.border),
      ),
      child: Column(
        children: List.generate(route.stops.length, (index) {
          final stop = route.stops[index];
          final isFirst = index == 0;
          final isLast = index == route.stops.length - 1;
          final stopTitle = stop.stopName ?? 'Waypoint ${index + 1}';

          return IntrinsicHeight(
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Timeline Line and Dot
                SizedBox(
                  width: 28,
                  child: Column(
                    children: [
                      Container(
                        width: isFirst || isLast ? 14 : 10,
                        height: isFirst || isLast ? 14 : 10,
                        decoration: BoxDecoration(
                          color: isFirst || isLast ? routeColor : AppColors.surfaceElevated,
                          shape: BoxShape.circle,
                          border: Border.all(
                            color: routeColor,
                            width: 2,
                          ),
                        ),
                      ),
                      if (!isLast)
                        Expanded(
                          child: Container(
                            width: 2,
                            color: AppColors.border,
                          ),
                        ),
                    ],
                  ),
                ),
                const SizedBox(width: 8),

                // Stop Name and Coordinates
                Expanded(
                  child: Padding(
                    padding: const EdgeInsets.only(bottom: 16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          stopTitle,
                          style: TextStyle(
                            fontSize: 13,
                            fontWeight: isFirst || isLast ? FontWeight.bold : FontWeight.w500,
                            color: isFirst || isLast ? AppColors.textPrimary : AppColors.textSecondary,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          '${stop.lat.toStringAsFixed(4)}, ${stop.lon.toStringAsFixed(4)}',
                          style: const TextStyle(
                            fontSize: 10,
                            color: AppColors.textMuted,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),

                if (isFirst)
                  _badge('ORIGIN', AppColors.cyan)
                else if (isLast)
                  _badge('TERMINAL', routeColor),
              ],
            ),
          );
        }),
      ),
    );
  }

  Widget _badge(String text, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: color.withValues(alpha: 0.4)),
      ),
      child: Text(
        text,
        style: TextStyle(
          fontSize: 9,
          fontWeight: FontWeight.bold,
          color: color,
        ),
      ),
    );
  }

  Widget _buildSectionHeader(String title, String countText) {
    return Row(
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
        Text(
          countText,
          style: const TextStyle(
            fontSize: 11,
            color: AppColors.textSecondary,
          ),
        ),
      ],
    );
  }
}
