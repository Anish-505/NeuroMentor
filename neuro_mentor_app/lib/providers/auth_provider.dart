import 'package:flutter/foundation.dart';
import '../models/user_model.dart';
import '../services/auth_service.dart';
import '../services/storage_service.dart';

/// Authentication state provider
/// Manages login, logout, register, and session persistence
class AuthProvider extends ChangeNotifier {
  final AuthService _authService = AuthService.instance;
  final StorageService _storageService = StorageService.instance;
  
  bool _isLoading = false;
  bool _isLoggedIn = false;
  UserModel? _currentUser;
  String? _errorMessage;
  
  /// Loading state
  bool get isLoading => _isLoading;
  
  /// Whether user is logged in
  bool get isLoggedIn => _isLoggedIn;
  
  /// Currently logged in user
  UserModel? get currentUser => _currentUser;
  
  /// Error message from last operation
  String? get errorMessage => _errorMessage;
  
  /// Check if user session exists on app start
  Future<void> checkSession() async {
    _isLoading = true;
    notifyListeners();
    
    _currentUser = _authService.getCurrentUser();
    _isLoggedIn = _currentUser != null;
    
    _isLoading = false;
    notifyListeners();
  }
  
  /// Login with email and password
  Future<bool> login(String email, String password) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();
    
    try {
      final user = await _authService.login(
        email: email,
        password: password,
      );
      
      if (user != null) {
        _currentUser = user;
        _isLoggedIn = true;
        _isLoading = false;
        notifyListeners();
        return true;
      } else {
        _errorMessage = 'Invalid email or password';
        _isLoading = false;
        notifyListeners();
        return false;
      }
    } catch (e) {
      _errorMessage = 'An error occurred. Please try again.';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }
  
  /// Register a new user
  Future<bool> register({
    required String name,
    required String email,
    required String password,
    String studentId = '',
  }) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();
    
    try {
      final user = await _authService.register(
        name: name,
        email: email,
        password: password,
        studentId: studentId,
      );
      
      if (user != null) {
        _currentUser = user;
        _isLoggedIn = true;
        _isLoading = false;
        notifyListeners();
        return true;
      } else {
        _errorMessage = 'Email already registered';
        _isLoading = false;
        notifyListeners();
        return false;
      }
    } catch (e) {
      _errorMessage = 'An error occurred. Please try again.';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }
  
  /// Logout current user
  Future<void> logout() async {
    _isLoading = true;
    notifyListeners();
    
    await _authService.logout();
    
    _currentUser = null;
    _isLoggedIn = false;
    _isLoading = false;
    notifyListeners();
  }
  
  /// Clear error message
  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }
  
  /// Refresh current user data
  Future<void> refreshUser() async {
    if (_currentUser == null) return;
    
    final updatedUser = _storageService.getUser(_currentUser!.uid);
    if (updatedUser != null) {
      _currentUser = updatedUser;
      notifyListeners();
    }
  }
}
