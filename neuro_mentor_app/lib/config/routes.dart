import 'package:flutter/material.dart';
import '../screens/auth/landing_screen.dart';
import '../screens/auth/login_screen.dart';
import '../screens/auth/register_screen.dart';
import '../screens/dashboard_screen.dart';
import '../screens/calibration/calibration_home_screen.dart';
import '../screens/calibration/calibration_session_screen.dart';
import '../screens/monitoring/live_monitoring_screen.dart';

/// Route names for the app
class Routes {
  static const String landing = '/';
  static const String login = '/login';
  static const String register = '/register';
  static const String dashboard = '/dashboard';
  static const String calibration = '/calibration';
  static const String calibrationSession = '/calibration/session';
  static const String monitoring = '/monitoring';
  
  /// Generate routes for the app
  static Route<dynamic> generateRoute(RouteSettings settings) {
    switch (settings.name) {
      case landing:
        return _buildRoute(const LandingScreen(), settings);
      case login:
        return _buildRoute(const LoginScreen(), settings);
      case register:
        return _buildRoute(const RegisterScreen(), settings);
      case dashboard:
        return _buildRoute(const DashboardScreen(), settings);
      case calibration:
        return _buildRoute(const CalibrationHomeScreen(), settings);
      case calibrationSession:
        final stateName = settings.arguments as String? ?? 'Calm';
        return _buildRoute(
          CalibrationSessionScreen(stateName: stateName),
          settings,
        );
      case monitoring:
        return _buildRoute(const LiveMonitoringScreen(), settings);
      default:
        return _buildRoute(
          Scaffold(
            body: Center(
              child: Text('Route ${settings.name} not found'),
            ),
          ),
          settings,
        );
    }
  }
  
  /// Build a route with a fade transition
  static PageRoute _buildRoute(Widget page, RouteSettings settings) {
    return PageRouteBuilder(
      settings: settings,
      pageBuilder: (context, animation, secondaryAnimation) => page,
      transitionsBuilder: (context, animation, secondaryAnimation, child) {
        return FadeTransition(
          opacity: animation,
          child: child,
        );
      },
      transitionDuration: const Duration(milliseconds: 300),
    );
  }
}

