import 'package:flutter/material.dart';
import '../config/theme.dart';
import '../providers/session_provider.dart';

/// Breathing Exercise Widget
/// Displays animated breathing cue with visual feedback

class BreathingWidget extends StatelessWidget {
  final SessionProvider session;

  const BreathingWidget({super.key, required this.session});

  @override
  Widget build(BuildContext context) {
    Color stateColor = AppTheme.getStateColor(session.currentStateName);
    
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        // Breathing cue
        AnimatedContainer(
          duration: const Duration(milliseconds: 300),
          child: Text(
            session.breathCue,
            style: TextStyle(
              fontSize: 48,
              fontWeight: FontWeight.w900,
              color: stateColor,
              shadows: [
                Shadow(
                  color: stateColor.withOpacity(0.5),
                  blurRadius: 20,
                ),
              ],
            ),
            textAlign: TextAlign.center,
          ),
        ),
        const SizedBox(height: 32),
        // Instructions
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: const Color(0x40000000),
            borderRadius: BorderRadius.circular(16),
          ),
          child: Text(
            session.currentPhase.instructions,
            style: const TextStyle(
              fontSize: 14,
              color: AppTheme.textSecondary,
              height: 1.6,
            ),
            textAlign: TextAlign.center,
          ),
        ),
      ],
    );
  }
}

/// Math Exercise Widget
/// Mental math with input field and feedback

class MathWidget extends StatefulWidget {
  final SessionProvider session;

  const MathWidget({super.key, required this.session});

  @override
  State<MathWidget> createState() => _MathWidgetState();
}

class _MathWidgetState extends State<MathWidget> {
  final TextEditingController _controller = TextEditingController();

  void _submitAnswer() {
    widget.session.submitMathAnswer(_controller.text);
    _controller.clear();
  }

  @override
  Widget build(BuildContext context) {
    Color stateColor = AppTheme.getStateColor(widget.session.currentStateName);
    String operation = widget.session.currentPhase.mathOperation ?? 'subtract';
    String symbol = operation == 'add' ? '+' : '-';
    
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text(
          'Current: ${widget.session.mathCurrentValue}',
          style: TextStyle(
            fontSize: 36,
            fontWeight: FontWeight.w900,
            color: stateColor,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          '$symbol 7 = ?',
          style: const TextStyle(
            fontSize: 24,
            color: AppTheme.textSecondary,
          ),
        ),
        const SizedBox(height: 24),
        SizedBox(
          width: 200,
          child: TextField(
            controller: _controller,
            keyboardType: TextInputType.number,
            textAlign: TextAlign.center,
            style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            decoration: InputDecoration(
              hintText: 'Enter answer',
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide(color: stateColor, width: 2),
              ),
            ),
            onSubmitted: (_) => _submitAnswer(),
          ),
        ),
        const SizedBox(height: 16),
        ElevatedButton(
          onPressed: _submitAnswer,
          child: const Text('SUBMIT'),
        ),
        const SizedBox(height: 16),
        Text(
          widget.session.mathFeedback,
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: widget.session.mathFeedback.contains('✓')
                ? Colors.green
                : Colors.red,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          'Score: ${widget.session.scoreCorrect}/${widget.session.scoreAttempts}',
          style: const TextStyle(color: AppTheme.textMuted),
        ),
      ],
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }
}

/// Stroop Task Widget
/// Color-word conflict task with button selection

class StroopWidget extends StatelessWidget {
  final SessionProvider session;

