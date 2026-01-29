import 'package:flutter/material.dart';
import 'package:lucide_icons/lucide_icons.dart';
import '../../config/theme.dart';
import '../../config/routes.dart';
import '../../widgets/gradient_button.dart';

/// Landing/Welcome screen
/// Displays NeuroMentor branding and "Get Started" button
class LandingScreen extends StatefulWidget {
  const LandingScreen({super.key});

  @override
  State<LandingScreen> createState() => _LandingScreenState();
}

class _LandingScreenState extends State<LandingScreen> 
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 1200),
      vsync: this,
    );
    
    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: const Interval(0.0, 0.6, curve: Curves.easeOut),
    ));
    
    _slideAnimation = Tween<Offset>(
      begin: const Offset(0, 0.3),
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: const Interval(0.2, 0.8, curve: Curves.easeOutCubic),
    ));
    
    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: AppTheme.backgroundGradient,
        ),
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 32),
            child: Column(
              children: [
                const Spacer(flex: 2),
                
                // Animated logo and branding
                FadeTransition(
                  opacity: _fadeAnimation,
                  child: SlideTransition(
                    position: _slideAnimation,
                    child: Column(
                      children: [
                        // Logo container with glow
                        Container(
                          width: 120,
                          height: 120,
                          decoration: BoxDecoration(
                            gradient: AppTheme.primaryGradient,
                            shape: BoxShape.circle,
                            boxShadow: [
                              BoxShadow(
                                color: AppTheme.primaryStart.withAlpha(100),
                                blurRadius: 40,
                                spreadRadius: 8,
                              ),
                            ],
                          ),
                          child: const Icon(
                            LucideIcons.brain,
                            color: Colors.white,
                            size: 56,
                          ),
                        ),
                        
                        const SizedBox(height: 32),
                        
                        // App name
                        ShaderMask(
                          shaderCallback: (bounds) => const LinearGradient(
                            colors: [
                              AppTheme.primaryStart,
                              AppTheme.primaryEnd,
                            ],
                          ).createShader(bounds),
                          child: Text(
                            'NeuroMentor',
                            style: AppTheme.headingXL.copyWith(
                              fontSize: 40,
                              color: Colors.white,
                            ),
                          ),
                        ),
                        
                        const SizedBox(height: 12),
                        
                        // Tagline
                        Text(
                          'Attention-Aware Learning Assistant',
                          style: AppTheme.bodyLarge.copyWith(
                            color: AppTheme.textMuted,
                            letterSpacing: 0.5,
                          ),
                          textAlign: TextAlign.center,
                        ),
                        
                        const SizedBox(height: 48),
                        
                        // Feature highlights
                        _buildFeatureRow(
                          LucideIcons.activity,
                          'Real-time EEG Monitoring',
                        ),
                        const SizedBox(height: 16),
                        _buildFeatureRow(
                          LucideIcons.target,
                          'Personalized Attention Calibration',
                        ),
                        const SizedBox(height: 16),
                        _buildFeatureRow(
                          LucideIcons.trendingUp,
                          'Focus & Stress Analytics',
                        ),
                      ],
                    ),
                  ),
                ),
                
                const Spacer(flex: 3),
                
                // Buttons
                FadeTransition(
                  opacity: _fadeAnimation,
                  child: Column(
                    children: [
                      // Get Started button
                      SizedBox(
                        width: double.infinity,
                        child: GradientButton(
                          text: 'Get Started',
                          icon: LucideIcons.arrowRight,
                          onPressed: () {
                            Navigator.pushNamed(context, Routes.login);
                          },
                        ),
                      ),
                      
                      const SizedBox(height: 24),
                      
                      // Already have account
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            "Already have an account? ",
                            style: AppTheme.bodyRegular.copyWith(
                              color: AppTheme.textMuted,
                            ),
                          ),
                          GestureDetector(
                            onTap: () {
                              Navigator.pushNamed(context, Routes.login);
                            },
                            child: Text(
                              'Sign In',
                              style: AppTheme.bodyRegular.copyWith(
                                color: AppTheme.primaryStart,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                
                const SizedBox(height: 48),
              ],
            ),
          ),
        ),
      ),
    );
  }
  
  Widget _buildFeatureRow(IconData icon, String text) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Container(
          width: 32,
          height: 32,
          decoration: BoxDecoration(
            color: AppTheme.primaryStart.withAlpha(30),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(
            icon,
            color: AppTheme.primaryStart,
            size: 16,
          ),
        ),
        const SizedBox(width: 12),
        Text(
          text,
          style: AppTheme.bodyRegular.copyWith(
            color: AppTheme.textSecondary,
          ),
        ),
      ],
    );
  }
}
