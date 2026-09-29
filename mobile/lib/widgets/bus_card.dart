import 'package:flutter/material.dart';
import '../models/bus.dart';
import '../theme/app_colors.dart';
import 'status_badge.dart';

class BusCard extends StatelessWidget {
  final BusModel bus;
  final VoidCallback? onTap;

  const BusCard({
    Key? key,
    required this.bus,
    this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: AppColors.primary.withOpacity(0.18),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(
                              color: AppColors.primary.withOpacity(0.4)),
                        ),
                        child: Text(
                          bus.routeId,
                          style: const TextStyle(
                            color: AppColors.primaryLight,
                            fontWeight: FontWeight.bold,
                            fontSize: 12,
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        bus.busId,
                        style: const TextStyle(
                          color: AppColors.textPrimary,
                          fontWeight: FontWeight.w600,
                          fontSize: 14,
                        ),
                      ),
                    ],
                  ),
                  OccupancyBadge(level: bus.occupancyLevel),
                ],
              ),
              const SizedBox(height: 10),
              Text(
                bus.routeName,
                style: const TextStyle(
                  color: AppColors.textSecondary,
                  fontSize: 13,
                ),
              ),
              const SizedBox(height: 12),
              // Occupancy progress bar
              Row(
                children: [
                  Expanded(
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(4),
                      child: LinearProgressIndicator(
                        value: bus.occupancyPercentage,
                        backgroundColor: AppColors.surfaceElevated,
                        valueColor: AlwaysStoppedAnimation<Color>(
                          bus.occupancyPercentage > 0.8
                              ? AppColors.danger
                              : bus.occupancyPercentage > 0.5
                                  ? AppColors.warning
                                  : AppColors.success,
                        ),
                        minHeight: 6,
                      ),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Text(
                    bus.crowdCount.toString() + ' / ' + bus.capacity.toString() + ' pax',
                    style: const TextStyle(
                      color: AppColors.textMuted,
                      fontSize: 11,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(
                    children: [
                      Icon(Icons.speed, size: 12, color: AppColors.cyan),
                      const SizedBox(width: 4),
                      Text(
                        bus.speed.toStringAsFixed(1) + ' km/h',
                        style: const TextStyle(
                          color: AppColors.textMuted,
                          fontSize: 11,
                        ),
                      ),
                    ],
                  ),
                  Row(
                    children: [
                      Container(
                        width: 6,
                        height: 6,
                        decoration: const BoxDecoration(
                          color: AppColors.success,
                          shape: BoxShape.circle,
                        ),
                      ),
                      const SizedBox(width: 4),
                      const Text(
                        'LIVE TELEMETRY',
                        style: TextStyle(
                          color: AppColors.success,
                          fontSize: 9.5,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
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
