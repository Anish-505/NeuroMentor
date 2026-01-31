import 'package:flutter/material.dart';
import '../screens/landing_screen.dart';
import '../screens/login_screen.dart';
import '../screens/register_screen.dart';
import '../screens/dashboard_screen.dart';
import '../screens/calibration_screen.dart';
import '../screens/monitoring_screen.dart';

/// App routes
class Routes {
  static const landing = '/';
  static const login = '/login';
  static const register = '/register';
  static const dashboard = '/dashboard';
  static const calibration = '/calibration';
  static const monitoring = '/monitoring';

  static Route<dynamic> generate(RouteSettings settings) {
    switch (settings.name) {
      case landing:
        return _fade(const LandingScreen());
      case login:
        return _fade(const LoginScreen());
      case register:
        return _fade(const RegisterScreen());
      case dashboard:
        return _fade(const DashboardScreen());
      case calibration:
        return _fade(CalibrationScreen(state: settings.arguments as String? ?? 'Calm'));
      case monitoring:
        return _fade(const MonitoringScreen());
      default:
        return _fade(const LandingScreen());
    }
  }

  static PageRoute _fade(Widget page) => PageRouteBuilder(
    pageBuilder: (_, __, ___) => page,
    transitionsBuilder: (_, a, __, child) => FadeTransition(opacity: a, child: child),
    transitionDuration: const Duration(milliseconds: 200),
  );
}
