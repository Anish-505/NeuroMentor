import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:lucide_icons/lucide_icons.dart';
import '../../config/theme.dart';
import '../../models/attention_session.dart';
import '../../providers/auth_provider.dart';
import '../../providers/user_data_provider.dart';
import '../../providers/monitoring_provider.dart';
import '../../widgets/glass_card.dart';
import '../../widgets/gradient_button.dart';
import '../../widgets/attention_graph.dart';

/// Live EEG monitoring screen with real-time visualization
class LiveMonitoringScreen extends StatefulWidget {
  const LiveMonitoringScreen({super.key});

  @override
  State<LiveMonitoringScreen> createState() => _LiveMonitoringScreenState();
}

class _LiveMonitoringScreenState extends State<LiveMonitoringScreen> {
  @override
  void initState() {
    super.initState();
    _setupMonitoring();
  }

  void _setupMonitoring() {
    final auth = context.read<AuthProvider>();
    final userData = context.read<UserDataProvider>();
    final monitoring = context.read<MonitoringProvider>();
    
    // Set calibration data for monitoring
    if (auth.currentUser != null) {
      final calibration = userData.getActiveCalibration(auth.currentUser!.uid);
      monitoring.setCalibrationData(calibration);
    }
  }

  Future<void> _startMonitoring() async {
    final auth = context.read<AuthProvider>();
    final monitoring = context.read<MonitoringProvider>();
    
    if (auth.currentUser != null) {
      await monitoring.startMonitoring(auth.currentUser!.uid);
    }
  }

