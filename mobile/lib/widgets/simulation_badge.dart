import 'package:flutter/material.dart';
import '../theme/app_colors.dart';

class SimulationBadge extends StatelessWidget {
  const SimulationBadge({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: AppColors.warning.withOpacity(0.12),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(
          color: AppColors.warning.withOpacity(0.4),
          width: 0.8,
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            Icons.sensors,
            size: 11,
            color: AppColors.warning,
          ),
          const SizedBox(width: 4),
          const Text(
            'SIMULATED FLEET',
            style: TextStyle(
              color: AppColors.warning,
              fontSize: 9.5,
              fontWeight: FontWeight.w700,
              letterSpacing: 0.6,
            ),
          ),
        ],
      ),
    );
  }
}
