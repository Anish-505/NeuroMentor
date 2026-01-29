import 'package:flutter/material.dart';
import 'package:lucide_icons/lucide_icons.dart';
import '../../config/theme.dart';
import '../../config/calibration_config.dart';
import '../../widgets/glass_card.dart';

/// Calibration home screen - allows selecting calibration state
class CalibrationHomeScreen extends StatelessWidget {
  const CalibrationHomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: AppTheme.backgroundGradient,
        ),
        child: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SizedBox(height: 24),
                
                // Header
                Row(
                  children: [
                    GestureDetector(
                      onTap: () => Navigator.pop(context),
                      child: Container(
                        width: 44,
                        height: 44,
                        decoration: BoxDecoration(
                          color: Colors.white.withAlpha(10),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                            color: Colors.white.withAlpha(20),
                          ),
                        ),
                        child: const Icon(
                          LucideIcons.arrowLeft,
                          color: AppTheme.textSecondary,
                          size: 20,
                        ),
                      ),
                    ),
                    const SizedBox(width: 16),
                    Text(
                      'Calibration',
                      style: AppTheme.headingLarge,
                    ),
                  ],
                ),
                
                const SizedBox(height: 16),
                
                Text(
                  'Complete all three states to establish your personal EEG baseline for accurate attention monitoring.',
                  style: AppTheme.bodyRegular.copyWith(
                    color: AppTheme.textMuted,
                  ),
                ),
                
                const SizedBox(height: 32),
                
                // State cards
                ...stateConfig.entries.map((entry) {
                  final stateName = entry.key;
                  final config = entry.value;
                  final totalMinutes = config.totalSeconds ~/ 60;
                  
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 16),
                    child: _StateCard(
                      name: stateName,
                      description: config.description,
                      color: config.color,
                      phases: config.phases.length,
                      duration: '$totalMinutes min',
                      icon: _getStateIcon(stateName),
                      onTap: () {
                        Navigator.pushNamed(
                          context,
                          '/calibration/session',
                          arguments: stateName,
                        );
                      },
                    ),
                  );
                }),
                
                const SizedBox(height: 24),
                
                // Info card
                GlassCard(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Container(
                            width: 36,
                            height: 36,
                            decoration: BoxDecoration(
                              color: AppTheme.secondaryStart.withAlpha(30),
                              borderRadius: BorderRadius.circular(10),
                            ),
                            child: const Icon(
                              LucideIcons.info,
                              color: AppTheme.secondaryStart,
                              size: 18,
                            ),
                          ),
                          const SizedBox(width: 12),
                          Text(
                            'How Calibration Works',
                            style: AppTheme.bodyLarge.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      Text(
                        '• Each state has multiple phases with specific tasks\n'
                        '• EEG data is recorded during each phase\n'
                        '• Your personal baseline is calculated from this data\n'
                        '• Live monitoring compares your current state to these baselines',
                        style: AppTheme.bodySmall.copyWith(
                          color: AppTheme.textSecondary,
                          height: 1.5,
                        ),
                      ),
                    ],
                  ),
                ),
                
                const SizedBox(height: 32),
                
                // Skip calibration option
                Center(
                  child: GestureDetector(
                    onTap: () {
                      _showSkipDialog(context);
                    },
                    child: Text(
                      'Use default dataset instead',
                      style: AppTheme.bodySmall.copyWith(
                        color: AppTheme.textMuted,
                        decoration: TextDecoration.underline,
                      ),
                    ),
                  ),
                ),
                
                const SizedBox(height: 32),
              ],
            ),
          ),
        ),
      ),
    );
  }
  
  IconData _getStateIcon(String stateName) {
    switch (stateName) {
      case 'Calm':
        return LucideIcons.heart;
      case 'Stressed':
        return LucideIcons.zap;
      case 'Focused':
        return LucideIcons.target;
      default:
        return LucideIcons.brain;
    }
  }
  
  void _showComingSoonDialog(BuildContext context, String stateName) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: AppTheme.cardBackground,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(24),
        ),
        title: Text(
          '$stateName Calibration',
          style: AppTheme.headingMedium,
        ),
        content: Text(
          'The full calibration session interface is coming soon. '
          'This will include all the breathing, math, Stroop, reading, and recall tasks.',
          style: AppTheme.bodyRegular.copyWith(
            color: AppTheme.textSecondary,
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(
              'OK',
              style: AppTheme.bodyRegular.copyWith(
                color: AppTheme.primaryStart,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
    );
  }
  
  void _showSkipDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: AppTheme.cardBackground,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(24),
        ),
        title: Text(
          'Use Default Dataset?',
          style: AppTheme.headingMedium,
        ),
        content: Text(
          'The default dataset provides average baselines that may not accurately reflect your personal EEG patterns. '
          'For best results, complete the calibration process.',
          style: AppTheme.bodyRegular.copyWith(
            color: AppTheme.textSecondary,
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(
              'Cancel',
              style: AppTheme.bodyRegular.copyWith(
                color: AppTheme.textMuted,
              ),
            ),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              Navigator.pop(context);
              // TODO: Set default calibration
            },
            child: Text(
              'Use Default',
              style: AppTheme.bodyRegular.copyWith(
                color: AppTheme.primaryStart,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

/// State card widget
class _StateCard extends StatelessWidget {
  final String name;
  final String description;
  final Color color;
  final int phases;
  final String duration;
  final IconData icon;
  final VoidCallback onTap;
  
  const _StateCard({
    required this.name,
    required this.description,
    required this.color,
    required this.phases,
    required this.duration,
    required this.icon,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: AppTheme.cardBackground,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: color.withAlpha(50),
            width: 1,
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    color: color.withAlpha(40),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(
                    icon,
                    color: color,
                    size: 24,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        name,
                        style: AppTheme.headingSmall.copyWith(
                          color: color,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Row(
                        children: [
                          Icon(
                            LucideIcons.layers,
                            color: AppTheme.textMuted,
                            size: 14,
                          ),
                          const SizedBox(width: 4),
                          Text(
                            '$phases phases',
                            style: AppTheme.bodySmall,
                          ),
                          const SizedBox(width: 12),
                          Icon(
                            LucideIcons.clock,
                            color: AppTheme.textMuted,
                            size: 14,
                          ),
                          const SizedBox(width: 4),
                          Text(
                            duration,
                            style: AppTheme.bodySmall,
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                Icon(
                  LucideIcons.chevronRight,
                  color: color.withAlpha(150),
                  size: 24,
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              description,
              style: AppTheme.bodySmall.copyWith(
                color: AppTheme.textMuted,
              ),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ),
      ),
    );
  }
}
