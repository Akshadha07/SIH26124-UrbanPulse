import 'package:flutter/material.dart';
import '../models/hazard.dart';
import '../theme/app_colors.dart';
import 'status_badge.dart';

class HazardCard extends StatelessWidget {
  final HazardModel hazard;
  final VoidCallback? onTap;

  const HazardCard({
    Key? key,
    required this.hazard,
    this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final bool isCritical = hazard.isCriticalWaterlogging;
    final Color accentColor = isCritical ? AppColors.danger : AppColors.warning;

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(
          color: isCritical
              ? AppColors.danger.withOpacity(0.6)
              : AppColors.border,
          width: isCritical ? 1.5 : 1.0,
        ),
      ),
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
                        padding: const EdgeInsets.all(7),
                        decoration: BoxDecoration(
                          color: accentColor.withOpacity(0.18),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Icon(
                          isCritical ? Icons.flood : Icons.warning_rounded,
                          size: 16,
                          color: accentColor,
                        ),
                      ),
                      const SizedBox(width: 10),
                      Text(
                        hazard.hazardType.toUpperCase().replaceAll('_', ' '),
                        style: TextStyle(
                          color: isCritical ? AppColors.danger : AppColors.textPrimary,
                          fontWeight: FontWeight.bold,
                          fontSize: 13,
                        ),
                      ),
                    ],
                  ),
                  HazardBadge(
                    status: hazard.status,
                    isConfirmed: hazard.isConfirmed,
                  ),
                ],
              ),
              const SizedBox(height: 8),
              if (hazard.addressHint != null) ...[
                Text(
                  hazard.addressHint!,
                  style: const TextStyle(
                    color: AppColors.textSecondary,
                    fontSize: 12,
                  ),
                ),
                const SizedBox(height: 8),
              ],
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(
                    children: [
                      Icon(Icons.near_me, size: 12, color: AppColors.cyan),
                      const SizedBox(width: 4),
                      Text(
                        hazard.distanceMeters.round().toString() + ' m ahead',
                        style: const TextStyle(
                          color: AppColors.cyan,
                          fontWeight: FontWeight.w600,
                          fontSize: 11,
                        ),
                      ),
                    ],
                  ),
                  if (hazard.isCorroborated)
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(
                        color: AppColors.success.withOpacity(0.12),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Row(
                        children: [
                          Icon(Icons.verified, size: 10, color: AppColors.success),
                          const SizedBox(width: 3),
                          Text(
                            hazard.distinctBusCount.toString() + ' Buses Corroborated',
                            style: const TextStyle(
                              color: AppColors.success,
                              fontSize: 10,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ],
                      ),
                    ),
                  Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: AppColors.surfaceElevated,
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      'Priority: ' + hazard.priorityScore.toStringAsFixed(1),
                      style: const TextStyle(
                        color: AppColors.textMuted,
                        fontSize: 10,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
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
