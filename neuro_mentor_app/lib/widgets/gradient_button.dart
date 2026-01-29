import 'package:flutter/material.dart';
import '../config/theme.dart';

/// Gradient button with glow effect
class GradientButton extends StatefulWidget {
  final String text;
  final VoidCallback? onPressed;
  final LinearGradient gradient;
  final double height;
  final double borderRadius;
  final bool isLoading;
  final IconData? icon;
  
  const GradientButton({
    super.key,
    required this.text,
    this.onPressed,
    this.gradient = AppTheme.primaryGradient,
    this.height = 56,
    this.borderRadius = 16,
    this.isLoading = false,
    this.icon,
  });

  @override
  State<GradientButton> createState() => _GradientButtonState();
}

class _GradientButtonState extends State<GradientButton> {
  bool _isPressed = false;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTapDown: (_) => setState(() => _isPressed = true),
      onTapUp: (_) => setState(() => _isPressed = false),
      onTapCancel: () => setState(() => _isPressed = false),
      onTap: widget.isLoading ? null : widget.onPressed,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 150),
        height: widget.height,
        transform: _isPressed 
            ? (Matrix4.identity()..scale(0.97))
            : Matrix4.identity(),
        decoration: BoxDecoration(
          gradient: widget.onPressed != null && !widget.isLoading
              ? widget.gradient
              : LinearGradient(
                  colors: [Colors.grey.shade700, Colors.grey.shade800],
                ),
          borderRadius: BorderRadius.circular(widget.borderRadius),
          boxShadow: widget.onPressed != null && !widget.isLoading
              ? [
                  BoxShadow(
                    color: widget.gradient.colors.first.withAlpha(100),
                    blurRadius: _isPressed ? 15 : 20,
                    spreadRadius: _isPressed ? 0 : 2,
                  ),
                ]
              : null,
        ),
        child: Center(
          child: widget.isLoading
              ? const SizedBox(
                  width: 24,
                  height: 24,
                  child: CircularProgressIndicator(
                    color: Colors.white,
                    strokeWidth: 2.5,
                  ),
                )
              : Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    if (widget.icon != null) ...[
                      Icon(
                        widget.icon,
                        color: Colors.white,
                        size: 20,
                      ),
                      const SizedBox(width: 10),
                    ],
                    Text(
                      widget.text,
                      style: AppTheme.headingSmall.copyWith(
                        color: Colors.white,
                        letterSpacing: 1.5,
                      ),
                    ),
                  ],
                ),
        ),
      ),
    );
  }
}

/// Outlined button variant
class OutlinedGradientButton extends StatefulWidget {
  final String text;
  final VoidCallback? onPressed;
  final Color borderColor;
  final double height;
  final double borderRadius;
  
  const OutlinedGradientButton({
    super.key,
    required this.text,
    this.onPressed,
    this.borderColor = AppTheme.primaryStart,
    this.height = 56,
    this.borderRadius = 16,
  });

  @override
  State<OutlinedGradientButton> createState() => _OutlinedGradientButtonState();
}

class _OutlinedGradientButtonState extends State<OutlinedGradientButton> {
  bool _isHovering = false;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: (_) => setState(() => _isHovering = true),
      onExit: (_) => setState(() => _isHovering = false),
      child: GestureDetector(
        onTap: widget.onPressed,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          height: widget.height,
          decoration: BoxDecoration(
            color: _isHovering 
                ? widget.borderColor.withAlpha(30)
                : Colors.transparent,
            borderRadius: BorderRadius.circular(widget.borderRadius),
            border: Border.all(
              color: widget.borderColor,
              width: 2,
            ),
          ),
          child: Center(
            child: Text(
              widget.text,
              style: AppTheme.headingSmall.copyWith(
                color: widget.borderColor,
                letterSpacing: 1.5,
              ),
            ),
          ),
        ),
      ),
    );
  }
}
