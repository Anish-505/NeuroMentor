import 'dart:async';
import 'package:flutter/material.dart';
import '../../config/theme.dart';

/// Listing challenge widget for stress calibration
/// User must list items in a category under time pressure
class ListingWidget extends StatefulWidget {
  final String category;
  final Function(int itemCount)? onSubmit;
  
  const ListingWidget({
    super.key,
    required this.category,
    this.onSubmit,
  });

  @override
  State<ListingWidget> createState() => _ListingWidgetState();
}

class _ListingWidgetState extends State<ListingWidget> {
  final _controller = TextEditingController();
  final _focusNode = FocusNode();
  final List<String> _items = [];
  bool _submitted = false;

  @override
  void dispose() {
    _controller.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  void _addItem() {
    final text = _controller.text.trim();
    if (text.isNotEmpty && !_items.contains(text.toLowerCase())) {
      setState(() {
        _items.add(text);
      });
      _controller.clear();
      _focusNode.requestFocus();
    }
  }

  void _removeItem(int index) {
    setState(() {
      _items.removeAt(index);
    });
  }

  void _submit() {
    setState(() {
      _submitted = true;
    });
    widget.onSubmit?.call(_items.length);
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        // Challenge prompt
        Container(
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [
                AppTheme.stressedColor.withAlpha(40),
                AppTheme.stressedColor.withAlpha(20),
              ],
            ),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: AppTheme.stressedColor.withAlpha(60)),
          ),
          child: Column(
            children: [
              Text(
                'LIST AS MANY AS YOU CAN',
                style: AppTheme.labelUppercase.copyWith(
                  color: AppTheme.stressedColor,
                  letterSpacing: 2,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                widget.category,
                style: AppTheme.headingLarge.copyWith(
                  color: Colors.white,
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
        
        const SizedBox(height: 24),
        
        // Input field
        if (!_submitted)
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              SizedBox(
                width: 200,
                child: TextField(
                  controller: _controller,
                  focusNode: _focusNode,
                  textCapitalization: TextCapitalization.words,
                  style: AppTheme.bodyLarge,
                  decoration: InputDecoration(
                    hintText: 'Type an item...',
                    hintStyle: AppTheme.bodyRegular.copyWith(
                      color: AppTheme.textMuted,
                    ),
                    filled: true,
                    fillColor: const Color(0xFF0F1420),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: const BorderSide(color: AppTheme.cardBorder),
                    ),
                    focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: const BorderSide(
                        color: AppTheme.primaryStart,
                        width: 2,
                      ),
                    ),
                    contentPadding: const EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 14,
                    ),
                  ),
                  onSubmitted: (_) => _addItem(),
                ),
              ),
              const SizedBox(width: 12),
              GestureDetector(
                onTap: _addItem,
                child: Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    gradient: AppTheme.primaryGradient,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(
                    Icons.add,
                    color: Colors.white,
                    size: 24,
                  ),
                ),
              ),
            ],
          ),
        
        const SizedBox(height: 24),
        
        // Items list
        Container(
          width: double.infinity,
          constraints: const BoxConstraints(
            maxHeight: 200,
          ),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: AppTheme.cardBackground,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: AppTheme.cardBorder),
          ),
          child: _items.isEmpty
              ? Center(
                  child: Text(
                    'No items yet',
                    style: AppTheme.bodyRegular.copyWith(
                      color: AppTheme.textMuted,
                    ),
                  ),
                )
              : SingleChildScrollView(
                  child: Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: List.generate(_items.length, (index) {
                      return Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 8,
                        ),
                        decoration: BoxDecoration(
                          color: AppTheme.focusedColor.withAlpha(30),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(
                            color: AppTheme.focusedColor.withAlpha(60),
                          ),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Text(
                              '${index + 1}. ${_items[index]}',
                              style: AppTheme.bodySmall.copyWith(
                                color: Colors.white,
                              ),
                            ),
                            if (!_submitted) ...[
                              const SizedBox(width: 8),
                              GestureDetector(
                                onTap: () => _removeItem(index),
                                child: Icon(
                                  Icons.close,
                                  size: 16,
                                  color: AppTheme.textMuted,
                                ),
                              ),
                            ],
                          ],
                        ),
                      );
                    }),
                  ),
                ),
        ),
        
        const SizedBox(height: 16),
        
        // Count display
        Text(
          '${_items.length} items listed',
          style: AppTheme.headingSmall.copyWith(
            color: AppTheme.focusedColor,
          ),
        ),
      ],
    );
  }
}
