import 'package:flutter/material.dart';

/// NeuroMentor App Theme - Dark Glassmorphism Design
/// Matching the PyQt5 original design aesthetic

class AppTheme {
  // Core colors
  static const Color background = Color(0xFF05070a);
  static const Color glassCard = Color(0x1A0f141e); // rgba(15, 20, 30, 0.8)
  static const Color glassBorder = Color(0x14FFFFFF); // rgba(255, 255, 255, 0.08)
  static const Color textPrimary = Color(0xFFf1f5f9);
  static const Color textSecondary = Color(0xFFcbd5e1);
  static const Color textMuted = Color(0xFF64748b);
  
  // State colors
  static const Color calmColor = Color(0xFF2563eb);
  static const Color stressedColor = Color(0xFFea0c0c);
  static const Color focusedColor = Color(0xFF16a34a);

  static Color getStateColor(String stateName) {
    switch (stateName) {
      case 'Calm':
        return calmColor;
      case 'Stressed':
        return stressedColor;
      case 'Focused':
        return focusedColor;
      default:
        return calmColor;
    }
  }

  static ThemeData get darkTheme {
    return ThemeData(
      brightness: Brightness.dark,
      scaffoldBackgroundColor: background,
      fontFamily: 'Inter',
      colorScheme: const ColorScheme.dark(
        primary: calmColor,
        secondary: textSecondary,
        surface: glassCard,
        onPrimary: Colors.white,
        onSecondary: Colors.white,
        onSurface: textPrimary,
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: Colors.transparent,
        elevation: 0,
        centerTitle: true,
        titleTextStyle: TextStyle(
          color: textPrimary,
          fontSize: 20,
          fontWeight: FontWeight.w800,
          letterSpacing: 2,
        ),
      ),
      cardTheme: CardTheme(
        color: glassCard,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(24),
          side: const BorderSide(color: glassBorder, width: 1),
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: const Color(0x0AFFFFFF),
          foregroundColor: Colors.white,
          elevation: 0,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: const BorderSide(color: Color(0x1FFFFFFF), width: 1),
          ),
          textStyle: const TextStyle(
            fontWeight: FontWeight.w800,
            letterSpacing: 1.5,
            fontSize: 14,
          ),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: const Color(0x80000000),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: Color(0x1AFFFFFF)),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: Color(0x1AFFFFFF)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: calmColor, width: 2),
        ),
        hintStyle: const TextStyle(color: textMuted),
      ),
      progressIndicatorTheme: const ProgressIndicatorThemeData(
        linearTrackColor: Color(0x08FFFFFF),
      ),
      textTheme: const TextTheme(
        displayLarge: TextStyle(
          fontSize: 44,
          fontWeight: FontWeight.w900,
          letterSpacing: 3,
          color: textPrimary,
        ),
        displayMedium: TextStyle(
          fontSize: 85,
          fontWeight: FontWeight.w900,
          fontFamily: 'monospace',
          color: textPrimary,
        ),
        headlineSmall: TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.w800,
          letterSpacing: 1,
          color: textMuted,
        ),
        bodyLarge: TextStyle(
          fontSize: 16,
          color: textSecondary,
        ),
        bodyMedium: TextStyle(
          fontSize: 14,
          color: textSecondary,
        ),
        labelLarge: TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.w800,
          letterSpacing: 1.5,
          color: Colors.white,
        ),
      ),
    );
  }
}

/// Glass card container widget for the glassmorphism effect
class GlassCard extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry? padding;
  final Color? glowColor;

  const GlassCard({
    super.key,
    required this.child,
    this.padding,
    this.glowColor,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xCC0f141e),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: AppTheme.glassBorder, width: 1),
        boxShadow: glowColor != null
            ? [
                BoxShadow(
                  color: glowColor!.withOpacity(0.3),
                  blurRadius: 40,
                  spreadRadius: 0,
                )
              ]
            : null,
      ),
      padding: padding ?? const EdgeInsets.all(40),
      child: child,
    );
  }
}

/// Timer display widget with glow effect
class TimerDisplay extends StatelessWidget {
  final String time;
  final Color glowColor;

  const TimerDisplay({
    super.key,
    required this.time,
    required this.glowColor,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 24, horizontal: 32),
      decoration: BoxDecoration(
        color: const Color(0x66000000),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0x08FFFFFF)),
        boxShadow: [
          BoxShadow(
            color: glowColor.withOpacity(0.4),
            blurRadius: 40,
            spreadRadius: 0,
          ),
        ],
      ),
      child: Text(
        time,
        style: TextStyle(
          fontSize: 72,
          fontWeight: FontWeight.w900,
          fontFamily: 'monospace',
          color: Colors.white,
          shadows: [
            Shadow(
              color: glowColor.withOpacity(0.5),
              blurRadius: 20,
            ),
          ],
        ),
      ),
    );
  }
}