  const StroopWidget({super.key, required this.session});

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        // Color buttons at top
        Wrap(
          spacing: 8,
          runSpacing: 8,
          alignment: WrapAlignment.center,
          children: [
            for (var color in stroopColors)
              ElevatedButton(
                onPressed: () => session.selectStroopColor(color['name']),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0x15FFFFFF),
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                ),
                child: Text(
                  color['name'],
                  style: const TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
          ],
        ),
        const SizedBox(height: 48),
        // Word display
        if (session.stroopCurrentWord != null)
          Text(
            session.stroopCurrentWord!,
            style: TextStyle(
              fontSize: 64,
              fontWeight: FontWeight.w900,
              color: Color(session.stroopCurrentColorValue ?? 0xFFFFFFFF),
            ),
          ),
        const SizedBox(height: 24),
        Text(
          session.stroopFeedback,
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: session.stroopFeedback.contains('✓')
                ? Colors.green
                : Colors.red,
          ),
        ),
        const SizedBox(height: 16),
        Text(
          'Score: ${session.scoreCorrect}/${session.scoreAttempts}',
          style: const TextStyle(color: AppTheme.textMuted, fontSize: 16),
        ),
        const SizedBox(height: 24),
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: const Color(0x40000000),
            borderRadius: BorderRadius.circular(12),
          ),
          child: const Text(
            'Tap the button matching the INK COLOR, not the word!',
            style: TextStyle(color: AppTheme.textMuted),
            textAlign: TextAlign.center,
          ),
        ),
      ],
    );
  }
}

/// Listing Challenge Widget
/// Timed listing with text input

class ListingWidget extends StatelessWidget {
  final SessionProvider session;

  const ListingWidget({super.key, required this.session});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        const Text(
          'Listing Challenge',
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: AppTheme.textPrimary,
          ),
        ),
        const SizedBox(height: 16),
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: const Color(0x40000000),
            borderRadius: BorderRadius.circular(12),
          ),
          child: const Text(
            'List as many items as you can:\n'
            '• Animals\n• Countries\n• Fruits\n• Sports\n\n'
            'Type quickly! Don\'t worry about spelling.',
            style: TextStyle(color: AppTheme.textSecondary, height: 1.5),
          ),
        ),
        const SizedBox(height: 16),
        Expanded(
          child: TextField(
            maxLines: null,
            expands: true,
            textAlignVertical: TextAlignVertical.top,
            decoration: const InputDecoration(
              hintText: 'Start typing items...',
              border: OutlineInputBorder(),
            ),
          ),
        ),
      ],
    );
  }
}

/// Reading Widget
/// Technical article display

class ReadingWidget extends StatelessWidget {
  final SessionProvider session;

  const ReadingWidget({super.key, required this.session});

  @override
  Widget build(BuildContext context) {
    Color stateColor = AppTheme.getStateColor(session.currentStateName);
    
    return Column(
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Expanded(
              child: Text(
                session.currentArticleTitle.isEmpty
                    ? 'No article loaded'
                    : session.currentArticleTitle,
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: stateColor,
                ),
              ),
            ),
            ElevatedButton(
              onPressed: session.loadRandomArticle,
              child: const Text('LOAD ARTICLE'),
            ),
          ],
        ),
        const SizedBox(height: 16),
        Expanded(
          child: Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: const Color(0x40000000),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: const Color(0x1AFFFFFF)),
            ),
            child: SingleChildScrollView(
              child: Text(
                session.currentArticleText.isEmpty
                    ? 'Tap "Load Article" to begin reading.'
                    : session.currentArticleText,
                style: const TextStyle(
                  fontSize: 16,
                  color: AppTheme.textSecondary,
                  height: 1.8,
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}

/// Recall Widget
/// Mental recall and summary text area

class RecallWidget extends StatelessWidget {
  final SessionProvider session;

  const RecallWidget({super.key, required this.session});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        const Text(
          'Mental Recall & Summary',
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: AppTheme.textPrimary,
          ),
        ),
        const SizedBox(height: 16),
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: const Color(0x40000000),
            borderRadius: BorderRadius.circular(12),
          ),
          child: const Text(
            'Try to recall what you just read.\n'
            'Summarize the main ideas in your own words.',
            style: TextStyle(color: AppTheme.textSecondary),
            textAlign: TextAlign.center,
          ),
        ),
        const SizedBox(height: 16),
        Expanded(
          child: TextField(
            maxLines: null,
            expands: true,
            textAlignVertical: TextAlignVertical.top,
            decoration: const InputDecoration(
              hintText: 'Type your summary here...',
              border: OutlineInputBorder(),
            ),
          ),
        ),
      ],
    );
  }
}
