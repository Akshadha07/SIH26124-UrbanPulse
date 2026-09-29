import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../../config/api_config.dart';
import '../../services/api_service.dart';
import '../../services/location_service.dart';
import '../../theme/app_colors.dart';
import 'my_reports_screen.dart';

class ReportIssueScreen extends StatefulWidget {
  const ReportIssueScreen({super.key});

  @override
  State<ReportIssueScreen> createState() => _ReportIssueScreenState();
}

class _ReportIssueScreenState extends State<ReportIssueScreen> {
  final ApiService _api = ApiService();
  final LocationService _location = LocationService();
  final ImagePicker _picker = ImagePicker();

  String _selectedCategory = 'pothole';
  final TextEditingController _descriptionController = TextEditingController();
  late TextEditingController _latController;
  late TextEditingController _lonController;

  bool _submitting = false;
  XFile? _selectedImage;
  String? _successReportId;

  final List<Map<String, dynamic>> _categories = [
    {
      'id': 'pothole',
      'label': 'Pothole',
      'icon': Icons.warning_amber_rounded,
      'color': AppColors.warning,
      'desc': 'Deep craters, road surface depressions',
    },
    {
      'id': 'waterlogging',
      'label': 'Waterlogging',
      'icon': Icons.water_drop_outlined,
      'color': AppColors.cyan,
      'desc': 'Road submergence, flooded underpasses',
    },
    {
      'id': 'road_damage',
      'label': 'Road Damage',
      'icon': Icons.broken_image_outlined,
      'color': AppColors.orange,
      'desc': 'Asphalt cracking, missing road barriers',
    },
    {
      'id': 'garbage',
      'label': 'Garbage Dump',
      'icon': Icons.delete_outline_rounded,
      'color': AppColors.danger,
      'desc': 'Uncollected debris obstructing traffic',
    },
    {
      'id': 'street_light',
      'label': 'Street Light',
      'icon': Icons.lightbulb_outline,
      'color': Colors.amberAccent,
      'desc': 'Dark corridor, non-functional street lamp',
    },
    {
      'id': 'other',
      'label': 'Other Civic Issue',
      'icon': Icons.report_problem_outlined,
      'color': AppColors.textSecondary,
      'desc': 'Traffic hazard or municipal obstruction',
    },
  ];

  @override
  void initState() {
    super.initState();
    _latController = TextEditingController(
      text: _location.currentLat.toStringAsFixed(4),
    );
    _lonController = TextEditingController(
      text: _location.currentLon.toStringAsFixed(4),
    );
  }

  @override
  void dispose() {
    _descriptionController.dispose();
    _latController.dispose();
    _lonController.dispose();
    super.dispose();
  }