  Future<void> _stopMonitoring() async {
    final monitoring = context.read<MonitoringProvider>();
    final userData = context.read<UserDataProvider>();
    
    final session = await monitoring.stopMonitoring();
    
    if (session != null) {
      await userData.saveSession(session);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: AppTheme.backgroundGradient,
        ),
        child: SafeArea(
          child: Consumer<MonitoringProvider>(
            builder: (context, monitoring, _) {
              return Column(
                children: [
                  // Header
                  Padding(
                    padding: const EdgeInsets.all(24),
                    child: Row(
                      children: [
                        GestureDetector(
                          onTap: () {
                            if (monitoring.isMonitoring) {
                              _showExitDialog();
                            } else {
                              Navigator.pop(context);
                            }
                          },
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
                        Expanded(
                          child: Text(
                            'Live Monitoring',
                            style: AppTheme.headingLarge,
                          ),
                        ),
                        // Mock state selector (for testing)
                        if (monitoring.isMonitoring)
                          PopupMenuButton<String>(
                            icon: const Icon(
                              LucideIcons.settings,
                              color: AppTheme.textMuted,
                            ),
                            color: AppTheme.cardBackground,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(16),
                            ),
                            itemBuilder: (context) => [
                              _buildMenuItem('Calm', 'Simulate calm state'),
                              _buildMenuItem('Stressed', 'Simulate stress'),
                              _buildMenuItem('Focused', 'Simulate focus'),
                            ],
                            onSelected: (state) {
                              monitoring.setMockState(state);
                            },
                          ),
                      ],
                    ),
                  ),
                  
                  // Main content
                  Expanded(
                    child: SingleChildScrollView(
                      padding: const EdgeInsets.symmetric(horizontal: 24),
                      child: Column(
                        children: [
                          // Session timer and state
                          _buildSessionHeader(monitoring),
                          
                          const SizedBox(height: 24),
                          
                          // Current state indicator
                          _buildStateIndicator(monitoring),
                          
                          const SizedBox(height: 24),
                          
                          // Focus and stress gauges
                          Row(
                            children: [
                              Expanded(
                                child: _buildGauge(
                                  'FOCUS',
                                  monitoring.currentFocusLevel,
                                  AppTheme.focusedColor,
                                ),
                              ),
                              const SizedBox(width: 16),
                              Expanded(
                                child: _buildGauge(
                                  'STRESS',
                                  monitoring.currentStressLevel,
                                  AppTheme.stressedColor,
                                ),
                              ),
                            ],
                          ),
                          
                          const SizedBox(height: 24),
                          
                          // Focus history graph
                          AttentionGraph(
                            data: monitoring.focusHistory,
                            lineColor: AppTheme.focusedColor,
                            label: 'FOCUS LEVEL',
                          ),
                          
                          const SizedBox(height: 16),
                          
                          // Stress history graph
                          AttentionGraph(
                            data: monitoring.stressHistory,
                            lineColor: AppTheme.stressedColor,
                            label: 'STRESS LEVEL',
                          ),
                          
                          const SizedBox(height: 16),
                          
                          // Band powers
                          BandPowerChart(
                            bandPowers: monitoring.currentBandPowers,
                          ),
                          
                          const SizedBox(height: 24),
                          
                          // Start/Stop button
                          SizedBox(
                            width: double.infinity,
                            child: GradientButton(
                              text: monitoring.isMonitoring ? 'Stop Session' : 'Start Monitoring',
                              icon: monitoring.isMonitoring 
                                  ? LucideIcons.square 
                                  : LucideIcons.play,
                              gradient: monitoring.isMonitoring
                                  ? const LinearGradient(
                                      colors: [AppTheme.stressedColor, Color(0xFFB91C1C)],
                                    )
                                  : AppTheme.accentGradient,
                              onPressed: () {
                                if (monitoring.isMonitoring) {
                                  _stopMonitoring();
                                } else {
                                  _startMonitoring();
                                }
                              },
                            ),
                          ),
                          
                          const SizedBox(height: 32),
                        ],
                      ),
                    ),
                  ),
                ],
              );
            },
          ),
        ),
      ),
    );
  }
  
  Widget _buildSessionHeader(MonitoringProvider monitoring) {
    final duration = monitoring.sessionDuration;
    final minutes = duration.inMinutes.toString().padLeft(2, '0');
    final seconds = (duration.inSeconds % 60).toString().padLeft(2, '0');
    
    return GlassCard(
      padding: const EdgeInsets.symmetric(vertical: 24, horizontal: 32),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'SESSION TIME',
                style: AppTheme.labelUppercase,
              ),
              const SizedBox(height: 4),
              Text(
                '$minutes:$seconds',
                style: AppTheme.monoMedium.copyWith(
                  fontSize: 36,
                ),
              ),
            ],
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            decoration: BoxDecoration(
              color: monitoring.isMonitoring
                  ? AppTheme.focusedColor.withAlpha(30)
                  : Colors.white.withAlpha(10),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(
              children: [
                Container(
                  width: 8,
                  height: 8,
                  decoration: BoxDecoration(
                    color: monitoring.isMonitoring
                        ? AppTheme.focusedColor
                        : AppTheme.textMuted,
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 8),
                Text(
                  monitoring.isMonitoring ? 'LIVE' : 'READY',
                  style: AppTheme.labelUppercase.copyWith(
                    color: monitoring.isMonitoring
                        ? AppTheme.focusedColor
                        : AppTheme.textMuted,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildStateIndicator(MonitoringProvider monitoring) {
    final state = monitoring.currentState;
    final color = Color(state.colorValue);
    
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            color.withAlpha(40),
            color.withAlpha(20),
          ],
        ),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: color.withAlpha(100),
          width: 2,
        ),
      ),
      child: Column(
        children: [
          Icon(
            _getStateIcon(state),
            color: color,
            size: 48,
          ),
          const SizedBox(height: 12),
          Text(
            state.displayName.toUpperCase(),
            style: AppTheme.headingLarge.copyWith(
              color: color,
              letterSpacing: 2,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            _getStateMessage(state),
            style: AppTheme.bodySmall.copyWith(
              color: AppTheme.textMuted,
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildGauge(String label, double value, Color color) {
    return GlassCard(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          Text(label, style: AppTheme.labelUppercase),
          const SizedBox(height: 12),
          Stack(
            alignment: Alignment.center,
            children: [
              SizedBox(
                width: 80,
                height: 80,
                child: CircularProgressIndicator(
                  value: value,
                  strokeWidth: 8,
                  backgroundColor: Colors.white.withAlpha(10),
                  valueColor: AlwaysStoppedAnimation(color),
                ),
              ),
              Text(
                '${(value * 100).toInt()}%',
                style: AppTheme.headingMedium.copyWith(
                  color: color,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
  
  PopupMenuItem<String> _buildMenuItem(String value, String text) {
    return PopupMenuItem(
      value: value,
      child: Text(
        text,
        style: AppTheme.bodyRegular,
      ),
    );
  }
  
  IconData _getStateIcon(MentalState state) {
    switch (state) {
      case MentalState.calm:
        return LucideIcons.heart;
      case MentalState.focused:
        return LucideIcons.target;
      case MentalState.stressed:
        return LucideIcons.alertTriangle;
      case MentalState.unfocused:
        return LucideIcons.cloudOff;
    }
  }
  
  String _getStateMessage(MentalState state) {
    switch (state) {
      case MentalState.calm:
        return 'Your mind is relaxed and at ease';
      case MentalState.focused:
        return 'Great concentration! Keep it up';
      case MentalState.stressed:
        return 'High stress detected - take a breath';
      case MentalState.unfocused:
        return 'Attention drifting - refocus';
    }
  }
  
  void _showExitDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: AppTheme.cardBackground,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(24),
        ),
        title: Text(
          'End Session?',
          style: AppTheme.headingMedium,
        ),
        content: Text(
          'This will stop the current monitoring session. Your data will be saved.',
          style: AppTheme.bodyRegular.copyWith(
            color: AppTheme.textSecondary,
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(
              'Continue',
              style: AppTheme.bodyRegular.copyWith(
                color: AppTheme.textMuted,
              ),
            ),
          ),
          TextButton(
            onPressed: () async {
              Navigator.pop(context);
              await _stopMonitoring();
              if (mounted) {
                Navigator.pop(context);
              }
            },
            child: Text(
              'End & Save',
              style: AppTheme.bodyRegular.copyWith(
                color: AppTheme.stressedColor,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
