import 'package:flutter/material.dart';
import '../models/aqi.dart';
import '../theme/app_colors.dart';

class AqiCard extends StatelessWidget {
  final AqiPointModel aqi;
  final VoidCallback? onTap;

  const AqiCard({
    Key? key,
    required this.aqi,
    this.onTap,
  }) : super(key: key);

  Color get categoryColor {
    final cat = aqi.category.toLowerCase();
    if (cat.contains('good')) return AppColors.success;
    if (cat.contains('moderate')) return AppColors.warning;
    if (cat.contains('poor') && !cat.contains('very')) return AppColors.orange;
    return AppColors.danger;
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Row(
            children: [
              Container(
                width: 52,
                height: 52,
                decoration: BoxDecoration(
                  color: categoryColor.withOpacity(0.18),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: categoryColor.withOpacity(0.5)),
                ),
                child: Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        aqi.aqiValue.round().toString(),
                        style: TextStyle(
                          color: categoryColor,
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const Text(
                        'AQI',
                        style: TextStyle(
                          color: AppColors.textMuted,
                          fontSize: 9,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          aqi.category.toUpperCase(),
                          style: TextStyle(
                            color: categoryColor,
                            fontWeight: FontWeight.bold,
                            fontSize: 13,
                          ),
                        ),
                        Text(
                          'Bus: ' + aqi.busId,
                          style: const TextStyle(
                            color: AppColors.textMuted,
                            fontSize: 11,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'PM2.5: ' +
                          aqi.pm25.toStringAsFixed(1) +
                          ' µg/m³' +
                          (aqi.pm10 != null ? ' • PM10: ' + aqi.pm10!.toStringAsFixed(1) : ''),
                      style: const TextStyle(
                        color: AppColors.textSecondary,
                        fontSize: 12,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      'Mobile sensing node at (${aqi.lat.toStringAsFixed(3)}, ${aqi.lon.toStringAsFixed(3)})',
                      style: const TextStyle(
                        color: AppColors.textMuted,
                        fontSize: 10,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
