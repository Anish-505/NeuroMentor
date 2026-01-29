import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:lucide_icons/lucide_icons.dart';
import '../config/theme.dart';
import '../config/routes.dart';
import '../providers/auth_provider.dart';
import '../providers/user_data_provider.dart';
import '../widgets/dashboard_card.dart';
import '../widgets/glass_card.dart';

/// Main dashboard screen after login
/// Displays user info and navigation options
class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  @override
  void initState() {
    super.initState();
    _loadUserData();
  }

  Future<void> _loadUserData() async {
    final auth = context.read<AuthProvider>();
    final userData = context.read<UserDataProvider>();
    
    if (auth.currentUser != null) {
      await userData.loadCalibrationData(auth.currentUser!.uid);
      await userData.loadSessions(auth.currentUser!.uid);
    }
  }

  Future<void> _handleLogout() async {
    final auth = context.read<AuthProvider>();
    await auth.logout();
    
    if (mounted) {
      Navigator.pushReplacementNamed(context, Routes.landing);
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
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SizedBox(height: 24),
                
                // Header with user info and logout
                Consumer<AuthProvider>(
                  builder: (context, auth, _) {
                    final user = auth.currentUser;
                    return Row(
                      children: [
                        // Avatar
                        Container(
                          width: 52,
                          height: 52,
                          decoration: BoxDecoration(
                            gradient: AppTheme.primaryGradient,
                            borderRadius: BorderRadius.circular(16),
                          ),
                          child: Center(
                            child: Text(
                              user?.name.isNotEmpty == true 
                                  ? user!.name[0].toUpperCase()
                                  : 'U',
                              style: AppTheme.headingMedium.copyWith(
                                color: Colors.white,
                              ),
                            ),
                          ),
                        ),
                        
                        const SizedBox(width: 16),
                        
                        // Name and greeting
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                _getGreeting(),
                                style: AppTheme.bodySmall.copyWith(
                                  color: AppTheme.textMuted,
                                ),
                              ),
                              Text(
                                user?.name ?? 'User',
                                style: AppTheme.headingSmall,
                              ),
                            ],
                          ),
                        ),
                        
                        // Logout button
                        GestureDetector(
                          onTap: _handleLogout,
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
                              LucideIcons.logOut,
                              color: AppTheme.textMuted,
                              size: 20,
                            ),
                          ),
                        ),
                      ],
                    );
                  },
                ),
                
                const SizedBox(height: 32),
                
                // Calibration status card
                Consumer<UserDataProvider>(
                  builder: (context, userData, _) {
                    final hasCalibration = userData.hasPersonalCalibration;
                    return GlassCard(
                      padding: const EdgeInsets.all(20),
                      glowColor: hasCalibration 
                          ? AppTheme.focusedColor 
                          : AppTheme.unfocusedColor,
                      child: Row(
                        children: [
                          Container(
                            width: 48,
                            height: 48,
                            decoration: BoxDecoration(
                              color: (hasCalibration 
                                  ? AppTheme.focusedColor 
                                  : AppTheme.unfocusedColor
                              ).withAlpha(40),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Icon(
                              hasCalibration 
                                  ? LucideIcons.checkCircle 
                                  : LucideIcons.alertCircle,
                              color: hasCalibration 
                                  ? AppTheme.focusedColor 
                                  : AppTheme.unfocusedColor,
                              size: 24,
                            ),
                          ),
                          const SizedBox(width: 16),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  hasCalibration 
                                      ? 'Calibration Complete' 
                                      : 'Calibration Needed',
                                  style: AppTheme.bodyLarge.copyWith(
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                                Text(
                                  hasCalibration 
                                      ? 'Your personal baseline is ready for monitoring'
                                      : 'Complete calibration for personalized tracking',
                                  style: AppTheme.bodySmall.copyWith(
                                    color: AppTheme.textMuted,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    );
                  },
                ),
                
                const SizedBox(height: 32),
                
                // Section title
                Text(
                  'WHAT WOULD YOU LIKE TO DO?',
                  style: AppTheme.labelUppercase,
                ),
                
                const SizedBox(height: 16),
                
                // Calibration option
                DashboardCard(
                  title: 'Calibration',
                  description: 'Complete breathing, stress, and focus exercises to establish your personal baseline',
                  icon: LucideIcons.sliders,
                  gradient: AppTheme.secondaryGradient,
                  badge: 'RECOMMENDED',
                  onTap: () {
                    Navigator.pushNamed(context, Routes.calibration);
                  },
                ),
                
                const SizedBox(height: 16),
                
                // Live Monitoring option
                DashboardCard(
                  title: 'Live Monitoring',
                  description: 'Start a real-time attention tracking session with EEG visualization',
                  icon: LucideIcons.activity,
                  gradient: AppTheme.accentGradient,
                  onTap: () {
                    Navigator.pushNamed(context, Routes.monitoring);
                  },
                ),
                
                const SizedBox(height: 32),
                
                // Session history preview
                Consumer<UserDataProvider>(
                  builder: (context, userData, _) {
                    final sessions = userData.sessions.take(3).toList();
                    
                    if (sessions.isEmpty) {
                      return const SizedBox.shrink();
                    }
                    
                    return Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              'RECENT SESSIONS',
                              style: AppTheme.labelUppercase,
                            ),
                            Text(
                              '${userData.sessions.length} total',
                              style: AppTheme.bodySmall.copyWith(
                                color: AppTheme.primaryStart,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        
                        ...sessions.map((session) => Container(
                          margin: const EdgeInsets.only(bottom: 8),
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: AppTheme.cardBackground,
                            borderRadius: BorderRadius.circular(16),
                            border: Border.all(color: AppTheme.cardBorder),
                          ),
                          child: Row(
                            children: [
                              Container(
                                width: 40,
                                height: 40,
                                decoration: BoxDecoration(
                                  color: AppTheme.focusedColor.withAlpha(30),
                                  borderRadius: BorderRadius.circular(10),
                                ),
                                child: const Icon(
                                  LucideIcons.clock,
                                  color: AppTheme.focusedColor,
                                  size: 18,
                                ),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      _formatDuration(session.duration),
                                      style: AppTheme.bodyLarge.copyWith(
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                    Text(
                                      _formatDate(session.startTime),
                                      style: AppTheme.bodySmall.copyWith(
                                        color: AppTheme.textMuted,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                              Text(
                                '${(session.averageFocusLevel * 100).toInt()}%',
                                style: AppTheme.headingSmall.copyWith(
                                  color: AppTheme.focusedColor,
                                ),
                              ),
                            ],
                          ),
                        )),
                      ],
                    );
                  },
                ),
                
                const SizedBox(height: 32),
              ],
            ),
          ),
        ),
      ),
    );
  }
  
  String _getGreeting() {
    final hour = DateTime.now().hour;
    if (hour < 12) return 'Good morning,';
    if (hour < 17) return 'Good afternoon,';
    return 'Good evening,';
  }
  
  String _formatDuration(Duration duration) {
    final minutes = duration.inMinutes;
    if (minutes < 60) return '$minutes min session';
    final hours = minutes ~/ 60;
    final mins = minutes % 60;
    return '$hours h ${mins} min session';
  }
  
  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final diff = now.difference(date);
    
    if (diff.inDays == 0) return 'Today';
    if (diff.inDays == 1) return 'Yesterday';
    if (diff.inDays < 7) return '${diff.inDays} days ago';
    return '${date.day}/${date.month}/${date.year}';
  }
}
