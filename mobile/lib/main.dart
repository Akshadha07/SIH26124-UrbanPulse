import 'package:flutter/material.dart';
import 'theme/app_theme.dart';
import 'screens/home/home_screen.dart';
import 'screens/buses/live_buses_screen.dart';
import 'screens/hazards/hazard_alerts_screen.dart';
import 'screens/reports/report_issue_screen.dart';
import 'screens/journey/journey_screen.dart';
import 'screens/aqi/aqi_screen.dart';
import 'screens/settings/settings_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const UrbanPulseApp());
}

class UrbanPulseApp extends StatelessWidget {
  const UrbanPulseApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'BEL UrbanPulse',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme,
      routes: {
        '/journey': (_) => const JourneyScreen(),
        '/aqi': (_) => const AqiScreen(),
        '/settings': (_) => const SettingsScreen(),
      },
      home: const MainNavigationShell(),
    );
  }
}

class MainNavigationShell extends StatefulWidget {
  const MainNavigationShell({super.key});

  @override
  State<MainNavigationShell> createState() => _MainNavigationShellState();
}

class _MainNavigationShellState extends State<MainNavigationShell> {
  int _currentIndex = 0;

  void _navigateToTab(int index) {
    setState(() {
      _currentIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: [
          HomeScreen(onNavigateTab: _navigateToTab),
          const LiveBusesScreen(),
          const HazardAlertsScreen(),
          const ReportIssueScreen(),
        ],
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: _navigateToTab,
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.home_outlined),
            selectedIcon: Icon(Icons.home),
            label: 'Home',
          ),
          NavigationDestination(
            icon: Icon(Icons.directions_bus_outlined),
            selectedIcon: Icon(Icons.directions_bus),
            label: 'Buses',
          ),
          NavigationDestination(
            icon: Icon(Icons.warning_amber_outlined),
            selectedIcon: Icon(Icons.warning_amber),
            label: 'Hazards',
          ),
          NavigationDestination(
            icon: Icon(Icons.add_a_photo_outlined),
            selectedIcon: Icon(Icons.add_a_photo),
            label: 'Report',
          ),
        ],
      ),
    );
  }
}