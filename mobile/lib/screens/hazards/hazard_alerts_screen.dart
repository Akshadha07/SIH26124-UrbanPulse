import 'package:flutter/material.dart';

import '../../models/hazard.dart';
import '../../services/api_service.dart';
import '../../theme/app_colors.dart';

class HazardAlertsScreen extends StatefulWidget {
  const HazardAlertsScreen({super.key});

  @override
  State<HazardAlertsScreen> createState() => _HazardAlertsScreenState();
}

class _HazardAlertsScreenState extends State<HazardAlertsScreen> {
  final ApiService _apiService = ApiService();

  List<HazardModel> _hazards = [];
  bool _isLoading = true;
  String? _error;
  String _selectedFilter = 'All';

  @override
  void initState() {
    super.initState();
    _loadHazards();
  }

  Future<void> _loadHazards() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final hazards = await _apiService.getNearbyHazards(
        radiusMeters: 5000,
      );

      if (!mounted) return;

      setState(() {
        _hazards = hazards;
        _isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;

      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  List<HazardModel> get _filteredHazards {
    if (_selectedFilter == 'All') {
      return _hazards;
    }

    if (_selectedFilter == 'Critical') {
      return _hazards.where((hazard) {
        return hazard.isCriticalWaterlogging ||
            hazard.priorityScore >= 80;
      }).toList();
    }

    if (_selectedFilter == 'Confirmed') {
      return _hazards.where((hazard) {
        return hazard.isCorroborated;
      }).toList();
    }

    if (_selectedFilter == 'Waterlogging') {
      return _hazards.where((hazard) {
        return hazard.hazardType.toUpperCase().contains('WATERLOGGING');
      }).toList();
    }

    if (_selectedFilter == 'Potholes') {
      return _hazards.where((hazard) {
        return hazard.hazardType.toUpperCase().contains('POTHOLE');
      }).toList();
    }

    return _hazards;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Hazard Alerts'),
        actions: [
          IconButton(
            onPressed: _isLoading ? null : _loadHazards,
            icon: const Icon(Icons.refresh_rounded),
            tooltip: 'Refresh',
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _loadHazards,
        child: _buildBody(),
      ),
    );
  }

  Widget _buildBody() {
    if (_isLoading && _hazards.isEmpty) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }

    if (_error != null && _hazards.isEmpty) {
      return ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        children: [
          SizedBox(
            height: MediaQuery.of(context).size.height * 0.7,
            child: Center(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Container(
                      padding: const EdgeInsets.all(18),
                      decoration: BoxDecoration(
                        color: Colors.red.withValues(alpha: 0.12),
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(
                        Icons.cloud_off_rounded,
                        size: 42,
                        color: Colors.redAccent,
                      ),
                    ),
                    const SizedBox(height: 18),
                    const Text(
                      'Unable to load hazards',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      _error!,
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        color: Colors.white.withValues(alpha: 0.6),
                      ),
                    ),
                    const SizedBox(height: 20),
                    FilledButton.icon(
                      onPressed: _loadHazards,
                      icon: const Icon(Icons.refresh_rounded),
                      label: const Text('Try Again'),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      );
    }

    final hazards = _filteredHazards;

    return ListView(
      physics: const AlwaysScrollableScrollPhysics(),
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 32),
      children: [
        _buildHeaderSummary(),
        const SizedBox(height: 16),
        _buildFilters(),
        const SizedBox(height: 16),
        if (hazards.isEmpty)
          _buildEmptyState()
        else
          ...hazards.map(
            (hazard) => Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: _buildHazardCard(hazard),
            ),
          ),
      ],
    );
  }

  Widget _buildHeaderSummary() {
    final criticalCount = _hazards.where((hazard) {
      return hazard.isCriticalWaterlogging || hazard.priorityScore >= 80;
    }).length;

    final confirmedCount = _hazards.where((hazard) {
      return hazard.isCorroborated;
    }).length;

    final waterloggingCount = _hazards.where((hazard) {
      return hazard.hazardType.toUpperCase().contains('WATERLOGGING');
    }).length;

    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: Colors.white.withValues(alpha: 0.07),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: Colors.orange.withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(
                  Icons.warning_amber_rounded,
                  color: Colors.orangeAccent,
                ),
              ),
              const SizedBox(width: 12),
              const Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Nearby road intelligence',
                      style: TextStyle(
                        fontSize: 17,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    SizedBox(height: 3),
                    Text(
                      'AI-detected hazards from the UrbanPulse fleet',
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.white54,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 18),
          Row(
            children: [
              Expanded(
                child: _summaryItem(
                  value: _hazards.length.toString(),
                  label: 'Nearby',
                  icon: Icons.location_on_outlined,
                ),
              ),
              Expanded(
                child: _summaryItem(
                  value: criticalCount.toString(),
                  label: 'Critical',
                  icon: Icons.priority_high_rounded,
                  valueColor: Colors.redAccent,
                ),
              ),
              Expanded(
                child: _summaryItem(
                  value: confirmedCount.toString(),
                  label: 'Confirmed',
                  icon: Icons.verified_outlined,
                  valueColor: Colors.greenAccent,
                ),
              ),
              Expanded(
                child: _summaryItem(
                  value: waterloggingCount.toString(),
                  label: 'Flooding',
                  icon: Icons.water_drop_outlined,
                  valueColor: Colors.cyanAccent,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _summaryItem({
    required String value,
    required String label,
    required IconData icon,
    Color valueColor = Colors.white,
  }) {
    return Column(
      children: [
        Icon(
          icon,
          size: 18,
          color: Colors.white54,
        ),
        const SizedBox(height: 6),
        Text(
          value,
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.w800,
            color: valueColor,
          ),
        ),
        const SizedBox(height: 2),
        Text(
          label,
          style: const TextStyle(
            fontSize: 10,
            color: Colors.white54,
          ),
        ),
      ],
    );
  }

  Widget _buildFilters() {
    final filters = [
      'All',
      'Critical',
      'Confirmed',
      'Waterlogging',
      'Potholes',
    ];

    return SizedBox(
      height: 42,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        itemCount: filters.length,
        separatorBuilder: (_, __) => const SizedBox(width: 8),
        itemBuilder: (context, index) {
          final filter = filters[index];
          final selected = filter == _selectedFilter;

          return ChoiceChip(
            label: Text(filter),
            selected: selected,
            onSelected: (_) {
              setState(() {
                _selectedFilter = filter;
              });
            },
            labelStyle: TextStyle(
              color: selected ? Colors.white : Colors.white70,
              fontWeight: selected ? FontWeight.w700 : FontWeight.w500,
            ),
            backgroundColor: AppColors.surface,
            selectedColor: AppColors.primary,
            side: BorderSide(
              color: selected
                  ? AppColors.primary
                  : Colors.white.withValues(alpha: 0.08),
            ),
          );
        },
      ),
    );
  }

  Widget _buildHazardCard(HazardModel hazard) {
    final critical = hazard.isCriticalWaterlogging ||
        hazard.priorityScore >= 80;

    final waterlogging =
        hazard.hazardType.toUpperCase().contains('WATERLOGGING');

    final confirmed = hazard.isCorroborated;

    final Color accent;

    if (critical) {
      accent = Colors.redAccent;
    } else if (waterlogging) {
      accent = Colors.cyanAccent;
    } else if (confirmed) {
      accent = Colors.orangeAccent;
    } else {
      accent = Colors.blueAccent;
    }

    return InkWell(
      borderRadius: BorderRadius.circular(20),
      onTap: () => _showHazardDetails(hazard),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: accent.withValues(alpha: 0.18),
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.16),
              blurRadius: 14,
              offset: const Offset(0, 6),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: 46,
                  height: 46,
                  decoration: BoxDecoration(
                    color: accent.withValues(alpha: 0.12),
                    borderRadius: BorderRadius.circular(14),
                  ),
                  child: Icon(
                    _hazardIcon(hazard.hazardType),
                    color: accent,
                    size: 24,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        _prettyHazardName(hazard.hazardType),
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                      const SizedBox(height: 5),
                      Text(
                        hazard.addressHint ??
                            '${hazard.lat.toStringAsFixed(4)}, ${hazard.lon.toStringAsFixed(4)}',
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                          fontSize: 12,
                          color: Colors.white54,
                        ),
                      ),
                    ],
                  ),
                ),
                _priorityBadge(hazard.priorityScore, accent),
              ],
            ),
            const SizedBox(height: 15),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                _smallBadge(
                  icon: Icons.near_me_outlined,
                  text: _formatDistance(hazard.distanceMeters),
                ),
                _smallBadge(
                  icon: Icons.speed_outlined,
                  text: '${hazard.severity.toStringAsFixed(1)}/5 severity',
                ),
                _smallBadge(
                  icon: Icons.psychology_outlined,
                  text:
                      '${(hazard.confidence * 100).round()}% confidence',
                ),
                if (confirmed)
                  _smallBadge(
                    icon: Icons.verified_outlined,
                    text: '${hazard.distinctBusCount} buses',
                    color: Colors.greenAccent,
                  ),
              ],
            ),
            const SizedBox(height: 14),
            Row(
              children: [
                Expanded(
                  child: _statusLine(
                    icon: confirmed
                        ? Icons.verified_rounded
                        : Icons.visibility_outlined,
                    text: _prettyStatus(hazard.status),
                    color: confirmed
                        ? Colors.greenAccent
                        : Colors.white60,
                  ),
                ),
                const Icon(
                  Icons.chevron_right_rounded,
                  color: Colors.white38,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _priorityBadge(double score, Color accent) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: 9,
        vertical: 6,
      ),
      decoration: BoxDecoration(
        color: accent.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Column(
        children: [
          Text(
            score.toStringAsFixed(0),
            style: TextStyle(
              color: accent,
              fontSize: 15,
              fontWeight: FontWeight.w900,
            ),
          ),
          const Text(
            'PRIORITY',
            style: TextStyle(
              color: Colors.white38,
              fontSize: 7,
              fontWeight: FontWeight.w700,
            ),
          ),
        ],
      ),
    );
  }

  Widget _smallBadge({
    required IconData icon,
    required String text,
    Color color = Colors.white60,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: 9,
        vertical: 6,
      ),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.045),
        borderRadius: BorderRadius.circular(9),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            icon,
            size: 13,
            color: color,
          ),
          const SizedBox(width: 5),
          Text(
            text,
            style: TextStyle(
              color: color,
              fontSize: 10,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  Widget _statusLine({
    required IconData icon,
    required String text,
    required Color color,
  }) {
    return Row(
      children: [
        Icon(
          icon,
          size: 16,
          color: color,
        ),
        const SizedBox(width: 7),
        Text(
          text,
          style: TextStyle(
            color: color,
            fontSize: 12,
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }

  Widget _buildEmptyState() {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: 24,
        vertical: 60,
      ),
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: Colors.greenAccent.withValues(alpha: 0.08),
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.verified_rounded,
              size: 48,
              color: Colors.greenAccent,
            ),
          ),
          const SizedBox(height: 18),
          const Text(
            'No hazards found',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.w800,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'No road hazards matching this filter were detected nearby.',
            textAlign: TextAlign.center,
            style: TextStyle(
              color: Colors.white.withValues(alpha: 0.55),
              height: 1.4,
            ),
          ),
          const SizedBox(height: 18),
          OutlinedButton.icon(
            onPressed: _loadHazards,
            icon: const Icon(Icons.refresh_rounded),
            label: const Text('Refresh'),
          ),
        ],
      ),
    );
  }

  void _showHazardDetails(HazardModel hazard) {
    final critical = hazard.isCriticalWaterlogging ||
        hazard.priorityScore >= 80;

    final accent = critical
        ? Colors.redAccent
        : hazard.hazardType.toUpperCase().contains('WATERLOGGING')
            ? Colors.cyanAccent
            : Colors.orangeAccent;

    showModalBottomSheet(
      context: context,
      backgroundColor: AppColors.surface,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(
          top: Radius.circular(28),
        ),
      ),
      builder: (context) {
        return SafeArea(
          child: Padding(
            padding: const EdgeInsets.fromLTRB(
              20,
              12,
              20,
              24,
            ),
            child: SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Center(
                    child: Container(
                      width: 42,
                      height: 4,
                      decoration: BoxDecoration(
                        color: Colors.white24,
                        borderRadius: BorderRadius.circular(20),
                      ),
                    ),
                  ),
                  const SizedBox(height: 22),
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: accent.withValues(alpha: 0.12),
                          borderRadius: BorderRadius.circular(14),
                        ),
                        child: Icon(
                          _hazardIcon(hazard.hazardType),
                          color: accent,
                          size: 28,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          _prettyHazardName(hazard.hazardType),
                          style: const TextStyle(
                            fontSize: 21,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 22),
                  if (hazard.isCriticalWaterlogging)
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        color: Colors.redAccent.withValues(alpha: 0.10),
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(
                          color: Colors.redAccent.withValues(alpha: 0.25),
                        ),
                      ),
                      child: const Row(
                        children: [
                          Icon(
                            Icons.warning_rounded,
                            color: Colors.redAccent,
                          ),
                          SizedBox(width: 10),
                          Expanded(
                            child: Text(
                              'Critical waterlogging detected. Exercise caution in this area.',
                              style: TextStyle(
                                color: Colors.redAccent,
                                fontWeight: FontWeight.w700,
                                height: 1.35,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  const SizedBox(height: 18),
                  _detailRow(
                    'Priority score',
                    hazard.priorityScore.toStringAsFixed(1),
                    Icons.priority_high_rounded,
                  ),
                  _detailRow(
                    'Severity',
                    '${hazard.severity.toStringAsFixed(1)} / 5',
                    Icons.warning_amber_rounded,
                  ),
                  _detailRow(
                    'AI confidence',
                    '${(hazard.confidence * 100).round()}%',
                    Icons.psychology_outlined,
                  ),
                  _detailRow(
                    'Distance',
                    _formatDistance(hazard.distanceMeters),
                    Icons.near_me_outlined,
                  ),
                  _detailRow(
                    'Confirmations',
                    hazard.confirmationCount.toString(),
                    Icons.repeat_rounded,
                  ),
                  _detailRow(
                    'Buses corroborating',
                    hazard.distinctBusCount.toString(),
                    Icons.directions_bus_outlined,
                  ),
                  _detailRow(
                    'Status',
                    _prettyStatus(hazard.status),
                    Icons.info_outline_rounded,
                  ),
                  const SizedBox(height: 8),
                  _detailRow(
                    'Coordinates',
                    '${hazard.lat.toStringAsFixed(6)}, ${hazard.lon.toStringAsFixed(6)}',
                    Icons.location_on_outlined,
                  ),
                  if (hazard.addressHint != null &&
                      hazard.addressHint!.isNotEmpty)
                    _detailRow(
                      'Location',
                      hazard.addressHint!,
                      Icons.place_outlined,
                    ),
                  if (hazard.waterloggingSeverity != null)
                    _detailRow(
                      'Waterlogging severity',
                      hazard.waterloggingSeverity!,
                      Icons.water_drop_outlined,
                    ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _detailRow(
    String label,
    String value,
    IconData icon,
  ) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 9),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(
            icon,
            size: 19,
            color: Colors.white54,
          ),
          const SizedBox(width: 12),
          SizedBox(
            width: 125,
            child: Text(
              label,
              style: const TextStyle(
                color: Colors.white54,
                fontSize: 12,
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              textAlign: TextAlign.right,
              style: const TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
        ],
      ),
    );
  }

  IconData _hazardIcon(String type) {
    final value = type.toUpperCase();

    if (value.contains('WATERLOGGING') || value.contains('FLOOD')) {
      return Icons.water_damage_outlined;
    }

    if (value.contains('POTHOLE')) {
      return Icons.warning_amber_rounded;
    }

    if (value.contains('ACCIDENT') || value.contains('CRASH')) {
      return Icons.car_crash_outlined;
    }

    if (value.contains('TRAFFIC')) {
      return Icons.traffic_rounded;
    }

    if (value.contains('DEBRIS')) {
      return Icons.construction_outlined;
    }

    return Icons.warning_amber_rounded;
  }

  String _prettyHazardName(String value) {
    return value
        .replaceAll('_', ' ')
        .toLowerCase()
        .split(' ')
        .map(
          (word) => word.isEmpty
              ? word
              : word[0].toUpperCase() + word.substring(1),
        )
        .join(' ');
  }

  String _prettyStatus(String value) {
    return value
        .replaceAll('_', ' ')
        .toLowerCase()
        .split(' ')
        .map(
          (word) => word.isEmpty
              ? word
              : word[0].toUpperCase() + word.substring(1),
        )
        .join(' ');
  }

  String _formatDistance(double meters) {
    if (meters < 1000) {
      return '${meters.round()} m away';
    }

    return '${(meters / 1000).toStringAsFixed(1)} km away';
  }
}