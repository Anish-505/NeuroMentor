import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:lucide_icons/lucide_icons.dart';
import '../../config/theme.dart';
import '../../config/routes.dart';
import '../../providers/auth_provider.dart';
import '../../utils/validators.dart';
import '../../widgets/gradient_button.dart';
import '../../widgets/glass_card.dart';

/// Login screen with email/password form
class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _obscurePassword = true;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _handleLogin() async {
    if (!_formKey.currentState!.validate()) return;
    
    final authProvider = context.read<AuthProvider>();
    
    final success = await authProvider.login(
      _emailController.text.trim(),
      _passwordController.text,
    );
    
    if (success && mounted) {
      Navigator.pushReplacementNamed(context, Routes.dashboard);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: AppTheme.backgroundGradient,
        ),
        child: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 24),
            child: Column(
              children: [
                const SizedBox(height: 48),
                
                // Back button and title
                Row(
                  children: [
                    GestureDetector(
                      onTap: () => Navigator.pop(context),
                      child: Container(
                        width: 44,
                        height: 44,
                        decoration: BoxDecoration(
                          color: Colors.white.withAlpha(10),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                            color: Colors.white.withAlpha(20),
                          ),
                        ),
                        child: const Icon(
                          LucideIcons.arrowLeft,
                          color: AppTheme.textSecondary,
                          size: 20,
                        ),
                      ),
                    ),
                    const Spacer(),
                  ],
                ),
                
                const SizedBox(height: 32),
                
                // Logo
                Container(
                  width: 72,
                  height: 72,
                  decoration: BoxDecoration(
                    gradient: AppTheme.primaryGradient,
                    shape: BoxShape.circle,
                    boxShadow: [
                      BoxShadow(
                        color: AppTheme.primaryStart.withAlpha(80),
                        blurRadius: 24,
                      ),
                    ],
                  ),
                  child: const Icon(
                    LucideIcons.brain,
                    color: Colors.white,
                    size: 36,
                  ),
                ),
                
                const SizedBox(height: 24),
                
                Text(
                  'Welcome Back',
                  style: AppTheme.headingLarge,
                ),
                
                const SizedBox(height: 8),
                
                Text(
                  'Sign in to continue your learning journey',
                  style: AppTheme.bodyRegular.copyWith(
                    color: AppTheme.textMuted,
                  ),
                ),
                
                const SizedBox(height: 40),
                
                // Login form
                GlassCard(
                  padding: const EdgeInsets.all(24),
                  child: Form(
                    key: _formKey,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Email field
                        Text(
                          'EMAIL',
                          style: AppTheme.labelUppercase,
                        ),
                        const SizedBox(height: 8),
                        TextFormField(
                          controller: _emailController,
                          keyboardType: TextInputType.emailAddress,
                          style: AppTheme.bodyLarge.copyWith(
                            color: AppTheme.textPrimary,
                          ),
                          decoration: InputDecoration(
                            hintText: 'Enter your email',
                            prefixIcon: const Icon(
                              LucideIcons.mail,
                              color: AppTheme.textMuted,
                              size: 20,
                            ),
                          ),
                          validator: Validators.validateEmail,
                        ),
                        
                        const SizedBox(height: 20),
                        
                        // Password field
                        Text(
                          'PASSWORD',
                          style: AppTheme.labelUppercase,
                        ),
                        const SizedBox(height: 8),
                        TextFormField(
                          controller: _passwordController,
                          obscureText: _obscurePassword,
                          style: AppTheme.bodyLarge.copyWith(
                            color: AppTheme.textPrimary,
                          ),
                          decoration: InputDecoration(
                            hintText: 'Enter your password',
                            prefixIcon: const Icon(
                              LucideIcons.lock,
                              color: AppTheme.textMuted,
                              size: 20,
                            ),
                            suffixIcon: GestureDetector(
                              onTap: () {
                                setState(() {
                                  _obscurePassword = !_obscurePassword;
                                });
                              },
                              child: Icon(
                                _obscurePassword 
                                    ? LucideIcons.eyeOff 
                                    : LucideIcons.eye,
                                color: AppTheme.textMuted,
                                size: 20,
                              ),
                            ),
                          ),
                          validator: Validators.validatePassword,
                        ),
                        
                        const SizedBox(height: 12),
                        
                        // Forgot password
                        Align(
                          alignment: Alignment.centerRight,
                          child: GestureDetector(
                            onTap: () {
                              // TODO: Implement forgot password
                            },
                            child: Text(
                              'Forgot Password?',
                              style: AppTheme.bodySmall.copyWith(
                                color: AppTheme.primaryStart,
                              ),
                            ),
                          ),
                        ),
                        
                        const SizedBox(height: 24),
                        
                        // Error message
                        Consumer<AuthProvider>(
                          builder: (context, auth, _) {
                            if (auth.errorMessage != null) {
                              return Container(
                                padding: const EdgeInsets.all(12),
                                margin: const EdgeInsets.only(bottom: 16),
                                decoration: BoxDecoration(
                                  color: AppTheme.stressedColor.withAlpha(30),
                                  borderRadius: BorderRadius.circular(12),
                                  border: Border.all(
                                    color: AppTheme.stressedColor.withAlpha(80),
                                  ),
                                ),
                                child: Row(
                                  children: [
                                    const Icon(
                                      LucideIcons.alertCircle,
                                      color: AppTheme.stressedColor,
                                      size: 18,
                                    ),
                                    const SizedBox(width: 8),
                                    Expanded(
                                      child: Text(
                                        auth.errorMessage!,
                                        style: AppTheme.bodySmall.copyWith(
                                          color: AppTheme.stressedColor,
                                        ),
                                      ),
                                    ),
                                  ],
                                ),
                              );
                            }
                            return const SizedBox.shrink();
                          },
                        ),
                        
                        // Login button
                        Consumer<AuthProvider>(
                          builder: (context, auth, _) {
                            return SizedBox(
                              width: double.infinity,
                              child: GradientButton(
                                text: 'Sign In',
                                isLoading: auth.isLoading,
                                onPressed: _handleLogin,
                              ),
                            );
                          },
                        ),
                      ],
                    ),
                  ),
                ),
                
                const SizedBox(height: 24),
                
                // Sign up link
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      "Don't have an account? ",
                      style: AppTheme.bodyRegular.copyWith(
                        color: AppTheme.textMuted,
                      ),
                    ),
                    GestureDetector(
                      onTap: () {
                        Navigator.pushReplacementNamed(context, Routes.register);
                      },
                      child: Text(
                        'Create Account',
                        style: AppTheme.bodyRegular.copyWith(
                          color: AppTheme.primaryStart,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ),
                
                const SizedBox(height: 48),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
