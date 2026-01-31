import 'dart:async';
import 'package:flutter/material.dart';
import '../../config/theme.dart';

/// Breathing exercise widget with visual animation
/// Supports box breathing (4-4-4-4) and 4-7-8 patterns
class BreathingWidget extends StatefulWidget {
  final List<int> breathPattern; // [Inhale, Hold, Exhale, Hold]
  final VoidCallback? onCycleComplete;

  const BreathingWidget({
    super.key,
    required this.breathPattern,
    this.onCycleComplete,
  });

  @override
  State<BreathingWidget> createState() => _BreathingWidgetState();
}

class _BreathingWidgetState extends State<BreathingWidget>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  int _currentPhase = 0; // 0=Inhale, 1=Hold, 2=Exhale, 3=Hold
  int _secondsRemaining = 0;
  Timer? _timer;
  int _cycleCount = 0;

  final List<String> _phaseNames = ['INHALE', 'HOLD', 'EXHALE', 'HOLD'];
  final List<Color> _phaseColors = [
    AppTheme.secondaryStart, // Inhale - Blue
    AppTheme.primaryStart, // Hold - Purple
    AppTheme.accentStart, // Exhale - Green
    AppTheme.primaryStart, // Hold - Purple
  ];

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 4),
    );
    _startPhase(0);
  }

  @override
  void dispose() {
    _controller.dispose();
    _timer?.cancel();
    super.dispose();
  }

  void _startPhase(int phase) {
    _currentPhase = phase;
    _secondsRemaining = widget.breathPattern[phase];

    // Skip phases with 0 duration
    if (_secondsRemaining == 0) {
      _advancePhase();
      return;
    }

    // Set animation based on phase
    _controller.duration = Duration(seconds: _secondsRemaining);

    if (phase == 0) {
      // Inhale - expand
      _controller.forward(from: 0.0);
    } else if (phase == 2) {
      // Exhale - contract
      _controller.reverse(from: 1.0);
    }
    // Hold phases: animation stays still

    _timer?.cancel();
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      setState(() {
        _secondsRemaining--;
        if (_secondsRemaining <= 0) {
          timer.cancel();
          _advancePhase();
        }
      });
    });
  }

  void _advancePhase() {
    int nextPhase = (_currentPhase + 1) % 4;

    // If we completed a full cycle
    if (nextPhase == 0) {
      _cycleCount++;
      widget.onCycleComplete?.call();
    }

    _startPhase(nextPhase);
  }

  @override
  Widget build(BuildContext context) {
    final color = _phaseColors[_currentPhase];

    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        // Breathing circle
        AnimatedBuilder(
          animation: _controller,
          builder: (context, child) {
            // Calculate size based on animation and phase
            double size;
            if (_currentPhase == 0) {
              // Inhale: grow from 120 to 200
              size = 120 + (80 * _controller.value);
            } else if (_currentPhase == 2) {
              // Exhale: shrink from 200 to 120
              size = 120 + (80 * _controller.value);
            } else {
              // Hold: stay at current size
              size = _currentPhase == 1 ? 200 : 120;
            }

            return Container(
              width: size,
              height: size,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(
                  colors: [
                    color.withAlpha(150),
                    color.withAlpha(50),
                  ],
                ),
                boxShadow: [
                  BoxShadow(
                    color: color.withAlpha(100),
                    blurRadius: 40,
                    spreadRadius: 10,
                  ),
                ],
              ),
              child: Center(
                child: Text(
                  '$_secondsRemaining',
                  style: AppTheme.timerStyle.copyWith(
                    fontSize: 48,
                    color: Colors.white,
                  ),
                ),
              ),
            );
          },
        ),

        const SizedBox(height: 32),

        // Phase indicator
        AnimatedContainer(
          duration: const Duration(milliseconds: 300),
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          decoration: BoxDecoration(
            color: color.withAlpha(40),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: color.withAlpha(100)),
          ),
          child: Text(
            _phaseNames[_currentPhase],
            style: AppTheme.headingMedium.copyWith(
              color: color,
              letterSpacing: 4,
            ),
          ),
        ),

        const SizedBox(height: 16),

        // Cycle counter
        Text(
          'Cycle $_cycleCount',
          style: AppTheme.bodyRegular.copyWith(
            color: AppTheme.textMuted,
          ),
        ),

        const SizedBox(height: 32),

        // Pattern indicator
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: List.generate(4, (index) {
            final isActive = index == _currentPhase;
            return Container(
              margin: const EdgeInsets.symmetric(horizontal: 4),
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(
                color: isActive
                    ? _phaseColors[index].withAlpha(100)
                    : Colors.white.withAlpha(10),
                borderRadius: BorderRadius.circular(8),
                border:
                    isActive ? Border.all(color: _phaseColors[index]) : null,
              ),
              child: Column(
                children: [
                  Text(
                    _phaseNames[index],
                    style: AppTheme.bodySmall.copyWith(
                      color: isActive ? Colors.white : AppTheme.textMuted,
                      fontSize: 10,
                    ),
                  ),
                  Text(
                    '${widget.breathPattern[index]}s',
                    style: AppTheme.bodySmall.copyWith(
                      color: isActive ? Colors.white : AppTheme.textMuted,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            );
          }),
        ),
      ],
    );
  }
}
