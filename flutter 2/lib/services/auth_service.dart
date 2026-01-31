import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user.dart';

/// Simple auth service using SharedPreferences
class AuthService {
  static const _usersKey = 'users';
  static const _currentUserKey = 'currentUser';

  /// Register new user
  static Future<User?> register(String name, String email, String password) async {
    final prefs = await SharedPreferences.getInstance();
    final users = _getUsers(prefs);
    
    // Check if email exists
    if (users.any((u) => u['email'] == email)) {
      return null; // Email already exists
    }

    final user = User(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      email: email,
      name: name,
      createdAt: DateTime.now(),
    );

    users.add({...user.toJson(), 'password': password});
    await prefs.setString(_usersKey, jsonEncode(users));
    await prefs.setString(_currentUserKey, jsonEncode(user.toJson()));
    
    return user;
  }

  /// Login user
  static Future<User?> login(String email, String password) async {
    final prefs = await SharedPreferences.getInstance();
    final users = _getUsers(prefs);
    
    final match = users.where((u) => u['email'] == email && u['password'] == password);
    if (match.isEmpty) return null;

    final userData = match.first;
    final user = User.fromJson(userData);
    await prefs.setString(_currentUserKey, jsonEncode(user.toJson()));
    
    return user;
  }

  /// Get current logged in user
  static Future<User?> getCurrentUser() async {
    final prefs = await SharedPreferences.getInstance();
    final data = prefs.getString(_currentUserKey);
    if (data == null) return null;
    return User.fromJson(jsonDecode(data));
  }

  /// Logout
  static Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_currentUserKey);
  }

  static List<Map<String, dynamic>> _getUsers(SharedPreferences prefs) {
    final data = prefs.getString(_usersKey);
    if (data == null) return [];
    return List<Map<String, dynamic>>.from(jsonDecode(data));
  }
}
