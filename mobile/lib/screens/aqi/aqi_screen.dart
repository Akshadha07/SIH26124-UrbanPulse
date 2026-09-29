import 'package:flutter/material.dart';
import '../../models/aqi.dart';
import '../../services/api_service.dart';
import '../../theme/app_colors.dart';
import '../../widgets/simulation_badge.dart';
import '../../widgets/empty_state.dart';

class AqiScreen extends StatefulWidget {
  const AqiScreen({super.key});

  @override
  State<AqiScreen> createState() => _AqiScreenState();
}

class _AqiScreenState extends State<AqiScreen> {
  final ApiService _api = ApiService();

  bool _loading = true;
  String? _error;
  List<AqiPointModel> _aqiList = [];
  String _selectedFilter = 'All';

  @override
  void initState() {
    super.initState();
    _loadAqiData();
  }

  Future<void> _loadAqiData() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final data = await _api.getLiveAqi(limit: 50);
      if (!mounted) return;
      setState(() {
        _aqiList = data;
        _loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString();
        _loading = false;
      });
    }
  }

  Color _getAqiColor(double aqi) {
    if (aqi <= 50) return AppColors.success;
    if (aqi <= 100) return AppColors.warning;
    if (aqi <= 150) return AppColors.orange;
    if (aqi <= 200) return AppColors.danger;
    if (aqi <= 300) return const Color(0xFF8B5CF6);
    return AppColors.disaster;
  }

  String _getAqiCategory(double aqi) {
    if (aqi <= 50) return 'Good';
    if (aqi <= 100) return 'Moderate';
    if (aqi <= 150) return 'Unhealthy (Sensitive)';
    if (aqi <= 200) return 'Unhealthy';
    if (aqi <= 300) return 'Very Unhealthy';
    return 'Hazardous';
  }

  String _getHealthAdvisory(double aqi) {
    if (aqi <= 50) {
      return 'Air quality is satisfactory. Ideal conditions for outdoor transit and walking.';
    } else if (aqi <= 100) {
      return 'Air quality is acceptable. Very sensitive individuals should limit prolonged outdoor exertion.';
    } else if (aqi <= 150) {
      return 'Sensitive groups may experience respiratory irritation. Consider wearing a mask during peak transit.';
    } else if (aqi <= 200) {
      return 'Everyone may begin to experience health effects. Use air-conditioned buses and minimize exposure.';
    } else {
      return 'Health alert: Serious risk of respiratory irritation. Commuters are advised to wear N95 filtration.';
    }
  }

  List<AqiPointModel> get _filteredAqi {
    if (_selectedFilter == 'All') return _aqiList;

    return _aqiList.where((p) {
      final cat = p.category.toLowerCase();
      if (_selectedFilter == 'Good') return cat.contains('good') || p.aqiValue <= 50;
      if (_selectedFilter == 'Moderate') return cat.contains('moderate') || (p.aqiValue > 50 && p.aqiValue <= 100);
      if (_selectedFilter == 'Unhealthy') return cat.contains('unhealthy') || (p.aqiValue > 100 && p.aqiValue <= 200);
      if (_selectedFilter == 'Hazardous') return cat.contains('hazard') || p.aqiValue > 200;
      return true;
    }).toList();
  }

  String _formatTimestamp(DateTime time) {
    final diff = DateTime.now().difference(time);
    if (diff.inSeconds < 30) return 'Just now';
    if (diff.inMinutes < 1) return '${diff.inSeconds}s ago';
    if (diff.inMinutes < 60) return '${diff.inMinutes}m ago';
    if (diff.inHours < 24) return '${diff.inHours}h ago';
    return '${diff.inDays}d ago';
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
            Text('Clean Commute AQI'),
            SizedBox(width: 8),
            SimulationBadge(),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Refresh AQI Readings',
            onPressed: _loading ? null : _loadAqiData,
          ),
        ],
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_loading && _aqiList.isEmpty) {
      return const Center(
        child: CircularProgressIndicator(color: AppColors.primaryLight),
      );
    }

    if (_error != null && _aqiList.isEmpty) {
      return ErrorStateWidget(
        message: 'Failed to connect to air quality telemetry. Please check backend connection.',
        onRetry: _loadAqiData,
      );
    }

    final filtered = _filteredAqi;

    // Calculate city-wide average AQI
    double avgAqi = 0.0;
    if (_aqiList.isNotEmpty) {
      final sum = _aqiList.fold<double>(0.0, (acc, item) => acc + item.aqiValue);
      avgAqi = sum / _aqiList.length;
    }

    return RefreshIndicator(
      onRefresh: _loadAqiData,
      color: AppColors.primaryLight,
      child: ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.fromLTRB(16, 8, 16, 32),
        children: [
          // City-Wide Air Quality Hero Card
          _buildCitySummaryCard(avgAqi),

          const SizedBox(height: 18),

          // Clean Commute Advisory Card
          _buildHealthAdvisoryCard(avgAqi),

          const SizedBox(height: 18),

          // Filter Chips
          _buildFilterChips(),

          const SizedBox(height: 16),

          // Section Header
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'LIVE SENSING TELEMETRY (FLEET MOUNTED)',
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w700,
                  color: AppColors.textMuted,
                  letterSpacing: 0.8,
                ),
              ),
              Text(
                '${filtered.length} nodes',
                style: const TextStyle(
                  fontSize: 11,
                  color: AppColors.textSecondary,
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),

          if (filtered.isEmpty)
            const EmptyStateWidget(
              icon: Icons.air,
              title: 'No Sensor Readings Found',
              description: 'No air quality points match the selected filter category.',
            )
          else
            ...filtered.map((point) => _buildAqiCard(point)),
        ],
      ),
    );
  }

  Widget _buildCitySummaryCard(double avgAqi) {
    final aqiColor = _getAqiColor(avgAqi);
    final category = _getAqiCategory(avgAqi);

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: aqiColor.withValues(alpha: 0.35), width: 1.2),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.25),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'VADODARA METRO AIR QUALITY',
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w700,
                      color: AppColors.textMuted,
                      letterSpacing: 0.8,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    category.toUpperCase(),
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.w900,
                      color: aqiColor,
                    ),
                  ),
                ],
              ),
              Container(
                width: 68,
                height: 68,
                decoration: BoxDecoration(
                  color: aqiColor.withValues(alpha: 0.15),
                  shape: BoxShape.circle,
                  border: Border.all(color: aqiColor, width: 2),
                ),
                child: Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        avgAqi.toStringAsFixed(0),
                        style: TextStyle(
                          fontSize: 22,
                          fontWeight: FontWeight.w900,
                          color: aqiColor,
                        ),
                      ),
                      const Text(
                        'AQI',
                        style: TextStyle(
                          fontSize: 9,
                          fontWeight: FontWeight.bold,
                          color: AppColors.textMuted,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),

          const SizedBox(height: 16),

          // Visual AQI Gauge Bar
          ClipRRect(
            borderRadius: BorderRadius.circular(6),
            child: LinearProgressIndicator(
              value: (avgAqi / 300.0).clamp(0.0, 1.0),
              minHeight: 8,
              backgroundColor: AppColors.surfaceElevated,
              valueColor: AlwaysStoppedAnimation<Color>(aqiColor),
            ),
          ),
          const SizedBox(height: 6),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: const [
              Text('0 Good', style: TextStyle(fontSize: 10, color: AppColors.success)),
              Text('100 Mod', style: TextStyle(fontSize: 10, color: AppColors.warning)),
              Text('200 Unhealthy', style: TextStyle(fontSize: 10, color: AppColors.danger)),
              Text('300+ Haz', style: TextStyle(fontSize: 10, color: AppColors.disaster)),
            ],
          ),

          const Divider(height: 24, color: AppColors.border),

          // Fleet Sensor Stats Row
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildSensorStat('Total Nodes', '${_aqiList.length} buses', Icons.sensors),
              _buildSensorStat(
                'Good Quality',
                '${_aqiList.where((p) => p.aqiValue <= 50).length}',
                Icons.check_circle_outline,
                color: AppColors.success,
              ),
              _buildSensorStat(
                'Elevated',
                '${_aqiList.where((p) => p.aqiValue > 100).length}',
                Icons.warning_amber_rounded,
                color: AppColors.warning,
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSensorStat(String label, String value, IconData icon, {Color? color}) {
    final fg = color ?? AppColors.textPrimary;
    return Column(
      children: [
        Icon(icon, size: 18, color: fg),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.bold,
            color: fg,
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
    );
  }

  Widget _buildHealthAdvisoryCard(double avgAqi) {
    final aqiColor = _getAqiColor(avgAqi);
    final advisory = _getHealthAdvisory(avgAqi);

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.surfaceElevated,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: AppColors.border),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: aqiColor.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(Icons.health_and_safety_outlined, color: aqiColor, size: 22),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Clean Commute Recommendation',
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.bold,
                    color: AppColors.textPrimary,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  advisory,
                  style: const TextStyle(
                    fontSize: 11,
                    color: AppColors.textSecondary,
                    height: 1.35,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFilterChips() {
    final filters = ['All', 'Good', 'Moderate', 'Unhealthy', 'Hazardous'];

    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: filters.map((f) {
          final isSelected = _selectedFilter == f;
          return Padding(
            padding: const EdgeInsets.only(right: 8),
            child: FilterChip(
              label: Text(f),
              selected: isSelected,
              onSelected: (_) {
                setState(() {
                  _selectedFilter = f;
                });
              },
              backgroundColor: AppColors.surface,
              selectedColor: AppColors.primary.withValues(alpha: 0.3),
              side: BorderSide(
                color: isSelected ? AppColors.primaryLight : AppColors.border,
              ),
              labelStyle: TextStyle(
                color: isSelected ? AppColors.primaryLight : AppColors.textSecondary,
                fontSize: 12,
                fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
              ),
            ),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildAqiCard(AqiPointModel point) {
    final color = _getAqiColor(point.aqiValue);

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withValues(alpha: 0.25)),
      ),
      child: Column(
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: color.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(Icons.air, color: color, size: 22),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Text(
                          point.busId,
                          style: const TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.bold,
                            color: AppColors.textPrimary,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: color.withValues(alpha: 0.15),
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: Text(
                            point.category,
                            style: TextStyle(
                              fontSize: 10,
                              fontWeight: FontWeight.bold,
                              color: color,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 3),
                    Text(
                      '${point.lat.toStringAsFixed(4)}, ${point.lon.toStringAsFixed(4)}',
                      style: const TextStyle(
                        fontSize: 11,
                        color: AppColors.textMuted,
                      ),
                    ),
                  ],
                ),
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    point.aqiValue.toStringAsFixed(0),
                    style: TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.w900,
                      color: color,
                    ),
                  ),
                  Text(
                    _formatTimestamp(point.timestamp),
                    style: const TextStyle(
                      fontSize: 10,
                      color: AppColors.textMuted,
                    ),
                  ),
                ],
              ),
            ],
          ),

          const SizedBox(height: 12),

          // Sensor Measurements Row
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: BoxDecoration(
              color: AppColors.surfaceElevated,
              borderRadius: BorderRadius.circular(10),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildMetricItem('PM 2.5', '${point.pm25.toStringAsFixed(1)} µg/m³'),
                if (point.pm10 != null)
                  _buildMetricItem('PM 10', '${point.pm10!.toStringAsFixed(1)} µg/m³'),
                if (point.co2 != null)
                  _buildMetricItem('CO2', '${point.co2!.toStringAsFixed(0)} ppm'),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMetricItem(String label, String value) {
    return Column(
      children: [
        Text(
          value,
          style: const TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.bold,
            color: AppColors.textPrimary,
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
    );
  }
}
