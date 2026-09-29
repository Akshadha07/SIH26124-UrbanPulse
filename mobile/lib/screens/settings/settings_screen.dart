import 'package:flutter/material.dart';
import '../../config/api_config.dart';
import '../../services/location_service.dart';
import '../../theme/app_colors.dart';
import '../../widgets/simulation_badge.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final LocationService _location = LocationService();
  bool _proximityAlertsEnabled = true;
  bool _disasterAlertsEnabled = true;

  void _showCustomHostDialog() {
    final hostController = TextEditingController();
    final portController = TextEditingController(text: '8000');

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppColors.surface,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Text('Set Custom Backend Host'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: hostController,
              decoration: const InputDecoration(
                labelText: 'Host IP / Domain',
                hintText: 'e.g. 192.168.1.100',
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: portController,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(
                labelText: 'Port',
                hintText: '8000',
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () {
              final host = hostController.text.trim();
              final port = int.tryParse(portController.text.trim()) ?? 8000;
              if (host.isNotEmpty) {
                setState(() {
                  ApiConfig.setCustomHost(host, port: port);
                });
              }
              Navigator.of(ctx).pop();
            },
            child: const Text('Save & Apply'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.background,
        elevation: 0,
        title: const Text('Settings & System Info'),
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(16, 8, 16, 32),
        children: [
          // Application Identity Card
          Container(
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
              color: AppColors.surface,
              borderRadius: BorderRadius.circular(18),
              border: Border.all(color: AppColors.border),
            ),
            child: Row(
              children: [
                Container(
                  width: 52,
                  height: 52,
                  decoration: BoxDecoration(
                    color: AppColors.primary.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(14),
                  ),
                  child: const Icon(
                    Icons.directions_bus,
                    color: AppColors.primaryLight,
                    size: 28,
                  ),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: const [
                          Text(
                            'BEL UrbanPulse',
                            style: TextStyle(
                              fontSize: 17,
                              fontWeight: FontWeight.bold,
                              color: AppColors.textPrimary,
                            ),
                          ),
                          SizedBox(width: 8),
                          SimulationBadge(),
                        ],
                      ),
                      const SizedBox(height: 3),
                      const Text(
                        'AI Mobile Urban Intelligence Platform',
                        style: TextStyle(
                          fontSize: 11,
                          color: AppColors.textSecondary,
                        ),
                      ),
                      const SizedBox(height: 2),
                      const Text(
                        'Bharat Electronics Limited (BEL) • SIH26124',
                        style: TextStyle(
                          fontSize: 10,
                          color: AppColors.cyan,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 20),

          // Section 1: Backend Connection
          _buildSectionHeader('BACKEND CONNECTION & API'),
          const SizedBox(height: 8),
          Container(
            decoration: BoxDecoration(
              color: AppColors.surface,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: AppColors.border),
            ),
            child: Column(
              children: [
                ListTile(
                  leading: const Icon(Icons.cloud_outlined, color: AppColors.primaryLight),
                  title: const Text('REST API Base URL', style: TextStyle(fontSize: 13)),
                  subtitle: Text(
                    ApiConfig.baseUrl,
                    style: const TextStyle(fontSize: 11, color: AppColors.textMuted),
                  ),
                ),
                const Divider(height: 1, color: AppColors.border),
                ListTile(
                  leading: const Icon(Icons.hub_outlined, color: AppColors.cyan),
                  title: const Text('Real-Time WebSocket', style: TextStyle(fontSize: 13)),
                  subtitle: Text(
                    ApiConfig.wsUrl,
                    style: const TextStyle(fontSize: 11, color: AppColors.textMuted),
                  ),
                ),
                const Divider(height: 1, color: AppColors.border),
                Padding(
                  padding: const EdgeInsets.all(12),
                  child: Row(
                    children: [
                      Expanded(
                        child: OutlinedButton(
                          onPressed: () {
                            setState(() {
                              ApiConfig.useLocalhost();
                            });
                          },
                          child: const Text('Localhost', style: TextStyle(fontSize: 11)),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: OutlinedButton(
                          onPressed: () {
                            setState(() {
                              ApiConfig.useAndroidEmulator();
                            });
                          },
                          child: const Text('Android 10.0.2.2', style: TextStyle(fontSize: 11)),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: OutlinedButton(
                          onPressed: _showCustomHostDialog,
                          child: const Text('Custom IP', style: TextStyle(fontSize: 11)),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 20),

          // Section 2: Commuter Preferences
          _buildSectionHeader('COMMUTE & SAFETY ALERTS'),
          const SizedBox(height: 8),
          Container(
            decoration: BoxDecoration(
              color: AppColors.surface,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: AppColors.border),
            ),
            child: Column(
              children: [
                SwitchListTile(
                  value: _proximityAlertsEnabled,
                  onChanged: (val) {
                    setState(() {
                      _proximityAlertsEnabled = val;
                    });
                  },
                  secondary: const Icon(Icons.near_me_outlined, color: AppColors.warning),
                  title: const Text('Proximity Hazard Alerts', style: TextStyle(fontSize: 13)),
                  subtitle: const Text(
                    'Banner alerts for confirmed defects within 400m',
                    style: TextStyle(fontSize: 11, color: AppColors.textMuted),
                  ),
                ),
                const Divider(height: 1, color: AppColors.border),
                SwitchListTile(
                  value: _disasterAlertsEnabled,
                  onChanged: (val) {
                    setState(() {
                      _disasterAlertsEnabled = val;
                    });
                  },
                  secondary: const Icon(Icons.flood_outlined, color: AppColors.danger),
                  title: const Text('Monsoon Flood Emergency Flash', style: TextStyle(fontSize: 13)),
                  subtitle: const Text(
                    'Priority emergency broadcasts for underpass waterlogging',
                    style: TextStyle(fontSize: 11, color: AppColors.textMuted),
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 20),

          // Section 3: Pilot City & Geolocation
          _buildSectionHeader('PILOT REGION & GEODATA'),
          const SizedBox(height: 8),
          Container(
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
                    const Icon(Icons.location_city, color: AppColors.cyan, size: 20),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        'Target Pilot City: ${ApiConfig.cityName}',
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  'Default GPS: ${ApiConfig.defaultLat.toStringAsFixed(4)}° N, ${ApiConfig.defaultLon.toStringAsFixed(4)}° E',
                  style: const TextStyle(fontSize: 11, color: AppColors.textSecondary),
                ),
                const SizedBox(height: 4),
                Text(
                  'Current Simulated Area: ${_location.locationName}',
                  style: const TextStyle(fontSize: 11, color: AppColors.textMuted),
                ),
              ],
            ),
          ),

          const SizedBox(height: 20),

          // Section 4: Data Transparency & Edge AI Architecture
          _buildSectionHeader('DATA TRANSPARENCY & EDGE PRIVACY'),
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppColors.surface,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: AppColors.border),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: const [
                Text(
                  'Edge Processing & Privacy Safeguards',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: AppColors.textPrimary),
                ),
                SizedBox(height: 6),
                Text(
                  '1. Edge CV on Public Transport: All video streams from bus-mounted cameras are analyzed on local edge hardware. Raw footage is never transmitted or retained in cloud storage.\n'
                  '2. Multi-Modal Corroboration: Defects are only confirmed when cross-verified across independent buses and sensor types (optical + IMU vibration).\n'
                  '3. Prototype Notice: Fleet telemetry in this prototype is driven by the BEL UrbanPulse simulation engine for demonstration of SIH26124 requirements.\n'
                  '4. Citizen Geolocation: Location access is only utilized during deliberate issue submission to pin civic defects accurately.',
                  style: TextStyle(fontSize: 11, color: AppColors.textSecondary, height: 1.4),
                ),
                SizedBox(height: 12),
                Text(
                  'Pipeline: OBSERVE → DETECT → CONFIRM → PRIORITIZE → ACT → VERIFY',
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                    color: AppColors.primaryLight,
                    letterSpacing: 0.5,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Text(
      title,
      style: const TextStyle(
        fontSize: 11,
        fontWeight: FontWeight.w700,
        color: AppColors.textMuted,
        letterSpacing: 0.8,
      ),
    );
  }
}
