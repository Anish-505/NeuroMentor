import 'dart:async';
import 'dart:math';
import 'package:flutter/material.dart';
import '../config/theme.dart';

/// Calibration session screen with timer and tasks
class CalibrationScreen extends StatefulWidget {
  final String state;
  const CalibrationScreen({super.key, required this.state});

  @override
  State<CalibrationScreen> createState() => _CalibrationScreenState();
}

class _CalibrationScreenState extends State<CalibrationScreen> {
  Timer? _timer;
  int _seconds = 0;
  bool _running = false;
  int _phase = 0;
  String _breathCue = 'Ready';

  // Phase durations in seconds
  static const _phaseDuration = 120; // 2 min per phase for demo

  late final List<_PhaseInfo> _phases;

  @override
  void initState() {
    super.initState();
    _phases = _getPhasesForState(widget.state);
  }

  List<_PhaseInfo> _getPhasesForState(String state) {
    switch (state) {
      case 'Calm':
        return [
          _PhaseInfo('Box Breathing', 'Inhale 4s → Hold 4s → Exhale 4s → Hold 4s'),
          _PhaseInfo('4-7-8 Breathing', 'Inhale 4s → Hold 7s → Exhale 8s'),
        ];
      case 'Stressed':
        return [
          _PhaseInfo('Mental Math', 'Subtract 7 from 1000'),
          _PhaseInfo('Stroop Task', 'Identify ink colors, not words'),
        ];
      case 'Focused':
        return [
          _PhaseInfo('Reading', 'Read technical content attentively'),
          _PhaseInfo('Recall', 'Summarize what you read'),
        ];
      default:
        return [_PhaseInfo('Training', 'Follow instructions')];
    }
  }

  void _start() {
    setState(() => _running = true);
    _timer = Timer.periodic(const Duration(seconds: 1), (_) {
      setState(() {
        _seconds++;
        if (widget.state == 'Calm') _updateBreathCue();
        if (_seconds >= _phaseDuration) _nextPhase();
      });
    });
  }

  void _pause() {
    _timer?.cancel();
    setState(() => _running = false);
  }

  void _nextPhase() {
    if (_phase < _phases.length - 1) {
      setState(() {
        _phase++;
        _seconds = 0;
      });
    } else {
      _complete();
    }
  }

  void _complete() {
    _timer?.cancel();
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        backgroundColor: AppTheme.bgDark,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: const Text('Calibration Complete!'),
        content: Text('${widget.state} state training finished.'),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              Navigator.pop(context);
            },
            child: const Text('Done'),
          ),
        ],
      ),
    );
  }

  void _updateBreathCue() {
    final cycle = _seconds % 16; // 4+4+4+4
    if (cycle < 4) {
      _breathCue = 'Inhale (${4 - cycle})';
    } else if (cycle < 8) {
      _breathCue = 'Hold (${8 - cycle})';
    } else if (cycle < 12) {
      _breathCue = 'Exhale (${12 - cycle})';
    } else {
      _breathCue = 'Hold (${16 - cycle})';
    }
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  Color get _stateColor {
    switch (widget.state) {
      case 'Calm':
        return Colors.blue;
      case 'Stressed':
        return Colors.red;
      case 'Focused':
        return Colors.green;
      default:
        return AppTheme.primaryStart;
    }
  }

  @override
  Widget build(BuildContext context) {
    final phaseProgress = _seconds / _phaseDuration;
    final currentPhase = _phases[_phase];

    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(gradient: AppTheme.backgroundGradient),
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              children: [
                // Header
                Row(
                  children: [
                    IconButton(
                      onPressed: () => Navigator.pop(context),
                      icon: const Icon(Icons.close),
                    ),
                    const Spacer(),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                      decoration: BoxDecoration(
                        color: _stateColor.withOpacity(0.2),
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Text(
                        widget.state.toUpperCase(),
                        style: TextStyle(color: _stateColor, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 32),
                // Timer
                Text(
                  '${(_seconds ~/ 60).toString().padLeft(2, '0')}:${(_seconds % 60).toString().padLeft(2, '0')}',
                  style: const TextStyle(fontSize: 64, fontWeight: FontWeight.bold, fontFamily: 'monospace'),
                ),
                const SizedBox(height: 8),
                // Progress bar
                ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: LinearProgressIndicator(
                    value: phaseProgress,
                    backgroundColor: Colors.white.withOpacity(0.1),
                    color: _stateColor,
                    minHeight: 8,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Phase ${_phase + 1} of ${_phases.length}',
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
                const SizedBox(height: 48),
                // Phase info
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(24),
                  decoration: glassDecoration(),
                  child: Column(
                    children: [
                      Text(
                        currentPhase.name,
                        style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: _stateColor),
                      ),
                      const SizedBox(height: 12),
                      Text(
                        currentPhase.instruction,
                        style: Theme.of(context).textTheme.bodyLarge,
                        textAlign: TextAlign.center,
                      ),
                      if (widget.state == 'Calm' && _running) ...[
                        const SizedBox(height: 24),
                        Text(
                          _breathCue,
                          style: const TextStyle(fontSize: 32, fontWeight: FontWeight.w300),
                        ),
                      ],
                      if (widget.state == 'Stressed' && _running) ...[
                        const SizedBox(height: 24),
                        _buildStressTask(),
                      ],
                    ],
                  ),
                ),
                const Spacer(),
                // Controls
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    if (!_running)
                      _ControlButton(
                        icon: Icons.play_arrow,
                        label: 'Start',
                        color: _stateColor,
                        onTap: _start,
                      )
                    else
                      _ControlButton(
                        icon: Icons.pause,
                        label: 'Pause',
                        color: Colors.orange,
                        onTap: _pause,
                      ),
                    _ControlButton(
                      icon: Icons.skip_next,
                      label: 'Skip',
                      color: Colors.white54,
                      onTap: _nextPhase,
                    ),
                  ],
                ),
                const SizedBox(height: 24),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildStressTask() {
    if (_phase == 0) {
      // Math task
      final value = 1000 - ((_seconds * 7) % 1000);
      return Column(
        children: [
          Text('Current: $value', style: const TextStyle(fontSize: 28)),
          const SizedBox(height: 8),
          const Text('Keep subtracting 7', style: TextStyle(color: Colors.white60)),
        ],
      );
    } else {
      // Stroop - show random color word in different color
      final words = ['RED', 'BLUE', 'GREEN', 'YELLOW'];
      final colors = [Colors.red, Colors.blue, Colors.green, Colors.yellow];
      final wordIdx = Random(_seconds).nextInt(4);
      final colorIdx = Random(_seconds + 1).nextInt(4);
      return Column(
        children: [
          Text(
            words[wordIdx],
            style: TextStyle(fontSize: 36, fontWeight: FontWeight.bold, color: colors[colorIdx]),
          ),
          const SizedBox(height: 8),
          const Text('What COLOR is the ink?', style: TextStyle(color: Colors.white60)),
        ],
      );
    }
  }
}

class _PhaseInfo {
  final String name;
  final String instruction;
  _PhaseInfo(this.name, this.instruction);
}

class _ControlButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;

  const _ControlButton({
    required this.icon,
    required this.label,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Column(
        children: [
          Container(
            width: 64,
            height: 64,
            decoration: BoxDecoration(
              color: color.withOpacity(0.2),
              shape: BoxShape.circle,
              border: Border.all(color: color.withOpacity(0.5)),
            ),
            child: Icon(icon, color: color, size: 32),
          ),
          const SizedBox(height: 8),
          Text(label, style: TextStyle(color: color)),
        ],
      ),
    );
  }
}
