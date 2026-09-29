import 'package:flutter/material.dart';
import '../theme/app_colors.dart';

class OccupancyBadge extends StatelessWidget {
  final String level;
  final bool showLabel;

  const OccupancyBadge({
    Key? key,
    required this.level,
    this.showLabel = true,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    Color bg;
    Color fg;
    String label;
    IconData icon;

    switch (level.toLowerCase()) {
      case 'low':
        bg = AppColors.success.withOpacity(0.15);
        fg = AppColors.success;
        label = 'Low Crowding';
        icon = Icons.airline_seat_recline_normal;
        break;
      case 'moderate':
      case 'medium':
        bg = AppColors.warning.withOpacity(0.15);
        fg = AppColors.warning;
        label = 'Moderate';
        icon = Icons.people_outline;
        break;
      case 'high':
        bg = AppColors.orange.withOpacity(0.15);
        fg = AppColors.orange;
        label = 'High Crowding';
        icon = Icons.groups;
        break;
      case 'full':
        bg = AppColors.danger.withOpacity(0.15);
        fg = AppColors.danger;
        label = 'Standing Only';
        icon = Icons.warning_amber_rounded;
        break;
      default:
        bg = AppColors.surfaceElevated;
        fg = AppColors.textSecondary;
        label = level.toUpperCase();
        icon = Icons.people;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3.5),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: fg.withOpacity(0.3), width: 1),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 12, color: fg),
          if (showLabel) ...[
            const SizedBox(width: 4),
            Text(
              label,
              style: TextStyle(
                color: fg,
                fontSize: 11,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class HazardBadge extends StatelessWidget {
  final String status;
  final bool isConfirmed;

  const HazardBadge({
    Key? key,
    required this.status,
    required this.isConfirmed,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    Color color = AppColors.warning;
    String label = isConfirmed ? 'CONFIRMED' : 'REPORTED';

    if (status.toUpperCase().contains('DISASTER')) {
      color = AppColors.danger;
      label = 'DISASTER ESCALATION';
    } else if (status.toUpperCase().contains('REPAIR') ||
        status.toUpperCase().contains('PROGRESS')) {
      color = AppColors.cyan;
      label = 'IN REPAIR';
    } else if (status.toUpperCase().contains('RESOLVED')) {
      color = AppColors.success;
      label = 'RESOLVED';
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2.5),
      decoration: BoxDecoration(
        color: color.withOpacity(0.12),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: color.withOpacity(0.35), width: 0.8),
      ),
      child: Text(
        label,
        style: TextStyle(
          color: color,
          fontSize: 10,
          fontWeight: FontWeight.w700,
          letterSpacing: 0.3,
        ),
      ),
    );
  }
}
