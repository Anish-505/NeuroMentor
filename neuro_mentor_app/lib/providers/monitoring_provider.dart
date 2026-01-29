import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:uuid/uuid.dart';
import '../models/calibration_data.dart';
import '../models/attention_session.dart';
import '../services/eeg_service.dart';
import '../utils/attention_algorithms.dart';

/// Live monitoring state provider
/// Manages EEG data stream, calculations, and session recording
class MonitoringProvider extends ChangeNotifier {
  final EEGService _eegService = EEGService.instance;
  final Uuid _uuid = const Uuid();
  
  // Session state
  AttentionSession? _currentSession;
  bool _isMonitoring = false;
  Duration _sessionDuration = Duration.zero;
  Timer? _durationTimer;
  
  // Current readings
  MentalState _currentState = MentalState.calm;
  double _currentFocusLevel = 0.5;
  double _currentStressLevel = 0.2;
  Map<String, double> _currentBandPowers = {};
  
  // Historical data for graphs (last 60 seconds)
  final List<double> _focusHistory = [];
  final List<double> _stressHistory = [];
  final List<Map<String, double>> _bandPowerHistory = [];
  static const int _historySize = 60;
  
  // Calibration reference
  CalibrationData? _calibrationData;
  
  // EEG data subscription
  StreamSubscription<EEGData>? _eegSubscription;
  
  // Getters
  bool get isMonitoring => _isMonitoring;
  AttentionSession? get currentSession => _currentSession;
  Duration get sessionDuration => _sessionDuration;
  MentalState get currentState => _currentState;
  double get currentFocusLevel => _currentFocusLevel;
  double get currentStressLevel => _currentStressLevel;
  Map<String, double> get currentBandPowers => _currentBandPowers;
  List<double> get focusHistory => List.unmodifiable(_focusHistory);
  List<double> get stressHistory => List.unmodifiable(_stressHistory);
  bool get isUsingPersonalCalibration => _calibrationData?.isPersonalized ?? false;
  String get calibrationSource => _calibrationData?.datasetSource ?? 'default';
  
  // Computed ratios
  double get focusIndex => 
      AttentionAlgorithms.calculateFocusIndex(_currentBandPowers);
  double get stressIndex => 
      AttentionAlgorithms.calculateStressIndex(_currentBandPowers);
  double get relaxationIndex => 
      AttentionAlgorithms.calculateRelaxationIndex(_currentBandPowers);
  
  /// Set calibration data to use for comparisons
  void setCalibrationData(CalibrationData data) {
    _calibrationData = data;
    notifyListeners();
  }
  
  /// Start monitoring session
  Future<void> startMonitoring(String userId) async {
    if (_isMonitoring) return;
    
    // Ensure we have calibration data
    _calibrationData ??= CalibrationData.defaultSample();
    
    // Create new session
    _currentSession = AttentionSession(
      sessionId: _uuid.v4(),
      userId: userId,
      startTime: DateTime.now(),
    );
    
    // Clear history
    _focusHistory.clear();
    _stressHistory.clear();
    _bandPowerHistory.clear();
    _sessionDuration = Duration.zero;
    
    // Start EEG streaming
    await _eegService.startStreaming();
    
    // Subscribe to EEG data
    _eegSubscription = _eegService.dataStream.listen(_onEEGData);
    
    // Start duration timer
    _durationTimer = Timer.periodic(const Duration(seconds: 1), (_) {
      _sessionDuration += const Duration(seconds: 1);
      notifyListeners();
    });
    
    _isMonitoring = true;
    notifyListeners();
  }
  
  /// Stop monitoring session
  Future<AttentionSession?> stopMonitoring() async {
    if (!_isMonitoring) return null;
    
    _isMonitoring = false;
    
    // Stop timers and subscriptions
    _durationTimer?.cancel();
    await _eegSubscription?.cancel();
    await _eegService.stopStreaming();
    
    // Finalize session
    _currentSession?.endSession();
    final session = _currentSession;
    
    notifyListeners();
    return session;
  }
  
  /// Handle incoming EEG data
  void _onEEGData(EEGData data) {
    if (!_isMonitoring || _calibrationData == null) return;
    
    // Update current band powers
    _currentBandPowers = data.toBandPowerMap();
    
    // Calculate attention metrics
    final dataPoint = AttentionAlgorithms.createDataPoint(
      liveBandPowers: _currentBandPowers,
      baseline: _calibrationData!,
    );
    
    // Update current state
    _currentState = dataPoint.state;
    _currentFocusLevel = dataPoint.focusLevel;
    _currentStressLevel = dataPoint.stressLevel;
    
    // Add to session
    _currentSession?.addDataPoint(dataPoint);
    
    // Add to history (keep last 60 seconds)
    _focusHistory.add(_currentFocusLevel);
    _stressHistory.add(_currentStressLevel);
    _bandPowerHistory.add(Map.from(_currentBandPowers));
    
    if (_focusHistory.length > _historySize) {
      _focusHistory.removeAt(0);
      _stressHistory.removeAt(0);
      _bandPowerHistory.removeAt(0);
    }
    
    notifyListeners();
  }
  
  /// Get session statistics
  Map<String, dynamic> getSessionStats() {
    if (_currentSession == null) {
      return {
        'totalFocusedTime': Duration.zero,
        'totalUnfocusedTime': Duration.zero,
        'averageFocusLevel': 0.0,
        'peakStressMoments': 0,
      };
    }
    
    return {
      'totalFocusedTime': _currentSession!.totalFocusedTime,
      'totalUnfocusedTime': _currentSession!.totalUnfocusedTime,
      'averageFocusLevel': _currentSession!.averageFocusLevel,
      'peakStressMoments': _currentSession!.peakStressMoments,
    };
  }
  
  /// Change mock EEG state (for testing)
  void setMockState(String state) {
    _eegService.setMockState(state);
  }
  
  /// Clean up
  @override
  void dispose() {
    _durationTimer?.cancel();
    _eegSubscription?.cancel();
    super.dispose();
  }
}
