import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:lucide_icons/lucide_icons.dart';
import '../../config/theme.dart';
import '../../config/routes.dart';
import '../../providers/auth_provider.dart';
import '../../utils/validators.dart';
import '../../widgets/gradient_button.dart';
import '../../widgets/glass_card.dart';

/// Registration screen with full form
class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _emailController = TextEditingController();
  final _studentIdController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  bool _obscurePassword = true;
  bool _obscureConfirmPassword = true;
  bool _acceptedTerms = false;
  int _passwordStrength = 0;

  @override
  void initState() {
    super.initState();
    _passwordController.addListener(_updatePasswordStrength);
  }

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    _studentIdController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  void _updatePasswordStrength() {
    setState(() {
      _passwordStrength = Validators.getPasswordStrength(
        _passwordController.text,
      );
    });
  }

  Future<void> _handleRegister() async {
    if (!_formKey.currentState!.validate()) return;
    
    if (!_acceptedTerms) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('Please accept the terms and conditions'),
          backgroundColor: AppTheme.stressedColor,
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      );
      return;
    }
    
    final authProvider = context.read<AuthProvider>();
    
    final success = await authProvider.register(
      name: _nameController.text.trim(),
      email: _emailController.text.trim(),
      password: _passwordController.text,
      studentId: _studentIdController.text.trim(),
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
                const SizedBox(height: 24),
                
                // Back button
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
                
                const SizedBox(height: 24),
                
                Text(
                  'Create Account',
                  style: AppTheme.headingLarge,
                ),
                
                const SizedBox(height: 8),
                
                Text(
                  'Start your attention-aware learning journey',
                  style: AppTheme.bodyRegular.copyWith(
                    color: AppTheme.textMuted,
                  ),
                ),
                
                const SizedBox(height: 32),
                
                // Registration form
                GlassCard(
                  padding: const EdgeInsets.all(24),
                  child: Form(
                    key: _formKey,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Name field
                        Text('FULL NAME', style: AppTheme.labelUppercase),
                        const SizedBox(height: 8),
                        TextFormField(
                          controller: _nameController,
                          style: AppTheme.bodyLarge.copyWith(
                            color: AppTheme.textPrimary,
                          ),
                          decoration: InputDecoration(
                            hintText: 'Enter your name',
                            prefixIcon: const Icon(
                              LucideIcons.user,
                              color: AppTheme.textMuted,
                              size: 20,
                            ),
                          ),
                          validator: Validators.validateName,
                        ),
                        
                        const SizedBox(height: 20),
                        
                        // Email field
                        Text('EMAIL', style: AppTheme.labelUppercase),
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
                        
                        // Student ID (optional)
                        Text(
                          'STUDENT ID (OPTIONAL)',
                          style: AppTheme.labelUppercase,
                        ),
                        const SizedBox(height: 8),
                        TextFormField(
                          controller: _studentIdController,
                          style: AppTheme.bodyLarge.copyWith(
                            color: AppTheme.textPrimary,
                          ),
                          decoration: InputDecoration(
                            hintText: 'Enter your student ID',
                            prefixIcon: const Icon(
                              LucideIcons.creditCard,
                              color: AppTheme.textMuted,
                              size: 20,
                            ),
                          ),
                          validator: Validators.validateStudentId,
                        ),
                        
                        const SizedBox(height: 20),
                        
                        // Password field
                        Text('PASSWORD', style: AppTheme.labelUppercase),
                        const SizedBox(height: 8),
                        TextFormField(
                          controller: _passwordController,
                          obscureText: _obscurePassword,
                          style: AppTheme.bodyLarge.copyWith(
                            color: AppTheme.textPrimary,
                          ),
                          decoration: InputDecoration(
                            hintText: 'Create a password',
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
                        
                        // Password strength indicator
                        const SizedBox(height: 8),
                        Row(
                          children: [
                            for (int i = 0; i < 4; i++) ...[
                              Expanded(
                                child: Container(
                                  height: 4,
                                  decoration: BoxDecoration(
                                    color: i < _passwordStrength
                                        ? _getStrengthColor(_passwordStrength)
                                        : Colors.white.withAlpha(20),
                                    borderRadius: BorderRadius.circular(2),
                                  ),
                                ),
                              ),
                              if (i < 3) const SizedBox(width: 4),
                            ],
                            const SizedBox(width: 8),
                            Text(
                              Validators.getPasswordStrengthLabel(_passwordStrength),
                              style: AppTheme.bodySmall.copyWith(
                                color: _getStrengthColor(_passwordStrength),
                              ),
                            ),
                          ],
                        ),
                        
                        const SizedBox(height: 20),
                        
                        // Confirm password
                        Text('CONFIRM PASSWORD', style: AppTheme.labelUppercase),
                        const SizedBox(height: 8),
                        TextFormField(
                          controller: _confirmPasswordController,
                          obscureText: _obscureConfirmPassword,
                          style: AppTheme.bodyLarge.copyWith(
                            color: AppTheme.textPrimary,
                          ),
                          decoration: InputDecoration(
                            hintText: 'Confirm your password',
                            prefixIcon: const Icon(
                              LucideIcons.keyRound,
                              color: AppTheme.textMuted,
                              size: 20,
                            ),
                            suffixIcon: GestureDetector(
                              onTap: () {
                                setState(() {
                                  _obscureConfirmPassword = !_obscureConfirmPassword;
                                });
                              },
                              child: Icon(
                                _obscureConfirmPassword 
                                    ? LucideIcons.eyeOff 
                                    : LucideIcons.eye,
                                color: AppTheme.textMuted,
                                size: 20,
                              ),
                            ),
                          ),
                          validator: (value) => Validators.validateConfirmPassword(
                            value,
                            _passwordController.text,
                          ),
                        ),
                        
                        const SizedBox(height: 20),
                        
                        // Terms checkbox
                        Row(
                          children: [
                            Checkbox(
                              value: _acceptedTerms,
                              onChanged: (value) {
                                setState(() {
                                  _acceptedTerms = value ?? false;
                                });
                              },
                            ),
                            Expanded(
                              child: GestureDetector(
                                onTap: () {
                                  setState(() {
                                    _acceptedTerms = !_acceptedTerms;
                                  });
                                },
                                child: RichText(
                                  text: TextSpan(
                                    style: AppTheme.bodySmall,
                                    children: [
                                      const TextSpan(text: 'I agree to the '),
                                      TextSpan(
                                        text: 'Terms of Service',
                                        style: AppTheme.bodySmall.copyWith(
                                          color: AppTheme.primaryStart,
                                        ),
                                      ),
                                      const TextSpan(text: ' and '),
                                      TextSpan(
                                        text: 'Privacy Policy',
                                        style: AppTheme.bodySmall.copyWith(
                                          color: AppTheme.primaryStart,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                            ),
                          ],
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
                        
                        // Register button
                        Consumer<AuthProvider>(
                          builder: (context, auth, _) {
                            return SizedBox(
                              width: double.infinity,
                              child: GradientButton(
                                text: 'Create Account',
                                isLoading: auth.isLoading,
                                onPressed: _handleRegister,
                              ),
                            );
                          },
                        ),
                      ],
                    ),
                  ),
                ),
                
                const SizedBox(height: 24),
                
                // Sign in link
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      'Already have an account? ',
                      style: AppTheme.bodyRegular.copyWith(
                        color: AppTheme.textMuted,
                      ),
                    ),
                    GestureDetector(
                      onTap: () {
                        Navigator.pushReplacementNamed(context, Routes.login);
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
                
                const SizedBox(height: 32),
              ],
            ),
          ),
        ),
      ),
    );
  }
  
  Color _getStrengthColor(int strength) {
    switch (strength) {
      case 1:
        return AppTheme.stressedColor;
      case 2:
        return AppTheme.unfocusedColor;
      case 3:
        return AppTheme.secondaryStart;
      case 4:
        return AppTheme.focusedColor;
      default:
        return AppTheme.textMuted;
    }
  }
}
