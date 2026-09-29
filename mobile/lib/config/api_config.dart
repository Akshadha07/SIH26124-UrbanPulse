class ApiConfig {
  // Default for Chrome / local desktop testing
  static String baseUrl = 'http://localhost:8000/api/v1';
  static String wsUrl = 'ws://localhost:8000/ws/live';

  // Toggle for local host or physical device with LAN IP
  static void setCustomHost(String host, {int port = 8000}) {
    baseUrl = 'http://' + host + ':' + port.toString() + '/api/v1';
    wsUrl = 'ws://' + host + ':' + port.toString() + '/ws/live';
  }

  static void useLocalhost() {
    baseUrl = 'http://localhost:8000/api/v1';
    wsUrl = 'ws://localhost:8000/ws/live';
  }

  static void useAndroidEmulator() {
    baseUrl = 'http://10.0.2.2:8000/api/v1';
    wsUrl = 'ws://10.0.2.2:8000/ws/live';
  }

  // Vadodara City Baseline Coordinates
  static const double defaultLat = 22.3072;
  static const double defaultLon = 73.1812;
  static const String cityName = 'Vadodara, Gujarat';
}