  Future<void> _pickImage() async {
    try {
      final image = await _picker.pickImage(
        source: ImageSource.gallery,
        maxWidth: 1024,
        maxHeight: 1024,
        imageQuality: 80,
      );
      if (image != null && mounted) {
        setState(() {
          _selectedImage = image;
        });
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Could not access image: $e'),
            backgroundColor: AppColors.danger,
          ),
        );
      }
    }
  }

  Future<void> _submitReport() async {
    final lat = double.tryParse(_latController.text.trim());
    final lon = double.tryParse(_lonController.text.trim());

    if (lat == null || lon == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please provide valid latitude and longitude coordinates.'),
          backgroundColor: AppColors.danger,
        ),
      );
      return;
    }

    setState(() {
      _submitting = true;
      _successReportId = null;
    });

    try {
      final report = await _api.submitCitizenReport(
        category: _selectedCategory,
        lat: lat,
        lon: lon,
        description: _descriptionController.text.trim().isEmpty
            ? null
            : _descriptionController.text.trim(),
        photoUrl: _selectedImage != null ? '/assets/citizen_reports/${_selectedImage!.name}' : null,
      );

      if (!mounted) return;

      setState(() {
        _submitting = false;
        _successReportId = report.id.toString();
        _descriptionController.clear();
        _selectedImage = null;
      });

      _showSuccessDialog(report.id);
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _submitting = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Submission failed: $e'),
          backgroundColor: AppColors.danger,
        ),
      );
    }
  }

  void _showSuccessDialog(int reportId) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppColors.surface,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: Row(
          children: const [
            Icon(Icons.check_circle, color: AppColors.success, size: 28),
            SizedBox(width: 10),
            Text('Report Registered', style: TextStyle(fontWeight: FontWeight.bold)),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Your report #$reportId has been submitted to the Vadodara Municipal Control Center and broadcast in real-time.',
              style: const TextStyle(fontSize: 13, color: AppColors.textPrimary, height: 1.4),
            ),
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: AppColors.surfaceElevated,
                borderRadius: BorderRadius.circular(10),
              ),
              child: Row(
                children: [
                  const Icon(Icons.hub_outlined, color: AppColors.cyan, size: 16),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Category: $_selectedCategory • Status: SUBMITTED',
                      style: const TextStyle(fontSize: 11, color: AppColors.textSecondary),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('New Report', style: TextStyle(color: AppColors.textSecondary)),
          ),
          FilledButton.icon(
            onPressed: () {
              Navigator.of(ctx).pop();
              Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => const MyReportsScreen()),
              );
            },
            icon: const Icon(Icons.history, size: 16),
            label: const Text('View My Reports'),
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
        title: const Text('Report Urban Issue'),
        actions: [
          TextButton.icon(
            onPressed: () {
              Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => const MyReportsScreen()),
              );
            },
            icon: const Icon(Icons.history, color: AppColors.primaryLight, size: 18),
            label: const Text(
              'History',
              style: TextStyle(color: AppColors.primaryLight, fontWeight: FontWeight.bold),
            ),
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(16, 8, 16, 32),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Top Explanation Banner
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: AppColors.surface,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: AppColors.border),
              ),
              child: Row(
                children: const [
                  Icon(Icons.shield_outlined, color: AppColors.cyan, size: 22),
                  SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      'Citizen reports directly assist AI sensor fusion by providing ground-truth verification of road hazards.',
                      style: TextStyle(
                        fontSize: 12,
                        color: AppColors.textSecondary,
                        height: 1.35,
                      ),
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 20),

            // Category Selection Header
            const Text(
              'SELECT HAZARD CATEGORY',
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w700,
                color: AppColors.textMuted,
                letterSpacing: 0.8,
              ),
            ),
            const SizedBox(height: 12),

            // Category Grid
            GridView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: _categories.length,
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                crossAxisSpacing: 10,
                mainAxisSpacing: 10,
                childAspectRatio: 2.2,
              ),
              itemBuilder: (context, index) {
                final cat = _categories[index];
                final isSelected = _selectedCategory == cat['id'];
                final catColor = cat['color'] as Color;

                return InkWell(
                  onTap: () {
                    setState(() {
                      _selectedCategory = cat['id'];
                    });
                  },
                  borderRadius: BorderRadius.circular(12),
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                    decoration: BoxDecoration(
                      color: isSelected
                          ? catColor.withValues(alpha: 0.15)
                          : AppColors.surface,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(
                        color: isSelected ? catColor : AppColors.border,
                        width: isSelected ? 1.5 : 1.0,
                      ),
                    ),
                    child: Row(
                      children: [
                        Icon(
                          cat['icon'] as IconData,
                          color: isSelected ? catColor : AppColors.textSecondary,
                          size: 20,
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Text(
                                cat['label'],
                                style: TextStyle(
                                  fontSize: 12,
                                  fontWeight: FontWeight.bold,
                                  color: isSelected ? AppColors.textPrimary : AppColors.textSecondary,
                                ),
                              ),
                              Text(
                                cat['desc'],
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                                style: const TextStyle(
                                  fontSize: 9,
                                  color: AppColors.textMuted,
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
            ),

            const SizedBox(height: 22),

            // Location Section
            const Text(
              'INCIDENT LOCATION (VADODARA)',
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w700,
                color: AppColors.textMuted,
                letterSpacing: 0.8,
              ),
            ),
            const SizedBox(height: 8),

            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: AppColors.surface,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: AppColors.border),
              ),
              child: Column(
                children: [
                  Row(
                    children: [
                      const Icon(Icons.my_location, color: AppColors.cyan, size: 18),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          'Current Area: ${_location.locationName}',
                          style: const TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            color: AppColors.textPrimary,
                          ),
                        ),
                      ),
                      TextButton(
                        onPressed: () {
                          setState(() {
                            _latController.text = ApiConfig.defaultLat.toStringAsFixed(4);
                            _lonController.text = ApiConfig.defaultLon.toStringAsFixed(4);
                          });
                        },
                        child: const Text('Reset', style: TextStyle(fontSize: 11)),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: _latController,
                          keyboardType: const TextInputType.numberWithOptions(decimal: true),
                          style: const TextStyle(fontSize: 13, color: AppColors.textPrimary),
                          decoration: InputDecoration(
                            labelText: 'Latitude',
                            labelStyle: const TextStyle(fontSize: 11, color: AppColors.textMuted),
                            filled: true,
                            fillColor: AppColors.surfaceElevated,
                            contentPadding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(8),
                              borderSide: const BorderSide(color: AppColors.border),
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: TextField(
                          controller: _lonController,
                          keyboardType: const TextInputType.numberWithOptions(decimal: true),
                          style: const TextStyle(fontSize: 13, color: AppColors.textPrimary),
                          decoration: InputDecoration(
                            labelText: 'Longitude',
                            labelStyle: const TextStyle(fontSize: 11, color: AppColors.textMuted),
                            filled: true,
                            fillColor: AppColors.surfaceElevated,
                            contentPadding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(8),
                              borderSide: const BorderSide(color: AppColors.border),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(height: 22),

            // Description Section
            const Text(
              'DESCRIPTION (OPTIONAL)',
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w700,
                color: AppColors.textMuted,
                letterSpacing: 0.8,
              ),
            ),
            const SizedBox(height: 8),

            TextField(
              controller: _descriptionController,
              maxLines: 3,
              maxLength: 250,
              style: const TextStyle(fontSize: 13, color: AppColors.textPrimary),
              decoration: InputDecoration(
                hintText: 'Describe size, severity, landmarks or lane obstruction...',
                hintStyle: const TextStyle(fontSize: 12, color: AppColors.textMuted),
                filled: true,
                fillColor: AppColors.surface,
                counterStyle: const TextStyle(fontSize: 10, color: AppColors.textMuted),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: const BorderSide(color: AppColors.border),
                ),
                enabledBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: const BorderSide(color: AppColors.border),
                ),
              ),
            ),

            const SizedBox(height: 12),

            // Photo Evidence Section
            const Text(
              'PHOTO EVIDENCE (OPTIONAL)',
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w700,
                color: AppColors.textMuted,
                letterSpacing: 0.8,
              ),
            ),
            const SizedBox(height: 8),

            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: AppColors.surface,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppColors.border),
              ),
              child: Row(
                children: [
                  Container(
                    width: 44,
                    height: 44,
                    decoration: BoxDecoration(
                      color: AppColors.surfaceElevated,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Icon(
                      _selectedImage != null ? Icons.image : Icons.add_a_photo_outlined,
                      color: _selectedImage != null ? AppColors.success : AppColors.textMuted,
                      size: 20,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          _selectedImage != null
                              ? 'Image Attached: ${_selectedImage!.name}'
                              : 'Attach Photo Evidence',
                          style: const TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            color: AppColors.textPrimary,
                          ),
                        ),
                        const SizedBox(height: 2),
                        const Text(
                          'Supports ground-truth confirmation',
                          style: TextStyle(fontSize: 10, color: AppColors.textMuted),
                        ),
                      ],
                    ),
                  ),
                  OutlinedButton(
                    onPressed: _pickImage,
                    style: OutlinedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                    ),
                    child: Text(_selectedImage != null ? 'Change' : 'Choose'),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 26),

            // Submit Button
            SizedBox(
              width: double.infinity,
              height: 50,
              child: FilledButton.icon(
                onPressed: _submitting ? null : _submitReport,
                style: FilledButton.styleFrom(
                  backgroundColor: AppColors.primary,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14),
                  ),
                ),
                icon: _submitting
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Colors.white,
                        ),
                      )
                    : const Icon(Icons.send_rounded),
                label: Text(
                  _submitting ? 'Transmitting to VMC...' : 'Submit Citizen Report',
                  style: const TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
