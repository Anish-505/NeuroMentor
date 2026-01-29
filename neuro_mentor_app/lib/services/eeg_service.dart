import 'dart:async';
import 'dart:math';

/// EEG Service for ESP32 communication
/// Supports both Bluetooth and WiFi connections
/// Includes mock data generation for testing
class EEGService {
  static EEGService? _instance;
  
  bool _isConnected = false;
  bool _isStreaming = false;
  bool _useMockData = true; // Set to true for testing without hardware
  
  final StreamController<EEGData> _dataController = 
      StreamController<EEGData>.broadcast();
  
  Timer? _mockDataTimer;
  final Random _random = Random();
  
  EEGService._();
  
  static EEGService get instance {
    _instance ??= EEGService._();
    return _instance!;
  }
  
  /// Stream of EEG data
  Stream<EEGData> get dataStream => _dataController.stream;
  
  /// Whether connected to ESP32
  bool get isConnected => _isConnected || _useMockData;
  
  /// Whether currently streaming data
  bool get isStreaming => _isStreaming;
  
  /// Enable/disable mock data mode
  void setMockMode(bool enabled) {
    _useMockData = enabled;
  }
  
  // ============================================================
  // CONNECTION (Placeholder for actual Bluetooth/WiFi implementation)
  // ============================================================
  
  /// Scan for available ESP32 devices
  Future<List<String>> scanDevices() async {
    if (_useMockData) {
      return ['ESP32-NeuroMentor (Mock)'];
    }
    
    // TODO: Implement actual Bluetooth scanning
    // Using flutter_blue_plus:
    // final devices = await FlutterBluePlus.scanResults.first;
    // return devices.map((r) => r.device.name).toList();
    
    await Future.delayed(const Duration(seconds: 2));
    return [];
  }
  
  /// Connect to ESP32 device
  Future<bool> connect(String deviceName) async {
    if (_useMockData) {
      await Future.delayed(const Duration(milliseconds: 500));
      _isConnected = true;
      return true;
    }
    
    // TODO: Implement actual connection
    // Using flutter_blue_plus:
    // final device = devices.firstWhere((d) => d.name == deviceName);
    // await device.connect();
    // _isConnected = true;
    
    return false;
  }
  
  /// Disconnect from ESP32
  Future<void> disconnect() async {
    _isConnected = false;
    await stopStreaming();
    
    // TODO: Implement actual disconnection
  }
  
  // ============================================================
  // STREAMING
  // ============================================================
  
  /// Start streaming EEG data
  Future<void> startStreaming() async {
    if (_isStreaming) return;
    _isStreaming = true;
    
    if (_useMockData) {
      _startMockDataGeneration();
    } else {
      // TODO: Send 'start_live_monitoring' command to ESP32
      // _serialPort.write('start_live_monitoring\n');
    }
  }
  
  /// Stop streaming EEG data
  Future<void> stopStreaming() async {
    _isStreaming = false;
    _mockDataTimer?.cancel();
    
    // TODO: Send 'stop' command to ESP32
  }
  
  /// Start calibration mode
  Future<void> startCalibration() async {
    if (!_useMockData) {
      // TODO: Send 'start_calibration' command to ESP32
    }
    await startStreaming();
  }
  
  // ============================================================
  // MOCK DATA GENERATION
  // ============================================================
  
  void _startMockDataGeneration() {
    _mockDataTimer?.cancel();
    _mockDataTimer = Timer.periodic(const Duration(seconds: 1), (_) {
      if (!_isStreaming) return;
      
      final data = _generateMockEEGData();
      _dataController.add(data);
    });
  }
  
  EEGData _generateMockEEGData() {
    // Generate realistic-looking EEG band powers
    // These values are normalized power levels
    
    // Base values with some variation
    final baseState = _mockCurrentState;
    
    double delta, theta, alpha, beta, gamma;
    
    switch (baseState) {
      case 'Calm':
        // High alpha, low beta
        delta = 30 + _random.nextDouble() * 10;
        theta = 20 + _random.nextDouble() * 8;
        alpha = 35 + _random.nextDouble() * 10;
        beta = 8 + _random.nextDouble() * 4;
        gamma = 2 + _random.nextDouble() * 2;
        break;
      case 'Stressed':
        // High beta, low alpha
        delta = 15 + _random.nextDouble() * 10;
        theta = 10 + _random.nextDouble() * 8;
        alpha = 10 + _random.nextDouble() * 8;
        beta = 45 + _random.nextDouble() * 15;
        gamma = 15 + _random.nextDouble() * 5;
        break;
      case 'Focused':
        // Balanced alpha and beta
        delta = 15 + _random.nextDouble() * 8;
        theta = 10 + _random.nextDouble() * 5;
        alpha = 30 + _random.nextDouble() * 10;
        beta = 35 + _random.nextDouble() * 10;
        gamma = 8 + _random.nextDouble() * 4;
        break;
      default:
        // Random/transition state
        delta = 20 + _random.nextDouble() * 15;
        theta = 15 + _random.nextDouble() * 10;
        alpha = 20 + _random.nextDouble() * 15;
        beta = 25 + _random.nextDouble() * 15;
        gamma = 5 + _random.nextDouble() * 5;
    }
    
    return EEGData(
      timestamp: DateTime.now(),
      delta: delta,
      theta: theta,
      alpha: alpha,
      beta: beta,
      gamma: gamma,
      state: baseState,
    );
  }
  
  // Simulate changing mental states for demo
  String _mockCurrentState = 'Calm';
  int _mockStateCounter = 0;
  
  /// Change mock state (for testing)
  void setMockState(String state) {
    _mockCurrentState = state;
  }
  
  // ============================================================
  // DATA PARSING (For real ESP32 data)
  // ============================================================
  
  /// Parse raw serial data from ESP32
  /// Expected format: "Live,Delta,Theta,Alpha,Beta,Gamma"
  EEGData? parseSerialData(String line) {
    try {
      if (!line.startsWith('Live')) return null;
      
      final parts = line.split(',');
      if (parts.length != 6) return null;
      
      return EEGData(
        timestamp: DateTime.now(),
        delta: double.parse(parts[1]),
        theta: double.parse(parts[2]),
        alpha: double.parse(parts[3]),
        beta: double.parse(parts[4]),
        gamma: double.parse(parts[5]),
        state: 'Live',
      );
    } catch (e) {
      return null;
    }
  }
  
  /// Clean up resources
  void dispose() {
    _mockDataTimer?.cancel();
    _dataController.close();
  }
}

/// EEG data point from ESP32
class EEGData {
  final DateTime timestamp;
  final double delta;
  final double theta;
  final double alpha;
  final double beta;
  final double gamma;
  final String state;
  
  EEGData({
    required this.timestamp,
    required this.delta,
    required this.theta,
    required this.alpha,
    required this.beta,
    required this.gamma,
    required this.state,
  });
  
  /// Convert to band power map for algorithm processing
  Map<String, double> toBandPowerMap() {
    return {
      'delta': delta,
      'theta': theta,
      'alpha': alpha,
      'beta': beta,
      'gamma': gamma,
    };
  }
  
  @override
  String toString() {
    return 'EEGData(δ:${delta.toStringAsFixed(1)}, θ:${theta.toStringAsFixed(1)}, '
           'α:${alpha.toStringAsFixed(1)}, β:${beta.toStringAsFixed(1)}, '
           'γ:${gamma.toStringAsFixed(1)})';
  }
}
