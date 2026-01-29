import 'package:flutter/material.dart';
import '../../config/theme.dart';

/// Recall widget for focus calibration
/// User must recall key points from the reading
class RecallWidget extends StatefulWidget {
  final String articleTitle;
  final List<String> keywords;
  final Function(String summary)? onSubmit;
  
  const RecallWidget({
    super.key,
    required this.articleTitle,
    required this.keywords,
    this.onSubmit,
  });

  @override
  State<RecallWidget> createState() => _RecallWidgetState();
}

class _RecallWidgetState extends State<RecallWidget> {
  final _controller = TextEditingController();
  final Map<String, bool> _keywordRecalled = {};
  bool _submitted = false;

  @override
  void initState() {
    super.initState();
    for (final keyword in widget.keywords) {
      _keywordRecalled[keyword.toLowerCase()] = false;
    }
    _controller.addListener(_checkKeywords);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _checkKeywords() {
    final text = _controller.text.toLowerCase();
    setState(() {
      for (final keyword in widget.keywords) {
        _keywordRecalled[keyword.toLowerCase()] = 
            text.contains(keyword.toLowerCase());
      }
    });
  }

  void _submit() {
    setState(() {
      _submitted = true;
    });
    widget.onSubmit?.call(_controller.text);
  }

  @override
  Widget build(BuildContext context) {
    final recalledCount = _keywordRecalled.values.where((v) => v).length;
    final totalKeywords = widget.keywords.length;
    
    return SingleChildScrollView(
      child: Column(
        children: [
          // Instructions
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [
                  AppTheme.focusedColor.withAlpha(30),
                  AppTheme.focusedColor.withAlpha(15),
                ],
              ),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: AppTheme.focusedColor.withAlpha(50)),
            ),
            child: Column(
              children: [
                Text(
                  'SUMMARIZE WHAT YOU READ',
                  style: AppTheme.labelUppercase.copyWith(
                    color: AppTheme.focusedColor,
                    letterSpacing: 2,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'About: ${widget.articleTitle}',
                  style: AppTheme.bodyLarge.copyWith(
                    color: Colors.white,
                  ),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),
          
          const SizedBox(height: 20),
          
          // Keyword tracker
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppTheme.cardBackground,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppTheme.cardBorder),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                      'Keywords to include:',
                      style: AppTheme.bodySmall.copyWith(
                        color: AppTheme.textMuted,
                      ),
                    ),
                    const Spacer(),
                    Text(
                      '$recalledCount / $totalKeywords',
                      style: AppTheme.bodySmall.copyWith(
                        color: recalledCount == totalKeywords
                            ? AppTheme.focusedColor
                            : AppTheme.unfocusedColor,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: widget.keywords.map((keyword) {
                    final found = _keywordRecalled[keyword.toLowerCase()] ?? false;
                    return Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 6,
                      ),
                      decoration: BoxDecoration(
                        color: found
                            ? AppTheme.focusedColor.withAlpha(30)
                            : Colors.white.withAlpha(10),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(
                          color: found
                              ? AppTheme.focusedColor
                              : AppTheme.textMuted.withAlpha(50),
                        ),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          if (found)
                            Icon(
                              Icons.check,
                              color: AppTheme.focusedColor,
                              size: 14,
                            ),
                          if (found) const SizedBox(width: 4),
                          Text(
                            keyword,
                            style: AppTheme.bodySmall.copyWith(
                              color: found ? AppTheme.focusedColor : AppTheme.textMuted,
                              fontWeight: found ? FontWeight.bold : FontWeight.normal,
                            ),
                          ),
                        ],
                      ),
                    );
                  }).toList(),
                ),
              ],
            ),
          ),
          
          const SizedBox(height: 20),
          
          // Summary input
          Container(
            decoration: BoxDecoration(
              color: AppTheme.cardBackground,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: AppTheme.cardBorder),
            ),
            child: TextField(
              controller: _controller,
              maxLines: 8,
              enabled: !_submitted,
              style: AppTheme.bodyRegular,
              decoration: InputDecoration(
                hintText: 'Write your summary here...\n\n'
                    'Try to use the keywords listed above.',
                hintStyle: AppTheme.bodyRegular.copyWith(
                  color: AppTheme.textMuted,
                ),
                border: InputBorder.none,
                contentPadding: const EdgeInsets.all(16),
              ),
            ),
          ),
          
          const SizedBox(height: 16),
          
          // Word count
          Text(
            '${_controller.text.split(RegExp(r'\s+')).where((s) => s.isNotEmpty).length} words',
            style: AppTheme.bodySmall.copyWith(
              color: AppTheme.textMuted,
            ),
          ),
          
          if (_submitted) ...[
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
              decoration: BoxDecoration(
                color: AppTheme.focusedColor.withAlpha(30),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                'Summary submitted! ✓',
                style: AppTheme.bodyLarge.copyWith(
                  color: AppTheme.focusedColor,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }
}
