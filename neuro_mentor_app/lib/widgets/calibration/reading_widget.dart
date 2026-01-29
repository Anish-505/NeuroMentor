import 'package:flutter/material.dart';
import '../../config/theme.dart';
import '../../config/technical_articles.dart';

/// Reading widget for focus calibration
/// Displays an article for concentrated reading
class ReadingWidget extends StatefulWidget {
  final Article article;
  final List<String>? keywords;
  
  const ReadingWidget({
    super.key,
    required this.article,
    this.keywords,
  });

  @override
  State<ReadingWidget> createState() => _ReadingWidgetState();
}

class _ReadingWidgetState extends State<ReadingWidget> {
  final ScrollController _scrollController = ScrollController();
  double _readProgress = 0;

  @override
  void initState() {
    super.initState();
    _scrollController.addListener(_updateProgress);
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  void _updateProgress() {
    if (_scrollController.hasClients) {
      final maxScroll = _scrollController.position.maxScrollExtent;
      if (maxScroll > 0) {
        setState(() {
          _readProgress = _scrollController.offset / maxScroll;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Progress bar
        Container(
          height: 4,
          decoration: BoxDecoration(
            color: Colors.white.withAlpha(10),
            borderRadius: BorderRadius.circular(2),
          ),
          child: Row(
            children: [
              AnimatedContainer(
                duration: const Duration(milliseconds: 100),
                width: MediaQuery.of(context).size.width * 
                    _readProgress.clamp(0.0, 1.0) * 0.9,
                decoration: BoxDecoration(
                  gradient: AppTheme.accentGradient,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ],
          ),
        ),
        
        const SizedBox(height: 16),
        
        // Article header
        Text(
          widget.article.title,
          style: AppTheme.headingMedium.copyWith(
            color: AppTheme.focusedColor,
          ),
          textAlign: TextAlign.center,
        ),
        
        const SizedBox(height: 8),
        
        if (widget.keywords != null && widget.keywords!.isNotEmpty)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: AppTheme.unfocusedColor.withAlpha(20),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              'Remember: ${widget.keywords!.join(", ")}',
              style: AppTheme.bodySmall.copyWith(
                color: AppTheme.unfocusedColor,
                fontStyle: FontStyle.italic,
              ),
            ),
          ),
        
        const SizedBox(height: 16),
        
        // Article content
        Expanded(
          child: Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: AppTheme.cardBackground,
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: AppTheme.cardBorder),
            ),
            child: SingleChildScrollView(
              controller: _scrollController,
              physics: const BouncingScrollPhysics(),
              child: Text(
                widget.article.content,
                style: AppTheme.bodyLarge.copyWith(
                  height: 1.8,
                  color: AppTheme.textSecondary,
                ),
              ),
            ),
          ),
        ),
        
        const SizedBox(height: 16),
        
        // Reading tip
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: AppTheme.focusedColor.withAlpha(20),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                Icons.lightbulb_outline,
                color: AppTheme.focusedColor,
                size: 18,
              ),
              const SizedBox(width: 8),
              Text(
                'Read carefully and focus on the content',
                style: AppTheme.bodySmall.copyWith(
                  color: AppTheme.focusedColor,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
