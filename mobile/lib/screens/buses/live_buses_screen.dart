import 'package:flutter/material.dart';
import '../../models/bus.dart';
import '../../services/api_service.dart';

class LiveBusesScreen extends StatefulWidget {
  const LiveBusesScreen({super.key});

  @override
  State<LiveBusesScreen> createState() => _LiveBusesScreenState();
}

class _LiveBusesScreenState extends State<LiveBusesScreen> {
  final ApiService _apiService = ApiService();

  List<BusModel> _buses = [];
  bool _loading = true;
  String? _error;
  String _filter = 'All';

  @override
  void initState() {
    super.initState();
    _loadBuses();
  }

  Future<void> _loadBuses() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final buses = await _apiService.getLiveBuses();

      if (!mounted) return;

      setState(() {
        _buses = buses;
        _loading = false;
      });
    } catch (e) {
      if (!mounted) return;

      setState(() {
        _error = 'Unable to load live buses';
        _loading = false;
      });
    }
  }

  List<BusModel> get _filteredBuses {
    if (_filter == 'All') {
      return _buses;
    }

    return _buses.where((bus) {
      final level = bus.occupancyLevel.toLowerCase();

      if (_filter == 'Low') return level == 'low';
      if (_filter == 'Moderate') {
        return level == 'moderate' || level == 'medium';
      }
      if (_filter == 'High') {
        return level == 'high' || level == 'crowded';
      }

      return true;
    }).toList();
  }

  Color _occupancyColor(String level) {
    switch (level.toLowerCase()) {
      case 'low':
        return const Color(0xFF00C897);
      case 'moderate':
      case 'medium':
        return const Color(0xFFFFB020);
      case 'high':
      case 'crowded':
        return const Color(0xFFFF5C5C);
      default:
        return const Color(0xFF60A5FA);
    }
  }

  String _occupancyLabel(String level) {
    switch (level.toLowerCase()) {
      case 'low':
        return 'LOW CROWDED';
      case 'moderate':
      case 'medium':
        return 'MODERATE';
      case 'high':
      case 'crowded':
        return 'CROWDED';
      default:
        return level.toUpperCase();
    }
  }

  String _formatUpdated(DateTime time) {
    final difference = DateTime.now().difference(time);

    if (difference.inSeconds < 10) {
      return 'Just now';
    }

    if (difference.inMinutes < 1) {
      return '${difference.inSeconds}s ago';
    }

    if (difference.inMinutes < 60) {
      return '${difference.inMinutes}m ago';
    }

    return '${difference.inHours}h ago';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF080D17),
      appBar: AppBar(
        backgroundColor: const Color(0xFF080D17),
        elevation: 0,
        titleSpacing: 20,
        title: const Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Live Buses',
              style: TextStyle(
                fontSize: 22,
                fontWeight: FontWeight.w800,
              ),
            ),
            SizedBox(height: 2),
            Text(
              'Vadodara public transport fleet',
              style: TextStyle(
                fontSize: 12,
                color: Color(0xFF8B9AB5),
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            tooltip: 'Refresh fleet',
            onPressed: _loading ? null : _loadBuses,
            icon: const Icon(Icons.refresh_rounded),
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_loading && _buses.isEmpty) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }

    if (_error != null && _buses.isEmpty) {
      return _buildError();
    }

    return RefreshIndicator(
      onRefresh: _loadBuses,
      child: ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.fromLTRB(16, 8, 16, 28),
        children: [
          _buildFleetSummary(),
          const SizedBox(height: 18),
          _buildFilters(),
          const SizedBox(height: 16),
          if (_filteredBuses.isEmpty)
            _buildEmptyState()
          else
            ..._filteredBuses.map(
              (bus) => Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: _BusCard(
                  bus: bus,
                  occupancyColor: _occupancyColor(bus.occupancyLevel),
                  occupancyLabel: _occupancyLabel(bus.occupancyLevel),
                  updatedText: _formatUpdated(bus.lastUpdated),
                  onTap: () => _showBusDetails(bus),
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildFleetSummary() {
    final active = _buses
        .where((bus) => bus.status.toLowerCase() == 'active')
        .length;

    final low = _buses
        .where((bus) => bus.occupancyLevel.toLowerCase() == 'low')
        .length;

    final crowded = _buses.where((bus) {
      final level = bus.occupancyLevel.toLowerCase();
      return level == 'high' || level == 'crowded';
    }).length;

    return Row(
      children: [
        Expanded(
          child: _StatCard(
            icon: Icons.directions_bus_rounded,
            value: '$active',
            label: 'ACTIVE',
            iconColor: const Color(0xFF3B82F6),
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: _StatCard(
            icon: Icons.people_alt_rounded,
            value: '$low',
            label: 'LOW CROWD',
            iconColor: const Color(0xFF00C897),
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: _StatCard(
            icon: Icons.groups_rounded,
            value: '$crowded',
            label: 'CROWDED',
            iconColor: const Color(0xFFFF5C5C),
          ),
        ),
      ],
    );
  }

  Widget _buildFilters() {
    const filters = ['All', 'Low', 'Moderate', 'High'];

    return SizedBox(
      height: 42,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        itemCount: filters.length,
        separatorBuilder: (_, __) => const SizedBox(width: 8),
        itemBuilder: (context, index) {
          final filter = filters[index];
          final selected = _filter == filter;

          return ChoiceChip(
            label: Text(filter),
            selected: selected,
            onSelected: (_) {
              setState(() {
                _filter = filter;
              });
            },
            labelStyle: TextStyle(
              color: selected
                  ? Colors.white
                  : const Color(0xFF9AA8BF),
              fontWeight: FontWeight.w700,
              fontSize: 13,
            ),
            backgroundColor: const Color(0xFF121B2B),
            selectedColor: const Color(0xFF1769E0),
            side: BorderSide(
              color: selected
                  ? const Color(0xFF1769E0)
                  : const Color(0xFF25344D),
            ),
          );
        },
      ),
    );
  }

  Widget _buildError() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(28),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.cloud_off_rounded,
              size: 58,
              color: Color(0xFFFFB020),
            ),
            const SizedBox(height: 18),
            const Text(
              'Unable to reach UrbanPulse',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.w800,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'Check that the UrbanPulse backend is running and try again.',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: Color(0xFF8B9AB5),
                height: 1.4,
              ),
            ),
            const SizedBox(height: 22),
            FilledButton.icon(
              onPressed: _loadBuses,
              icon: const Icon(Icons.refresh_rounded),
              label: const Text('Try Again'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Container(
      padding: const EdgeInsets.all(32),
      decoration: BoxDecoration(
        color: const Color(0xFF111A2A),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(
          color: const Color(0xFF25344D),
        ),
      ),
      child: const Column(
        children: [
          Icon(
            Icons.directions_bus_outlined,
            size: 52,
            color: Color(0xFF61718C),
          ),
          SizedBox(height: 14),
          Text(
            'No buses match this filter',
            style: TextStyle(
              fontWeight: FontWeight.w700,
              fontSize: 17,
            ),
          ),
          SizedBox(height: 6),
          Text(
            'Try another crowding category.',
            style: TextStyle(
              color: Color(0xFF8B9AB5),
            ),
          ),
        ],
      ),
    );
  }

  void _showBusDetails(BusModel bus) {
    final color = _occupancyColor(bus.occupancyLevel);

    showModalBottomSheet(
      context: context,
      backgroundColor: const Color(0xFF101928),
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(
          top: Radius.circular(24),
        ),
      ),
      builder: (context) {
        return SafeArea(
          child: Padding(
            padding: const EdgeInsets.fromLTRB(22, 18, 22, 28),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Center(
                  child: Container(
                    width: 42,
                    height: 4,
                    decoration: BoxDecoration(
                      color: const Color(0xFF34435C),
                      borderRadius: BorderRadius.circular(10),
                    ),
                  ),
                ),
                const SizedBox(height: 22),
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: const Color(0xFF1769E0).withValues(alpha: 0.14),
                        borderRadius: BorderRadius.circular(14),
                      ),
                      child: const Icon(
                        Icons.directions_bus_rounded,
                        color: Color(0xFF60A5FA),
                        size: 28,
                      ),
                    ),
                    const SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            bus.busId,
                            style: const TextStyle(
                              fontSize: 21,
                              fontWeight: FontWeight.w800,
                            ),
                          ),
                          const SizedBox(height: 3),
                          Text(
                            bus.routeId,
                            style: const TextStyle(
                              color: Color(0xFF60A5FA),
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ],
                      ),
                    ),
                    _LiveDot(status: bus.status),
                  ],
                ),
                const SizedBox(height: 22),
                Text(
                  bus.routeName,
                  style: const TextStyle(
                    fontSize: 15,
                    color: Color(0xFF9AA8BF),
                  ),
                ),
                const SizedBox(height: 20),
                Row(
                  children: [
                    Expanded(
                      child: _DetailItem(
                        icon: Icons.speed_rounded,
                        label: 'Speed',
                        value: '${bus.speed.toStringAsFixed(1)} km/h',
                      ),
                    ),
                    Expanded(
                      child: _DetailItem(
                        icon: Icons.people_alt_rounded,
                        label: 'Passengers',
                        value: '${bus.crowdCount} / ${bus.capacity}',
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    Expanded(
                      child: _DetailItem(
                        icon: Icons.my_location_rounded,
                        label: 'Location',
                        value:
                            '${bus.lat.toStringAsFixed(4)}, ${bus.lon.toStringAsFixed(4)}',
                      ),
                    ),
                    Expanded(
                      child: _DetailItem(
                        icon: Icons.update_rounded,
                        label: 'Updated',
                        value: _formatUpdated(bus.lastUpdated),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 20),
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 14,
                    vertical: 12,
                  ),
                  decoration: BoxDecoration(
                    color: color.withValues(alpha: 0.10),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: color.withValues(alpha: 0.28),
                    ),
                  ),
                  child: Row(
                    children: [
                      Icon(
                        Icons.groups_rounded,
                        color: color,
                        size: 20,
                      ),
                      const SizedBox(width: 10),
                      Text(
                        _occupancyLabel(bus.occupancyLevel),
                        style: TextStyle(
                          color: color,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                      const Spacer(),
                      Text(
                        '${(bus.occupancyPercentage * 100).round()}%',
                        style: TextStyle(
                          color: color,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}

class _BusCard extends StatelessWidget {
  final BusModel bus;
  final Color occupancyColor;
  final String occupancyLabel;
  final String updatedText;
  final VoidCallback onTap;

  const _BusCard({
    required this.bus,
    required this.occupancyColor,
    required this.occupancyLabel,
    required this.updatedText,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(18),
        child: Container(
          padding: const EdgeInsets.all(17),
          decoration: BoxDecoration(
            color: const Color(0xFF121B2B),
            borderRadius: BorderRadius.circular(18),
            border: Border.all(
              color: const Color(0xFF25344D),
            ),
          ),
          child: Column(
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(11),
                    decoration: BoxDecoration(
                      color: const Color(0xFF1769E0).withValues(alpha: 0.13),
                      borderRadius: BorderRadius.circular(13),
                    ),
                    child: const Icon(
                      Icons.directions_bus_rounded,
                      color: Color(0xFF60A5FA),
                      size: 25,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          bus.busId,
                          style: const TextStyle(
                            fontSize: 17,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                        const SizedBox(height: 3),
                        Text(
                          '${bus.routeId} • ${bus.routeName}',
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: const TextStyle(
                            color: Color(0xFF8796AF),
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ),
                  ),
                  _OccupancyBadge(
                    text: occupancyLabel,
                    color: occupancyColor,
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  const Icon(
                    Icons.speed_rounded,
                    size: 17,
                    color: Color(0xFF4DB6E8),
                  ),
                  const SizedBox(width: 6),
                  Text(
                    '${bus.speed.toStringAsFixed(1)} km/h',
                    style: const TextStyle(
                      color: Color(0xFF9AA8BF),
                      fontSize: 13,
                    ),
                  ),
                  const SizedBox(width: 18),
                  const Icon(
                    Icons.people_alt_rounded,
                    size: 17,
                    color: Color(0xFF4DB6E8),
                  ),
                  const SizedBox(width: 6),
                  Text(
                    '${bus.crowdCount} / ${bus.capacity} pax',
                    style: const TextStyle(
                      color: Color(0xFF9AA8BF),
                      fontSize: 13,
                    ),
                  ),
                  const Spacer(),
                  const Icon(
                    Icons.circle,
                    size: 8,
                    color: Color(0xFF00C897),
                  ),
                  const SizedBox(width: 5),
                  const Text(
                    'LIVE',
                    style: TextStyle(
                      color: Color(0xFF00C897),
                      fontSize: 11,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 13),
              ClipRRect(
                borderRadius: BorderRadius.circular(8),
                child: LinearProgressIndicator(
                  value: bus.occupancyPercentage,
                  minHeight: 5,
                  backgroundColor: const Color(0xFF26344B),
                  valueColor: AlwaysStoppedAnimation<Color>(
                    occupancyColor,
                  ),
                ),
              ),
              const SizedBox(height: 10),
              Row(
                children: [
                  const Icon(
                    Icons.location_on_outlined,
                    size: 14,
                    color: Color(0xFF64748B),
                  ),
                  const SizedBox(width: 4),
                  Text(
                    '${bus.lat.toStringAsFixed(4)}, ${bus.lon.toStringAsFixed(4)}',
                    style: const TextStyle(
                      color: Color(0xFF64748B),
                      fontSize: 11,
                    ),
                  ),
                  const Spacer(),
                  Text(
                    updatedText,
                    style: const TextStyle(
                      color: Color(0xFF64748B),
                      fontSize: 11,
                    ),
                  ),
                  const SizedBox(width: 4),
                  const Icon(
                    Icons.chevron_right_rounded,
                    size: 17,
                    color: Color(0xFF64748B),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _OccupancyBadge extends StatelessWidget {
  final String text;
  final Color color;

  const _OccupancyBadge({
    required this.text,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: 9,
        vertical: 6,
      ),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.10),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: color.withValues(alpha: 0.28),
        ),
      ),
      child: Text(
        text,
        style: TextStyle(
          color: color,
          fontSize: 10,
          fontWeight: FontWeight.w800,
        ),
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  final IconData icon;
  final String value;
  final String label;
  final Color iconColor;

  const _StatCard({
    required this.icon,
    required this.value,
    required this.label,
    required this.iconColor,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: 12,
        vertical: 14,
      ),
      decoration: BoxDecoration(
        color: const Color(0xFF121B2B),
        borderRadius: BorderRadius.circular(15),
        border: Border.all(
          color: const Color(0xFF25344D),
        ),
      ),
      child: Column(
        children: [
          Icon(
            icon,
            color: iconColor,
            size: 22,
          ),
          const SizedBox(height: 7),
          Text(
            value,
            style: const TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.w800,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            label,
            textAlign: TextAlign.center,
            style: const TextStyle(
              color: Color(0xFF71809A),
              fontSize: 9,
              fontWeight: FontWeight.w700,
            ),
          ),
        ],
      ),
    );
  }
}

class _DetailItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;

  const _DetailItem({
    required this.icon,
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(right: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                icon,
                size: 15,
                color: const Color(0xFF4DB6E8),
              ),
              const SizedBox(width: 5),
              Text(
                label,
                style: const TextStyle(
                  color: Color(0xFF71809A),
                  fontSize: 11,
                ),
              ),
            ],
          ),
          const SizedBox(height: 5),
          Text(
            value,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(
              fontSize: 13,
              fontWeight: FontWeight.w700,
            ),
          ),
        ],
      ),
    );
  }
}

class _LiveDot extends StatelessWidget {
  final String status;

  const _LiveDot({
    required this.status,
  });

  @override
  Widget build(BuildContext context) {
    final active = status.toLowerCase() == 'active';

    return Row(
      children: [
        Icon(
          Icons.circle,
          size: 8,
          color: active
              ? const Color(0xFF00C897)
              : const Color(0xFFFFB020),
        ),
        const SizedBox(width: 5),
        Text(
          active ? 'LIVE' : status.toUpperCase(),
          style: TextStyle(
            color: active
                ? const Color(0xFF00C897)
                : const Color(0xFFFFB020),
            fontSize: 11,
            fontWeight: FontWeight.w800,
          ),
        ),
      ],
    );
  }
}