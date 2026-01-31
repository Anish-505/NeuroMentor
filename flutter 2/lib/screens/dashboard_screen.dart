import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../config/theme.dart';
import '../config/routes.dart';
import '../providers/auth_provider.dart';

/// Dashboard with calibration and monitoring options
class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();
    final user = auth.user;

    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(gradient: AppTheme.backgroundGradient),
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header
                Row(
                  children: [
                    Container(
                      width: 50,
                      height: 50,
                      decoration: BoxDecoration(
                        gradient: AppTheme.primaryGradient,
                        shape: BoxShape.circle,
                      ),
                      child: Center(
                        child: Text(
                          user?.name.substring(0, 1).toUpperCase() ?? 'U',
                          style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                        ),
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Hello, ${user?.name ?? 'User'}!',
                              style: Theme.of(context).textTheme.headlineMedium),
                          Text('Ready to train?', style: Theme.of(context).textTheme.bodyMedium),
                        ],
                      ),
                    ),
                    IconButton(
                      onPressed: () async {
                        await auth.logout();
                        if (context.mounted) {
                          Navigator.pushReplacementNamed(context, Routes.landing);
                        }
                      },
                      icon: const Icon(Icons.logout),
                    ),
                  ],
                ),
                const SizedBox(height: 48),
                Text('Choose an Option', style: Theme.of(context).textTheme.headlineMedium),
                const SizedBox(height: 24),
                // Calibration card
                _DashboardCard(
                  icon: Icons.adjust,
                  title: 'Model Calibration',
                  description: 'Complete 20-minute training to create your personal attention baseline',
                  gradient: AppTheme.primaryGradient,
                  onTap: () => _showStateSelector(context),
                ),
                const SizedBox(height: 16),
                // Monitoring card
                _DashboardCard(
                  icon: Icons.show_chart,
                  title: 'Live Monitoring',
                  description: 'Real-time EEG tracking with focus and stress visualization',
                  gradient: AppTheme.secondaryGradient,
                  onTap: () => Navigator.pushNamed(context, Routes.monitoring),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  void _showStateSelector(BuildContext context) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (ctx) => Container(
        decoration: BoxDecoration(
          color: AppTheme.bgDark,
          borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
        ),
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('Select Training State', style: Theme.of(context).textTheme.headlineMedium),
            const SizedBox(height: 24),
            _StateOption(
              title: 'Calm',
              color: Colors.blue,
              onTap: () {
                Navigator.pop(ctx);
                Navigator.pushNamed(context, Routes.calibration, arguments: 'Calm');
              },
            ),
            const SizedBox(height: 12),
            _StateOption(
              title: 'Stressed',
              color: Colors.red,
              onTap: () {
                Navigator.pop(ctx);
                Navigator.pushNamed(context, Routes.calibration, arguments: 'Stressed');
              },
            ),
            const SizedBox(height: 12),
            _StateOption(
              title: 'Focused',
              color: Colors.green,
              onTap: () {
                Navigator.pop(ctx);
                Navigator.pushNamed(context, Routes.calibration, arguments: 'Focused');
              },
            ),
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }
}

class _DashboardCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String description;
  final Gradient gradient;
  final VoidCallback onTap;

  const _DashboardCard({
    required this.icon,
    required this.title,
    required this.description,
    required this.gradient,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: glassDecoration(),
        child: Row(
          children: [
            Container(
              width: 60,
              height: 60,
              decoration: BoxDecoration(
                gradient: gradient,
                borderRadius: BorderRadius.circular(16),
              ),
              child: Icon(icon, color: Colors.white, size: 30),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 4),
                  Text(description, style: TextStyle(color: Colors.white.withOpacity(0.7), fontSize: 13)),
                ],
              ),
            ),
            const Icon(Icons.chevron_right),
          ],
        ),
      ),
    );
  }
}

class _StateOption extends StatelessWidget {
  final String title;
  final Color color;
  final VoidCallback onTap;

  const _StateOption({required this.title, required this.color, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: color.withOpacity(0.2),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: color.withOpacity(0.5)),
        ),
        child: Row(
          children: [
            Container(
              width: 12,
              height: 12,
              decoration: BoxDecoration(color: color, shape: BoxShape.circle),
            ),
            const SizedBox(width: 12),
            Text(title, style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600, color: color)),
            const Spacer(),
            Icon(Icons.arrow_forward, color: color),
          ],
        ),
      ),
    );
  }
}
