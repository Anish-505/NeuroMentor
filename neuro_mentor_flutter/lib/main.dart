import 'package:flutter/material.dart';
import 'config/theme.dart';
import 'screens/home_screen.dart';

/// NeuroMentor Flutter App
/// EEG-based Stress Monitoring and Calibration Application
/// 
/// Port of the PyQt5 calibration_final.py to Flutter
/// 
/// Features:
/// - Calm State: Box Breathing (4-4-4-4) and 4-7-8 Breathing exercises
/// - Stressed State: Mental Math, Stroop Task, and Listing Challenges
/// - Focused State: Technical Reading and Mental Recall
/// 
/// Author: NeuroMentor Team

void main() {
  runApp(const NeuroMentorApp());
}

class NeuroMentorApp extends StatelessWidget {
  const NeuroMentorApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'NeuroMentor',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme,
      home: const HomeScreen(),
    );
  }
}
