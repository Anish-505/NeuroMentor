import 'package:flutter/material.dart';
import '../config/state_config.dart';
import '../config/theme.dart';
import '../providers/session_provider.dart';
import '../widgets/task_widgets.dart';

/// Home Screen - Main Dashboard
/// Ported from Python BrainStateApp._build_ui()

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  late SessionProvider _session;

  @override
  void initState() {
    super.initState();
    _session = SessionProvider();
    _session.addListener(_onSessionUpdate);
    _session.onStateComplete = _showCompletionDialog;
  }

  void _onSessionUpdate() {
    setState(() {});
  }

  void _showCompletionDialog(String message) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF0f141e),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: const Text(
          'Session Complete',
          style: TextStyle(color: AppTheme.textPrimary),
        ),
        content: Text(
          message,
          style: const TextStyle(color: AppTheme.textSecondary),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _session.removeListener(_onSessionUpdate);
    _session.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    Color stateColor = AppTheme.getStateColor(_session.currentStateName);
    
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Row(
            children: [
              // Main Content Area
              Expanded(
                flex: 3,
                child: GlassCard(
                  glowColor: stateColor,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // State Title
                      Text(
                        _session.currentStateName.toUpperCase(),
                        style: TextStyle(
                          fontSize: 40,
                          fontWeight: FontWeight.w900,
                          letterSpacing: 3,
                          color: stateColor,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        _session.currentPhase.name.toUpperCase(),
                        style: const TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w800,
                          letterSpacing: 1,
                          color: AppTheme.textMuted,
                        ),
                      ),
                      const SizedBox(height: 24),
                      
                      // Timer Display
                      Center(
                        child: TimerDisplay(
                          time: _session.timerDisplay,
                          glowColor: stateColor,
                        ),
                      ),
                      const SizedBox(height: 16),
                      
                      // Progress Bar
                      ClipRRect(
                        borderRadius: BorderRadius.circular(5),
                        child: LinearProgressIndicator(
                          value: _session.progressPercent,
                          backgroundColor: const Color(0x08FFFFFF),
                          valueColor: AlwaysStoppedAnimation<Color>(stateColor),
                          minHeight: 10,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Phase ${_session.currentPhaseIndex + 1} of ${_session.totalPhases}',
                        style: const TextStyle(
                          color: AppTheme.textMuted,
                          fontSize: 12,
                        ),
                      ),
                      const SizedBox(height: 24),
                      
                      // Task Widget Area
                      Expanded(
                        child: _buildTaskWidget(),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(width: 20),
              
              // Control Panel
              SizedBox(
                width: 280,
                child: GlassCard(
                  padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      const Text(
                        'SYSTEM CONTEXT',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w800,
                          letterSpacing: 1,
                          color: AppTheme.textMuted,
                        ),
                      ),
                      const SizedBox(height: 12),
                      
                      // State Selector
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12),
                        decoration: BoxDecoration(
                          color: const Color(0x99000000),
                          borderRadius: BorderRadius.circular(10),
                          border: Border.all(color: const Color(0x1AFFFFFF)),
                        ),
                        child: DropdownButtonHideUnderline(
                          child: DropdownButton<String>(
                            value: _session.currentStateName,
                            isExpanded: true,
                            dropdownColor: const Color(0xFF0f141e),
                            items: stateConfigs.keys.map((state) {
                              return DropdownMenuItem(
                                value: state,
                                child: Text(
                                  state,
                                  style: const TextStyle(color: Colors.white),
                                ),
                              );
                            }).toList(),
                            onChanged: (value) {
                              if (value != null) {
                                _session.changeState(value);
                              }
                            },
                          ),
                        ),
                      ),
                      const SizedBox(height: 16),
                      
                      // Auto Sequence Toggle
                      Row(
                        children: [
                          Checkbox(
                            value: _session.autoSequence,
                            onChanged: (_) => _session.toggleAutoSequence(),
                            activeColor: stateColor,
                          ),
                          const Text(
                            'Sequential Protocol',
                            style: TextStyle(
                              color: AppTheme.textMuted,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                      
                      const Divider(color: Color(0x1AFFFFFF), height: 32),
                      
                      // Control Buttons
                      _ControlButton(
                        label: _session.isRunning ? 'RUNNING...' : 'INITIALIZE',
                        onPressed: _session.isRunning ? null : _session.start,
                        isPrimary: true,
                        glowColor: stateColor,
                      ),
                      const SizedBox(height: 12),
                      _ControlButton(
                        label: 'PAUSE',
                        onPressed: _session.isRunning ? _session.stop : null,
                      ),
                      const SizedBox(height: 12),
                      _ControlButton(
                        label: 'TERMINATE',
                        onPressed: _session.reset,
                      ),
                      const SizedBox(height: 12),
                      _ControlButton(
                        label: 'INCREMENT PHASE',
                        onPressed: _session.nextPhase,
                      ),
                      
                      const Spacer(),
                      
                      // Help text
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: const Color(0x20000000),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          _session.currentConfig.description,
                          style: const TextStyle(
                            color: AppTheme.textMuted,
                            fontSize: 12,
                            fontStyle: FontStyle.italic,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTaskWidget() {
    switch (_session.currentPhase.mode) {
      case 'breathing':
        return BreathingWidget(session: _session);
      case 'math':
        return MathWidget(session: _session);
      case 'stroop':
        return StroopWidget(session: _session);
      case 'listing':
        return ListingWidget(session: _session);
      case 'reading':
        return ReadingWidget(session: _session);
      case 'recall':
        return RecallWidget(session: _session);
      default:
        return Center(
          child: Text(
            'Unknown mode: ${_session.currentPhase.mode}',
            style: const TextStyle(color: AppTheme.textMuted),
          ),
        );
    }
  }
}

class _ControlButton extends StatelessWidget {
  final String label;
  final VoidCallback? onPressed;
  final bool isPrimary;
  final Color? glowColor;

  const _ControlButton({
    required this.label,
    required this.onPressed,
    this.isPrimary = false,
    this.glowColor,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: isPrimary && glowColor != null
          ? BoxDecoration(
              borderRadius: BorderRadius.circular(12),
              boxShadow: [
                BoxShadow(
                  color: glowColor!.withOpacity(0.4),
                  blurRadius: 20,
                  spreadRadius: 0,
                ),
              ],
            )
          : null,
      child: ElevatedButton(
        onPressed: onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: isPrimary
              ? const Color(0x1AFFFFFF)
              : const Color(0x0AFFFFFF),
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: BorderSide(
              color: isPrimary
                  ? const Color(0x4DFFFFFF)
                  : const Color(0x1FFFFFFF),
            ),
          ),
        ),
        child: Text(
          label,
          style: TextStyle(
            fontWeight: FontWeight.w800,
            letterSpacing: 1.5,
            color: onPressed == null ? AppTheme.textMuted : Colors.white,
          ),
        ),
      ),
    );
  }
}
