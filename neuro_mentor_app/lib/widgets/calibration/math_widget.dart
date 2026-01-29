import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../config/theme.dart';
import '../../config/calibration_config.dart';

/// Mental math widget for stress calibration
/// Supports addition and subtraction with step values
class MathWidget extends StatefulWidget {
  final MathOp operation;
  final int startValue;
  final int stepValue;
  final Function(int correct, int total)? onScoreUpdate;
  
  const MathWidget({
    super.key,
    required this.operation,
    required this.startValue,
    required this.stepValue,
    this.onScoreUpdate,
  });

  @override
  State<MathWidget> createState() => _MathWidgetState();
}

class _MathWidgetState extends State<MathWidget> {
  final _controller = TextEditingController();
  final _focusNode = FocusNode();
  
  late int _currentValue;
  int _correctCount = 0;
  int _totalAttempts = 0;
  String? _feedback;
  bool _isCorrect = false;

  @override
  void initState() {
    super.initState();
    _currentValue = widget.startValue;
  }

  @override
  void dispose() {
    _controller.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  void _checkAnswer() {
    final input = _controller.text.trim();
    if (input.isEmpty) return;
    
    final userAnswer = int.tryParse(input);
    if (userAnswer == null) {
      setState(() {
        _feedback = 'Please enter a valid number';
        _isCorrect = false;
      });
      return;
    }
    
    // Calculate expected answer
    int expected;
    if (widget.operation == MathOp.subtract) {
      expected = _currentValue - widget.stepValue;
    } else {
      expected = _currentValue + widget.stepValue;
    }
    
    _totalAttempts++;
    
    if (userAnswer == expected) {
      _correctCount++;
      _currentValue = expected;
      _feedback = 'Correct! ✓';
      _isCorrect = true;
    } else {
      _feedback = 'Try again! Expected: $expected';
      _isCorrect = false;
    }
    
    setState(() {});
    widget.onScoreUpdate?.call(_correctCount, _totalAttempts);
    
    // Clear input for next attempt
    _controller.clear();
    _focusNode.requestFocus();
  }

  @override
  Widget build(BuildContext context) {
    final opSymbol = widget.operation == MathOp.subtract ? '−' : '+';
    
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        // Current number display
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 48, vertical: 24),
          decoration: BoxDecoration(
            color: AppTheme.cardBackground,
            borderRadius: BorderRadius.circular(24),
            border: Border.all(color: AppTheme.stressedColor.withAlpha(50)),
            boxShadow: [
              BoxShadow(
                color: AppTheme.stressedColor.withAlpha(30),
                blurRadius: 20,
              ),
            ],
          ),
          child: Column(
            children: [
              Text(
                '$_currentValue $opSymbol ${widget.stepValue} = ?',
                style: AppTheme.headingLarge.copyWith(
                  fontSize: 36,
                  color: AppTheme.stressedColor,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                widget.operation == MathOp.subtract
                    ? 'Keep subtracting ${widget.stepValue}'
                    : 'Keep adding ${widget.stepValue}',
                style: AppTheme.bodySmall.copyWith(
                  color: AppTheme.textMuted,
                ),
              ),
            ],
          ),
        ),
        
        const SizedBox(height: 32),
        
        // Answer input
        SizedBox(
          width: 200,
          child: TextField(
            controller: _controller,
            focusNode: _focusNode,
            keyboardType: TextInputType.number,
            textAlign: TextAlign.center,
            style: AppTheme.headingMedium.copyWith(
              fontSize: 32,
            ),
            inputFormatters: [
              FilteringTextInputFormatter.allow(RegExp(r'[0-9-]')),
            ],
            decoration: InputDecoration(
              hintText: 'Answer',
              hintStyle: AppTheme.bodyLarge.copyWith(
                color: AppTheme.textMuted,
              ),
              filled: true,
              fillColor: const Color(0xFF0F1420),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(16),
                borderSide: BorderSide(
                  color: _feedback != null && !_isCorrect
                      ? AppTheme.stressedColor
                      : AppTheme.cardBorder,
                  width: 2,
                ),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(16),
                borderSide: BorderSide(
                  color: _isCorrect ? AppTheme.focusedColor : AppTheme.primaryStart,
                  width: 2,
                ),
              ),
            ),
            onSubmitted: (_) => _checkAnswer(),
          ),
        ),
        
        const SizedBox(height: 16),
        
        // Submit button
        GestureDetector(
          onTap: _checkAnswer,
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 12),
            decoration: BoxDecoration(
              gradient: AppTheme.primaryGradient,
              borderRadius: BorderRadius.circular(12),
              boxShadow: [
                BoxShadow(
                  color: AppTheme.primaryStart.withAlpha(80),
                  blurRadius: 16,
                ),
              ],
            ),
            child: Text(
              'SUBMIT',
              style: AppTheme.labelUppercase.copyWith(
                color: Colors.white,
              ),
            ),
          ),
        ),
        
        const SizedBox(height: 24),
        
        // Feedback
        if (_feedback != null)
          AnimatedContainer(
            duration: const Duration(milliseconds: 200),
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
            decoration: BoxDecoration(
              color: (_isCorrect ? AppTheme.focusedColor : AppTheme.stressedColor)
                  .withAlpha(30),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(
              _feedback!,
              style: AppTheme.bodyLarge.copyWith(
                color: _isCorrect ? AppTheme.focusedColor : AppTheme.stressedColor,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        
        const SizedBox(height: 24),
        
        // Score display
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
                '$_correctCount / $_totalAttempts',
                style: AppTheme.headingSmall.copyWith(
                  color: AppTheme.focusedColor,
                ),
              ),
              if (_totalAttempts > 0) ...[
                const SizedBox(width: 12),
                Text(
                  '(${((_correctCount / _totalAttempts) * 100).toInt()}%)',
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
