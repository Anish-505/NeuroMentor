import 'package:flutter/material.dart';
import '../models/user.dart';
import '../services/auth_service.dart';

/// Auth state provider
class AuthProvider extends ChangeNotifier {
  User? _user;
  bool _loading = false;
  String? _error;

  User? get user => _user;
  bool get isLoggedIn => _user != null;
  bool get loading => _loading;
  String? get error => _error;

  /// Check for existing session
  Future<void> checkSession() async {
    _loading = true;
    notifyListeners();
    
    _user = await AuthService.getCurrentUser();
    _loading = false;
    notifyListeners();
  }

  /// Register new user
  Future<bool> register(String name, String email, String password) async {
    _loading = true;
    _error = null;
    notifyListeners();

    final user = await AuthService.register(name, email, password);
    _loading = false;
    
    if (user == null) {
      _error = 'Email already exists';
      notifyListeners();
      return false;
    }
    
    _user = user;
    notifyListeners();
    return true;
  }

  /// Login user
  Future<bool> login(String email, String password) async {
    _loading = true;
    _error = null;
    notifyListeners();

    final user = await AuthService.login(email, password);
    _loading = false;
    
    if (user == null) {
      _error = 'Invalid email or password';
      notifyListeners();
      return false;
    }
    
    _user = user;
    notifyListeners();
    return true;
  }

  /// Logout
  Future<void> logout() async {
    await AuthService.logout();
    _user = null;
    notifyListeners();
  }
}
