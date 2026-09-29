import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../config/api_config.dart';
import '../models/ws_event.dart';

class WebSocketService {
  static final WebSocketService _instance = WebSocketService._internal();
  factory WebSocketService() => _instance;
  WebSocketService._internal();

  WebSocketChannel? _channel;
  final StreamController<WsEnvelope> _eventController =
      StreamController<WsEnvelope>.broadcast();
  Stream<WsEnvelope> get stream => _eventController.stream;

  bool _isConnected = false;
  bool get isConnected => _isConnected;

  Timer? _reconnectTimer;
  Timer? _pingTimer;

  void connect() {
    if (_isConnected || _channel != null) return;

    try {
      final uri = Uri.parse(ApiConfig.wsUrl);
      _channel = WebSocketChannel.connect(uri);

      _channel!.stream.listen(
        (message) {
          _isConnected = true;
          if (message == 'pong') return;

          try {
            final Map<String, dynamic> data = jsonDecode(message);
            final envelope = WsEnvelope.fromJson(data);
            _eventController.add(envelope);
          } catch (_) {
            // Ignore malformed messages
          }
        },
        onDone: () {
          _handleDisconnect();
        },
        onError: (error) {
          _handleDisconnect();
        },
        cancelOnError: true,
      );

      _isConnected = true;
      _startPing();
    } catch (_) {
      _handleDisconnect();
    }
  }

  void _startPing() {
    _pingTimer?.cancel();
    _pingTimer = Timer.periodic(const Duration(seconds: 15), (_) {
      if (_isConnected && _channel != null) {
        try {
          _channel!.sink.add('ping');
        } catch (_) {
          _handleDisconnect();
        }
      }
    });
  }

  void _handleDisconnect() {
    _isConnected = false;
    _pingTimer?.cancel();
    _channel = null;

    _reconnectTimer?.cancel();
    _reconnectTimer = Timer(const Duration(seconds: 5), () {
      connect();
    });
  }

  void disconnect() {
    _pingTimer?.cancel();
    _reconnectTimer?.cancel();
    _channel?.sink.close();
    _channel = null;
    _isConnected = false;
  }
}
