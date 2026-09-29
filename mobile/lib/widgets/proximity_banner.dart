import 'package:flutter/material.dart';
import '../services/notification_service.dart';
import '../theme/app_colors.dart';

class ProximityBanner extends StatelessWidget {
  final ProximityAlert alert;
  final VoidCallback onDismiss;
  final VoidCallback? onTap;

  const ProximityBanner({
    Key? key,
    required this.alert,
    required this.onDismiss,
    this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final bool isCritical = alert.isCritical;
    final Color borderColor = isCritical ? AppColors.danger : AppColors.warning;
    final Color bgColor = isCritical
        ? AppColors.danger.withOpacity(0.18)
        : AppColors.warning.withOpacity(0.15);

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: borderColor.withOpacity(0.7), width: 1.2),
        boxShadow: [
          BoxShadow(
            color: borderColor.withOpacity(0.2),
            blurRadius: 10,
            offset: const Offset(0, 3),
          )
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(14),
          onTap: onTap,
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: borderColor.withOpacity(0.25),
                    shape: BoxShape.circle,
                  ),
                  child: Icon(
                    isCritical ? Icons.flood : Icons.warning_amber_rounded,
                    color: borderColor,
                    size: 20,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        alert.title,
                        style: TextStyle(
                          color: borderColor,
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                          letterSpacing: 0.2,
                        ),
                      ),
                      const SizedBox(height: 3),
                      Text(
                        alert.message,
                        style: const TextStyle(
                          color: AppColors.textPrimary,
                          fontSize: 12,
                          height: 1.3,
                        ),
                      ),
                    ],
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.close, size: 16, color: AppColors.textMuted),
                  padding: EdgeInsets.zero,
                  constraints: const BoxConstraints(),
                  onPressed: onDismiss,
                )
              ],
            ),
          ),
        ),
      ),
    );
  }
}
