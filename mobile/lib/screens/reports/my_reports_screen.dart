import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../models/citizen_report.dart';
import '../../services/api_service.dart';
import '../../theme/app_colors.dart';
import '../../widgets/empty_state.dart';

class MyReportsScreen extends StatefulWidget {
  const MyReportsScreen({super.key});

  @override
  State<MyReportsScreen> createState() => _MyReportsScreenState();
}

class _MyReportsScreenState extends State<MyReportsScreen> {
  final ApiService _api = ApiService();

  bool _loading = true;
  String? _error;
  List<CitizenReportModel> _reports = [];

  @override
  void initState() {
    super.initState();
    _loadReports();
  }

  Future<void> _loadReports() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final reports = await _api.getCitizenReports();
      if (!mounted) return;
      setState(() {
        _reports = reports;
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

  Color _getCategoryColor(String category) {
    switch (category.toLowerCase()) {
      case 'pothole':
        return AppColors.warning;
      case 'waterlogging':
        return AppColors.cyan;
      case 'road_damage':
        return AppColors.orange;
      case 'garbage':
        return AppColors.danger;
      case 'street_light':
        return Colors.amberAccent;
      default:
        return AppColors.textSecondary;
    }
  }

  IconData _getCategoryIcon(String category) {
    switch (category.toLowerCase()) {
      case 'pothole':
        return Icons.warning_amber_rounded;
      case 'waterlogging':
        return Icons.water_drop_outlined;
      case 'road_damage':
        return Icons.broken_image_outlined;
      case 'garbage':
        return Icons.delete_outline_rounded;
      case 'street_light':
        return Icons.lightbulb_outline;
      default:
        return Icons.report_problem_outlined;
    }
  }

  Color _getStatusColor(String status) {
    switch (status.toUpperCase()) {
      case 'SUBMITTED':
        return AppColors.primaryLight;
      case 'UNDER_REVIEW':
      case 'ACKNOWLEDGED':
        return AppColors.warning;
      case 'CONFIRMED':
      case 'IN_PROGRESS':
        return AppColors.orange;
      case 'RESOLVED':
      case 'VERIFIED':
        return AppColors.success;
      default:
        return AppColors.textSecondary;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.background,
        elevation: 0,
        title: const Text('My Reports History'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Refresh Reports',
            onPressed: _loading ? null : _loadReports,
          ),
        ],
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_loading && _reports.isEmpty) {
      return const Center(
        child: CircularProgressIndicator(color: AppColors.primaryLight),
      );
    }

    if (_error != null && _reports.isEmpty) {
      return ErrorStateWidget(
        message: 'Could not fetch submitted reports history. Please try again.',
        onRetry: _loadReports,
      );
    }

    if (_reports.isEmpty) {
      return RefreshIndicator(
        onRefresh: _loadReports,
        child: ListView(
          physics: const AlwaysScrollableScrollPhysics(),
          children: [
            SizedBox(
              height: MediaQuery.of(context).size.height * 0.7,
              child: const EmptyStateWidget(
                icon: Icons.assignment_outlined,
                title: 'No Reports Filed Yet',
                description: 'Your submitted road damage and waterlogging reports will be tracked here.',
              ),
            ),
          ],
        ),
      );
    }

    final totalCount = _reports.length;
    final resolvedCount = _reports
        .where((r) => r.status.toUpperCase() == 'RESOLVED' || r.status.toUpperCase() == 'VERIFIED')
        .length;
    final pendingCount = totalCount - resolvedCount;

    final dateFormat = DateFormat('dd MMM yyyy, hh:mm a');

    return RefreshIndicator(
      onRefresh: _loadReports,
      color: AppColors.primaryLight,
      child: ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.fromLTRB(16, 8, 16, 32),
        children: [
          // Summary Statistics Card
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppColors.surface,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: AppColors.border),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildStatItem('Total Filed', '$totalCount', Icons.assignment_outlined, AppColors.cyan),
                _buildStatItem('In Review', '$pendingCount', Icons.pending_actions, AppColors.warning),
                _buildStatItem('Resolved', '$resolvedCount', Icons.task_alt, AppColors.success),
              ],
            ),
          ),

          const SizedBox(height: 18),

          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'SUBMISSION LOG',
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w700,
                  color: AppColors.textMuted,
                  letterSpacing: 0.8,
                ),
              ),
              Text(
                '$totalCount records',
                style: const TextStyle(
                  fontSize: 11,
                  color: AppColors.textSecondary,
                ),
              ),
            ],
          ),

          const SizedBox(height: 10),

          ..._reports.map((report) {
            final catColor = _getCategoryColor(report.category);
            final statusColor = _getStatusColor(report.status);

            return Container(
              margin: const EdgeInsets.only(bottom: 12),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppColors.surface,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppColors.border),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: catColor.withValues(alpha: 0.15),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: Icon(
                          _getCategoryIcon(report.category),
                          color: catColor,
                          size: 20,
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
                                  report.category.replaceAll('_', ' ').toUpperCase(),
                                  style: const TextStyle(
                                    fontSize: 13,
                                    fontWeight: FontWeight.bold,
                                    color: AppColors.textPrimary,
                                  ),
                                ),
                                const SizedBox(width: 8),
                                Text(
                                  '#${report.id}',
                                  style: const TextStyle(
                                    fontSize: 11,
                                    color: AppColors.textMuted,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 2),
                            Text(
                              dateFormat.format(report.createdAt.toLocal()),
                              style: const TextStyle(
                                fontSize: 10,
                                color: AppColors.textMuted,
                              ),
                            ),
                          ],
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                        decoration: BoxDecoration(
                          color: statusColor.withValues(alpha: 0.15),
                          borderRadius: BorderRadius.circular(6),
                          border: Border.all(color: statusColor.withValues(alpha: 0.4)),
                        ),
                        child: Text(
                          report.status.toUpperCase(),
                          style: TextStyle(
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                            color: statusColor,
                          ),
                        ),
                      ),
                    ],
                  ),

                  if (report.description != null && report.description!.isNotEmpty) ...[
                    const SizedBox(height: 10),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: AppColors.surfaceElevated,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        report.description!,
                        style: const TextStyle(
                          fontSize: 12,
                          color: AppColors.textSecondary,
                          height: 1.3,
                        ),
                      ),
                    ),
                  ],

                  const SizedBox(height: 10),

                  Row(
                    children: [
                      const Icon(Icons.location_on_outlined, size: 14, color: AppColors.textMuted),
                      const SizedBox(width: 4),
                      Text(
                        '${report.lat.toStringAsFixed(4)}, ${report.lon.toStringAsFixed(4)}',
                        style: const TextStyle(
                          fontSize: 11,
                          color: AppColors.textMuted,
                        ),
                      ),
                      const Spacer(),
                      if (report.photoUrl != null)
                        Row(
                          children: const [
                            Icon(Icons.photo_outlined, size: 14, color: AppColors.cyan),
                            SizedBox(width: 4),
                            Text(
                              'Photo attached',
                              style: TextStyle(fontSize: 11, color: AppColors.cyan),
                            ),
                          ],
                        ),
                    ],
                  ),
                ],
              ),
            );
          }),
        ],
      ),
    );
  }

  Widget _buildStatItem(String label, String value, IconData icon, Color color) {
    return Column(
      children: [
        Icon(icon, size: 20, color: color),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        Text(
          label,
          style: const TextStyle(
            fontSize: 11,
            color: AppColors.textMuted,
          ),
        ),
      ],
    );
  }
}
