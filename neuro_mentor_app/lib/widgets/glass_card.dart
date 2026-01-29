import 'package:flutter/material.dart';
import '../config/theme.dart';

/// Glassmorphism card widget
/// Rounded corners, semi-transparent background, subtle border
class GlassCard extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry? padding;
  final double borderRadius;
  final Color? glowColor;
  final VoidCallback? onTap;
  
  const GlassCard({
    super.key,
    required this.child,
    this.padding,
    this.borderRadius = 24.0,
    this.glowColor,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: padding ?? const EdgeInsets.all(24),
        decoration: BoxDecoration(
          color: AppTheme.cardBackground,
          borderRadius: BorderRadius.circular(borderRadius),
          border: Border.all(
            color: AppTheme.cardBorder,
            width: 1,
          ),
          boxShadow: glowColor != null
              ? AppTheme.glowShadow(glowColor!)
              : null,
        ),
        child: child,
      ),
    );
  }
}

/// Animated glass card with hover/tap effects
class AnimatedGlassCard extends StatefulWidget {
  final Widget child;
  final EdgeInsetsGeometry? padding;
  final double borderRadius;
  final Color glowColor;
  final VoidCallback? onTap;
  
  const AnimatedGlassCard({
    super.key,
    required this.child,
    this.padding,
    this.borderRadius = 24.0,
    this.glowColor = AppTheme.primaryStart,
    this.onTap,
  });

  @override
  State<AnimatedGlassCard> createState() => _AnimatedGlassCardState();
}

class _AnimatedGlassCardState extends State<AnimatedGlassCard> {
  bool _isHovering = false;
  bool _isTapped = false;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: (_) => setState(() => _isHovering = true),
      onExit: (_) => setState(() => _isHovering = false),
      child: GestureDetector(
        onTapDown: (_) => setState(() => _isTapped = true),
        onTapUp: (_) => setState(() => _isTapped = false),
        onTapCancel: () => setState(() => _isTapped = false),
        onTap: widget.onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          curve: Curves.easeOutCubic,
          padding: widget.padding ?? const EdgeInsets.all(24),
          transform: _isTapped 
              ? (Matrix4.identity()..scale(0.98))
              : Matrix4.identity(),
          decoration: BoxDecoration(
            color: _isHovering 
                ? AppTheme.cardBackground.withAlpha(230)
                : AppTheme.cardBackground,
            borderRadius: BorderRadius.circular(widget.borderRadius),
            border: Border.all(
              color: _isHovering 
                  ? widget.glowColor.withAlpha(100)
                  : AppTheme.cardBorder,
              width: _isHovering ? 1.5 : 1,
            ),
            boxShadow: _isHovering
                ? AppTheme.glowShadow(widget.glowColor, blur: 30)
                : null,
          ),
          child: widget.child,
        ),
      ),
    );
  }
}
