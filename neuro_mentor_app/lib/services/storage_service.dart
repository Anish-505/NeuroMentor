import 'dart:convert';
import 'package:hive_flutter/hive_flutter.dart';
import '../models/user_model.dart';
import '../models/calibration_data.dart';
import '../models/attention_session.dart';

/// Local storage service using Hive
/// Stores user data, calibration, and session history
class StorageService {
  static const String _usersBoxName = 'users';
  static const String _sessionsBoxName = 'sessions';
  static const String _metaBoxName = 'meta';
  
  static StorageService? _instance;
  late Box<String> _usersBox;
  late Box<String> _sessionsBox;
  late Box<String> _metaBox;
  
  StorageService._();
  
  static StorageService get instance {
    _instance ??= StorageService._();
    return _instance!;
  }
  
  /// Initialize Hive and open boxes
  Future<void> init() async {
    await Hive.initFlutter();
    _usersBox = await Hive.openBox<String>(_usersBoxName);
    _sessionsBox = await Hive.openBox<String>(_sessionsBoxName);
    _metaBox = await Hive.openBox<String>(_metaBoxName);
  }
  
  // ============================================================
  // USER OPERATIONS
  // ============================================================
  
  /// Save user data
  Future<void> saveUser(UserModel user) async {
    await _usersBox.put(user.uid, jsonEncode(user.toJson()));
  }
  
  /// Get user by UID
  UserModel? getUser(String uid) {
    final data = _usersBox.get(uid);
    if (data == null) return null;
    return UserModel.fromJson(jsonDecode(data) as Map<String, dynamic>);
  }
  
  /// Get user by email
  UserModel? getUserByEmail(String email) {
    for (final key in _usersBox.keys) {
      final data = _usersBox.get(key);
      if (data != null) {
        final user = UserModel.fromJson(jsonDecode(data) as Map<String, dynamic>);
        if (user.email.toLowerCase() == email.toLowerCase()) {
          return user;
        }
      }
    }
    return null;
  }
  
  /// Delete user
  Future<void> deleteUser(String uid) async {
    await _usersBox.delete(uid);
  }
  
  /// Get all users (for debugging)
  List<UserModel> getAllUsers() {
    return _usersBox.values
        .map((data) => UserModel.fromJson(jsonDecode(data) as Map<String, dynamic>))
        .toList();
  }
  
  // ============================================================
  // CALIBRATION OPERATIONS
  // ============================================================
  
  /// Update user's calibration data
  Future<void> updateCalibration(String uid, CalibrationData calibration) async {
    final user = getUser(uid);
    if (user == null) return;
    
    final updatedUser = user.copyWith(
      calibrationBaseline: calibration,
      hasCompletedCalibration: true,
    );
    await saveUser(updatedUser);
  }
  
  /// Get user's calibration data (or default)
  CalibrationData getCalibrationData(String uid) {
    final user = getUser(uid);
    if (user?.calibrationBaseline != null) {
      return user!.calibrationBaseline!;
    }
    return CalibrationData.defaultSample();
  }
  
  // ============================================================
  // SESSION OPERATIONS
  // ============================================================
  
  /// Save an attention session
  Future<void> saveSession(AttentionSession session) async {
    await _sessionsBox.put(session.sessionId, jsonEncode(session.toJson()));
  }
  
  /// Get session by ID
  AttentionSession? getSession(String sessionId) {
    final data = _sessionsBox.get(sessionId);
    if (data == null) return null;
    return AttentionSession.fromJson(jsonDecode(data) as Map<String, dynamic>);
  }
  
  /// Get all sessions for a user
  List<AttentionSession> getUserSessions(String userId) {
    final sessions = <AttentionSession>[];
    for (final key in _sessionsBox.keys) {
      final data = _sessionsBox.get(key);
      if (data != null) {
        final session = AttentionSession.fromJson(
          jsonDecode(data) as Map<String, dynamic>,
        );
        if (session.userId == userId) {
          sessions.add(session);
        }
      }
    }
    sessions.sort((a, b) => b.startTime.compareTo(a.startTime));
    return sessions;
  }
  
  /// Delete a session
  Future<void> deleteSession(String sessionId) async {
    await _sessionsBox.delete(sessionId);
  }
  
  // ============================================================
  // SESSION MANAGEMENT (LOGIN STATE)
  // ============================================================
  
  /// Save current logged-in user
  Future<void> setCurrentUserId(String? uid) async {
    if (uid == null) {
      await _metaBox.delete('currentUserId');
    } else {
      await _metaBox.put('currentUserId', uid);
    }
  }
  
  /// Get current logged-in user ID
  String? getCurrentUserId() {
    return _metaBox.get('currentUserId');
  }
  
  /// Get current logged-in user
  UserModel? getCurrentUser() {
    final uid = getCurrentUserId();
    if (uid == null) return null;
    return getUser(uid);
  }
  
  /// Clear all data (for development/testing)
  Future<void> clearAll() async {
    await _usersBox.clear();
    await _sessionsBox.clear();
    await _metaBox.clear();
  }
}
