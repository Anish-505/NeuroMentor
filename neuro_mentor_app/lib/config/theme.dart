import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// NeuroMentor App Theme
/// Dark glassmorphism design with vibrant gradients

class AppTheme {
  // ============================================================
  // COLOR PALETTE
  // ============================================================
  
  // Background colors
  static const Color backgroundDark = Color(0xFF0F172A);
  static const Color backgroundMid = Color(0xFF1E1B4B);
  static const Color backgroundLight = Color(0xFF312E81);
  
  // Surface colors (for cards)
  static const Color surfaceColor = Color(0x140F141E); // rgba(15, 20, 30, 0.08)
  static const Color cardBackground = Color(0xCC0F141E); // rgba(15, 20, 30, 0.8)
  static const Color cardBorder = Color(0x14FFFFFF); // rgba(255, 255, 255, 0.08)
  
  // Primary gradient (Purple to Pink)
  static const Color primaryStart = Color(0xFF8B5CF6);
  static const Color primaryEnd = Color(0xFFEC4899);
  
  // Secondary gradient (Blue to Cyan)
  static const Color secondaryStart = Color(0xFF3B82F6);
  static const Color secondaryEnd = Color(0xFF06B6D4);
  
  // Accent gradient (Green to Emerald)
  static const Color accentStart = Color(0xFF10B981);
  static const Color accentEnd = Color(0xFF059669);
  
  // State colors
  static const Color calmColor = Color(0xFF2563EB);
  static const Color stressedColor = Color(0xFFEA0C0C);
  static const Color focusedColor = Color(0xFF16A34A);
  static const Color unfocusedColor = Color(0xFFF59E0B);
  
  // Text colors
  static const Color textPrimary = Color(0xFFF1F5F9);
  static const Color textSecondary = Color(0xFFCBD5E1);
  static const Color textMuted = Color(0xFF64748B);
  static const Color textDark = Color(0xFF475569);
  
  // ============================================================
  // GRADIENTS
  // ============================================================
  
  static const LinearGradient backgroundGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [backgroundDark, backgroundMid, backgroundLight],
    stops: [0.0, 0.5, 1.0],
  );
  
  static const LinearGradient primaryGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [primaryStart, primaryEnd],
  );
  
  static const LinearGradient secondaryGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [secondaryStart, secondaryEnd],
  );
  
  static const LinearGradient accentGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [accentStart, accentEnd],
  );
  
  // ============================================================
  // BORDER RADIUS
  // ============================================================
  
  static const double radiusSmall = 12.0;
  static const double radiusMedium = 16.0;
  static const double radiusLarge = 20.0;
  static const double radiusXL = 24.0;
  static const double radiusXXL = 32.0;
  
  // ============================================================
  // SHADOWS & EFFECTS
  // ============================================================
  
  static List<BoxShadow> glowShadow(Color color, {double blur = 20}) {
    return [
      BoxShadow(
        color: color.withAlpha(100),
        blurRadius: blur,
        spreadRadius: 0,
      ),
    ];
  }
  
  static BoxDecoration glassDecoration({
    double borderRadius = 24.0,
    Color? glowColor,
  }) {
    return BoxDecoration(
      color: cardBackground,
      borderRadius: BorderRadius.circular(borderRadius),
      border: Border.all(color: cardBorder, width: 1),
      boxShadow: glowColor != null ? glowShadow(glowColor) : null,
    );
  }
  
  // ============================================================
  // TEXT STYLES
  // ============================================================
  
  static TextStyle get headingXL => GoogleFonts.inter(
    fontSize: 44,
    fontWeight: FontWeight.w900,
    letterSpacing: 3,
    color: textPrimary,
  );
  
  static TextStyle get headingLarge => GoogleFonts.inter(
    fontSize: 32,
    fontWeight: FontWeight.w800,
    color: textPrimary,
  );
  
  static TextStyle get headingMedium => GoogleFonts.inter(
    fontSize: 24,
    fontWeight: FontWeight.w700,
    color: textPrimary,
  );
  
  static TextStyle get headingSmall => GoogleFonts.inter(
    fontSize: 18,
    fontWeight: FontWeight.w600,
    color: textPrimary,
  );
  
  static TextStyle get bodyLarge => GoogleFonts.inter(
    fontSize: 16,
    fontWeight: FontWeight.w400,
    color: textSecondary,
  );
  
  static TextStyle get bodyRegular => GoogleFonts.inter(
    fontSize: 14,
    fontWeight: FontWeight.w400,
    color: textSecondary,
  );
  
  static TextStyle get bodySmall => GoogleFonts.inter(
    fontSize: 12,
    fontWeight: FontWeight.w400,
    color: textMuted,
  );
  
  static TextStyle get labelUppercase => GoogleFonts.inter(
    fontSize: 14,
    fontWeight: FontWeight.w800,
    letterSpacing: 1,
    color: textDark,
  );
  
  static TextStyle get timerStyle => GoogleFonts.jetBrainsMono(
    fontSize: 85,
    fontWeight: FontWeight.w900,
    color: textPrimary,
  );
  
  static TextStyle get monoMedium => GoogleFonts.jetBrainsMono(
    fontSize: 24,
    fontWeight: FontWeight.w600,
    color: textPrimary,
  );
  
  // ============================================================
  // THEME DATA
  // ============================================================
  
  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      scaffoldBackgroundColor: backgroundDark,
      colorScheme: const ColorScheme.dark(
        primary: primaryStart,
        secondary: secondaryStart,
        surface: cardBackground,
        error: stressedColor,
      ),
      textTheme: TextTheme(
        displayLarge: headingXL,
        displayMedium: headingLarge,
        displaySmall: headingMedium,
        headlineSmall: headingSmall,
        bodyLarge: bodyLarge,
        bodyMedium: bodyRegular,
        bodySmall: bodySmall,
        labelLarge: labelUppercase,
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: const Color(0xFF0F1420),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(radiusMedium),
          borderSide: const BorderSide(color: Color(0xFF2D3748), width: 2),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(radiusMedium),
          borderSide: const BorderSide(color: Color(0xFF2D3748), width: 2),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(radiusMedium),
          borderSide: const BorderSide(color: primaryStart, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(radiusMedium),
          borderSide: const BorderSide(color: stressedColor, width: 2),
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
        hintStyle: bodyRegular.copyWith(color: textMuted),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: const Color(0x1AFFFFFF),
          foregroundColor: textPrimary,
          padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(radiusMedium),
            side: const BorderSide(color: Color(0x1FFFFFFF)),
          ),
          textStyle: GoogleFonts.inter(
            fontSize: 16,
            fontWeight: FontWeight.w800,
            letterSpacing: 1.5,
          ),
        ),
      ),
      checkboxTheme: CheckboxThemeData(
        fillColor: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return primaryStart;
          }
          return Colors.transparent;
        }),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(4),
        ),
      ),
      progressIndicatorTheme: const ProgressIndicatorThemeData(
        color: primaryStart,
        linearTrackColor: Color(0x0DFFFFFF),
      ),
    );
  }
}
