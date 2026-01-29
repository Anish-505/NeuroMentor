import 'package:uuid/uuid.dart';
import '../models/user_model.dart';
import 'storage_service.dart';

/// Authentication service for local login/register/logout
/// Uses simple password comparison (in production, use bcrypt or similar)
class AuthService {
  static AuthService? _instance;
  final StorageService _storage = StorageService.instance;
  final Uuid _uuid = const Uuid();
  
  AuthService._();
  
  static AuthService get instance {
    _instance ??= AuthService._();
    return _instance!;
  }
  
  /// Register a new user
  /// Returns the created user or null if email already exists
  Future<UserModel?> register({
    required String name,
    required String email,
    required String password,
    String studentId = '',
  }) async {
    // Check if email already exists
    final existingUser = _storage.getUserByEmail(email);
    if (existingUser != null) {
      return null; // Email already registered
    }
    
    // Create new user
    final user = UserModel(
      uid: _uuid.v4(),
      email: email.toLowerCase(),
      name: name,
      studentId: studentId,
      createdAt: DateTime.now(),
      hasCompletedCalibration: false,
    );
    
    // Save user
    await _storage.saveUser(user);
    
    // Store password (in production, hash this!)
    await _storePassword(user.uid, password);
    
    // Set as current user
    await _storage.setCurrentUserId(user.uid);
    
    return user;
  }
  
  /// Login with email and password
  /// Returns the user or null if credentials are invalid
  Future<UserModel?> login({
    required String email,
    required String password,
  }) async {
    // Find user by email
    final user = _storage.getUserByEmail(email);
    if (user == null) {
      return null; // User not found
    }
    
    // Verify password
    final storedPassword = await _getPassword(user.uid);
    if (storedPassword != password) {
      return null; // Wrong password
    }
    
    // Set as current user
    await _storage.setCurrentUserId(user.uid);
    
    return user;
  }
  
  /// Logout current user
  Future<void> logout() async {
    await _storage.setCurrentUserId(null);
  }
  
  /// Check if a user is logged in
  bool isLoggedIn() {
    return _storage.getCurrentUserId() != null;
  }
  
  /// Get current logged-in user
  UserModel? getCurrentUser() {
    return _storage.getCurrentUser();
  }
  
  /// Update user password
  Future<bool> updatePassword({
    required String uid,
    required String currentPassword,
    required String newPassword,
  }) async {
    final storedPassword = await _getPassword(uid);
    if (storedPassword != currentPassword) {
      return false;
    }
    
    await _storePassword(uid, newPassword);
    return true;
  }
  
  // ============================================================
  // PASSWORD STORAGE (Simple implementation - use bcrypt in production)
  // ============================================================
  
  // Note: This stores passwords in plain text for demo purposes.
  // In a production app, use bcrypt or similar hashing.
  
  late final Map<String, String> _passwords = {};
  
  Future<void> _storePassword(String uid, String password) async {
    _passwords[uid] = password;
    // In a real app, you'd store this securely:
    // await FlutterSecureStorage().write(key: 'pw_$uid', value: hashPassword(password));
  }
  
  Future<String?> _getPassword(String uid) async {
    return _passwords[uid];
    // In a real app:
    // return await FlutterSecureStorage().read(key: 'pw_$uid');
  }
}
