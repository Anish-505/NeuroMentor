import 'package:flutter/foundation.dart';
import '../models/calibration_data.dart';
import '../models/attention_session.dart';
import '../services/storage_service.dart';

/// User data provider
/// Manages calibration data and session history
class UserDataProvider extends ChangeNotifier {
  final StorageService _storageService = StorageService.instance;
  
  CalibrationData? _calibrationData;
  List<AttentionSession> _sessions = [];
  bool _isLoading = false;
  
  CalibrationData? get calibrationData => _calibrationData;
  List<AttentionSession> get sessions => _sessions;
  bool get isLoading => _isLoading;
  
  /// Whether user has personalized calibration
  bool get hasPersonalCalibration => 
      _calibrationData?.isPersonalized ?? false;
  
  /// Load user's calibration data
  Future<void> loadCalibrationData(String userId) async {
    _isLoading = true;
    notifyListeners();
    
    _calibrationData = _storageService.getCalibrationData(userId);
    
    _isLoading = false;
    notifyListeners();
  }
  
  /// Get calibration data (or default if not available)
  CalibrationData getActiveCalibration(String userId) {
    if (_calibrationData != null) {
      return _calibrationData!;
    }
    return _storageService.getCalibrationData(userId);
  }
  
  /// Save new calibration data
  Future<void> saveCalibration(String userId, CalibrationData data) async {
    _isLoading = true;
    notifyListeners();
    
    await _storageService.updateCalibration(userId, data);
    _calibrationData = data;
    
    _isLoading = false;
    notifyListeners();
  }
  
  /// Load user's session history
  Future<void> loadSessions(String userId) async {
    _isLoading = true;
    notifyListeners();
    
    _sessions = _storageService.getUserSessions(userId);
    
    _isLoading = false;
    notifyListeners();
  }
  
  /// Save a new session
  Future<void> saveSession(AttentionSession session) async {
    await _storageService.saveSession(session);
    _sessions.insert(0, session);
    notifyListeners();
  }
  
  /// Clear user data (on logout)
  void clearData() {
    _calibrationData = null;
    _sessions = [];
    notifyListeners();
  }
  
  /// Switch between personal and default calibration
  void useDefaultCalibration() {
    _calibrationData = CalibrationData.defaultSample();
    notifyListeners();
  }
}
