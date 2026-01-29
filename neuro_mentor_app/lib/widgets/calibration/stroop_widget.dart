import 'dart:math';
import 'package:flutter/material.dart';
import '../../config/theme.dart';
import '../../config/calibration_config.dart';

/// Stroop task widget for stress calibration
/// User must click button matching the INK COLOR, not the word
class StroopWidget extends StatefulWidget {
  final Function(int correct, int total)? onScoreUpdate;
  
  const StroopWidget({
    super.key,
    this.onScoreUpdate,
  });

  @override
  State<StroopWidget> createState() => _StroopWidgetState();
}

class _StroopWidgetState extends State<StroopWidget>
    with SingleTickerProviderStateMixin {
  final Random _random = Random();
  
  late String _displayWord;
  late String _inkColorName;
  late Color _inkColor;
  
  int _correctCount = 0;
  int _totalTrials = 0;
  String? _feedback;
  bool _isCorrect = false;
  
  late AnimationController _feedbackController;
  late Animation<double> _feedbackAnimation;

  @override
  void initState() {
    super.initState();
    _feedbackController = AnimationController(
      duration: const Duration(milliseconds: 500),
      vsync: this,
    );
    _feedbackAnimation = CurvedAnimation(
      parent: _feedbackController,
      curve: Curves.easeOut,
    );
    _generateTrial();
  }

  @override
  void dispose() {
    _feedbackController.dispose();
    super.dispose();
  }

  void _generateTrial() {
    // Pick a random word
    final wordIndex = _random.nextInt(defaultStroopColors.length);
    _displayWord = defaultStroopColors[wordIndex].key;
    
    // Pick a random ink color (50% chance of mismatch for cognitive conflict)
    int colorIndex;
    if (_random.nextDouble() < 0.5) {
      // Match
      colorIndex = wordIndex;
    } else {
      // Mismatch
      do {
        colorIndex = _random.nextInt(defaultStroopColors.length);
      } while (colorIndex == wordIndex);
    }
    
    _inkColorName = defaultStroopColors[colorIndex].key;
    _inkColor = defaultStroopColors[colorIndex].value;
    
    setState(() {
      _feedback = null;
    });
  }

  void _checkAnswer(String selectedColor) {
    _totalTrials++;
    
    if (selectedColor == _inkColorName) {
      _correctCount++;
      _isCorrect = true;
      _feedback = 'Correct! ✓';
    } else {
      _isCorrect = false;
      _feedback = 'Wrong! Ink was $_inkColorName';
    }
    
    setState(() {});
    widget.onScoreUpdate?.call(_correctCount, _totalTrials);
    
    // Show feedback animation then generate new trial
    _feedbackController.forward(from: 0).then((_) {
      Future.delayed(const Duration(milliseconds: 300), () {
        if (mounted) _generateTrial();
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        // Instructions
        Container(
          padding: const EdgeInsets.all(16),
          margin: const EdgeInsets.only(bottom: 24),
          decoration: BoxDecoration(
            color: AppTheme.unfocusedColor.withAlpha(20),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: AppTheme.unfocusedColor.withAlpha(50)),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                Icons.info_outline,
                color: AppTheme.unfocusedColor,
                size: 20,
              ),
              const SizedBox(width: 8),
              Text(
                'Click the button matching the INK COLOR',
                style: AppTheme.bodyRegular.copyWith(
                  color: AppTheme.unfocusedColor,
                ),
              ),
            ],
          ),
        ),
        
        // Display word with colored ink
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 48, vertical: 32),
          decoration: BoxDecoration(
            color: AppTheme.cardBackground,
            borderRadius: BorderRadius.circular(24),
            border: Border.all(color: _inkColor.withAlpha(100)),
            boxShadow: [
              BoxShadow(
                color: _inkColor.withAlpha(50),
                blurRadius: 30,
              ),
            ],
          ),
          child: Text(
            _displayWord.toUpperCase(),
            style: AppTheme.headingXL.copyWith(
              fontSize: 56,
              color: _inkColor,
              fontWeight: FontWeight.w900,
            ),
          ),
        ),
        
        const SizedBox(height: 32),
        
        // Color buttons
        Wrap(
          spacing: 12,
          runSpacing: 12,
          alignment: WrapAlignment.center,
          children: defaultStroopColors.map((entry) {
            return _ColorButton(
              colorName: entry.key,
              color: entry.value,
              onTap: () => _checkAnswer(entry.key),
            );
          }).toList(),
        ),
        
        const SizedBox(height: 24),
        
        // Feedback
        AnimatedBuilder(
          animation: _feedbackAnimation,
          builder: (context, child) {
            if (_feedback == null) return const SizedBox(height: 48);
            
            return Opacity(
              opacity: 1 - _feedbackAnimation.value,
              child: Transform.scale(
                scale: 1 + (_feedbackAnimation.value * 0.2),
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                  decoration: BoxDecoration(
                    color: (_isCorrect ? AppTheme.focusedColor : AppTheme.stressedColor)
                        .withAlpha(40),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    _feedback!,
                    style: AppTheme.headingSmall.copyWith(
                      color: _isCorrect ? AppTheme.focusedColor : AppTheme.stressedColor,
                    ),
                  ),
                ),
              ),
            );
          },
        ),
        
        const SizedBox(height: 24),
        
        // Score
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          decoration: BoxDecoration(
            color: Colors.white.withAlpha(10),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                'Score: ',
                style: AppTheme.bodyRegular.copyWith(
                  color: AppTheme.textMuted,
                ),
              ),
              Text(
                '$_correctCount / $_totalTrials',
                style: AppTheme.headingSmall.copyWith(
                  color: AppTheme.focusedColor,
                ),
              ),
              if (_totalTrials > 0) ...[
                const SizedBox(width: 12),
                Text(
                  '(${((_correctCount / _totalTrials) * 100).toInt()}%)',
                  style: AppTheme.bodyRegular.copyWith(
                    color: AppTheme.textMuted,
                  ),
                ),
              ],
            ],
          ),
        ),
      ],
    );
  }
}

class _ColorButton extends StatelessWidget {
  final String colorName;
  final Color color;
  final VoidCallback onTap;
  
  const _ColorButton({
    required this.colorName,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 80,
        padding: const EdgeInsets.symmetric(vertical: 12),
        decoration: BoxDecoration(
          color: color.withAlpha(30),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: color, width: 2),
        ),
        child: Center(
          child: Text(
            colorName,
            style: AppTheme.bodySmall.copyWith(
              color: color,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
      ),
    );
  }
}
