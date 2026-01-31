import 'package:flutter/material.dart';

/// App theme with dark gradient glassmorphism design
class AppTheme {
  // Gradient colors
  static const primaryStart = Color(0xFF8B5CF6);
  static const primaryEnd = Color(0xFFEC4899);
  static const secondaryStart = Color(0xFF3B82F6);
  static const secondaryEnd = Color(0xFF06B6D4);
  static const accentStart = Color(0xFF10B981);
  static const accentEnd = Color(0xFF059669);

  // Background colors
  static const bgDark = Color(0xFF0F172A);
  static const bgMid = Color(0xFF1E1B4B);

  // Gradients
  static const backgroundGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [bgDark, bgMid, Color(0xFF312E81)],
  );

  static const primaryGradient = LinearGradient(
    colors: [primaryStart, primaryEnd],
  );

  static const secondaryGradient = LinearGradient(
    colors: [secondaryStart, secondaryEnd],
  );

  static const accentGradient = LinearGradient(
    colors: [accentStart, accentEnd],
  );

  // Theme data
  static ThemeData get darkTheme => ThemeData(
    brightness: Brightness.dark,
    scaffoldBackgroundColor: bgDark,
    primaryColor: primaryStart,
    colorScheme: const ColorScheme.dark(
      primary: primaryStart,
      secondary: secondaryStart,
    ),
    fontFamily: 'Roboto',
    textTheme: const TextTheme(
      headlineLarge: TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: Colors.white),
      headlineMedium: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.white),
      bodyLarge: TextStyle(fontSize: 16, color: Colors.white70),
      bodyMedium: TextStyle(fontSize: 14, color: Colors.white60),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: Colors.white.withOpacity(0.1),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(16),
        borderSide: BorderSide.none,
      ),
      contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      ),
    ),
  );
}

/// Glass card decoration
BoxDecoration glassDecoration({double opacity = 0.1}) => BoxDecoration(
  color: Colors.white.withOpacity(opacity),
  borderRadius: BorderRadius.circular(24),
  border: Border.all(color: Colors.white.withOpacity(0.2)),
);
