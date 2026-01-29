import 'dart:async';
import 'dart:math';
import 'package:flutter/material.dart';
import 'package:lucide_icons/lucide_icons.dart';
import '../../config/theme.dart';
import '../../config/calibration_config.dart';
import '../../config/technical_articles.dart';
import '../../services/wikipedia_service.dart';
import '../../widgets/glass_card.dart';
import '../../widgets/calibration/breathing_widget.dart';
import '../../widgets/calibration/math_widget.dart';
import '../../widgets/calibration/stroop_widget.dart';
import '../../widgets/calibration/listing_widget.dart';
import '../../widgets/calibration/reading_widget.dart';
import '../../widgets/calibration/recall_widget.dart';

/// Main calibration session screen
/// Manages the timer, phases, and displays appropriate task widgets
class CalibrationSessionScreen extends StatefulWidget {
  final String stateName;
  
  const CalibrationSessionScreen({
    super.key,
    required this.stateName,
  });

  @override
  State<CalibrationSessionScreen> createState() => _CalibrationSessionScreenState();
}

class _CalibrationSessionScreenState extends State<CalibrationSessionScreen> {
  late StateConfig _stateConfig;
  int _currentPhaseIndex = 0;
  int _phaseSecondsRemaining = 0;
  int _totalElapsedSeconds = 0;
  Timer? _timer;
  bool _isRunning = false;
  bool _isPaused = false;
  bool _isCompleted = false;
  
  // For reading/recall phases
  Article? _currentArticle;
  List<String> _selectedKeywords = [];
  
  // For listing phase
  String _listingCategory = '';
  
  // Current phase scores
  int _phaseCorrect = 0;
  int _phaseTotal = 0;

  @override
  void initState() {
    super.initState();
    _stateConfig = stateConfig[widget.stateName]!;
    _phaseSecondsRemaining = _stateConfig.phases[0].durationSeconds;
    _preparePhase();
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  PhaseConfig get _currentPhase => _stateConfig.phases[_currentPhaseIndex];

  void _preparePhase() async {
    final phase = _currentPhase;
    
    // Reset scores
    _phaseCorrect = 0;
    _phaseTotal = 0;
    
    // Prepare phase-specific content
    if (phase.mode == PhaseMode.reading) {
      // Fetch article for reading phase
      _currentArticle = await WikipediaService.fetchRandomArticle();
      // Select random keywords
      final words = _currentArticle!.content
          .split(RegExp(r'\s+'))
          .where((w) => w.length > 5)
          .toList();
      words.shuffle();
      _selectedKeywords = words.take(3).toList();
    } else if (phase.mode == PhaseMode.recall) {
      // Use keywords from previous reading phase
      // Already set from reading phase
    } else if (phase.mode == PhaseMode.listing) {
      // Random category for listing
      _listingCategory = phase.listingCategories?[
        Random().nextInt(phase.listingCategories!.length)
      ] ?? 'Things that are blue';
    }
    
    setState(() {});
  }

  void _startSession() {
    setState(() {
      _isRunning = true;
      _isPaused = false;
    });
    
    _timer = Timer.periodic(const Duration(seconds: 1), (_) {
      if (_isPaused) return;
      
      setState(() {
        _phaseSecondsRemaining--;
        _totalElapsedSeconds++;
        
        if (_phaseSecondsRemaining <= 0) {
          _advancePhase();
        }
      });
    });
  }

  void _pauseSession() {
    setState(() {
      _isPaused = true;
    });
  }

  void _resumeSession() {
    setState(() {
      _isPaused = false;
    });
  }

  void _advancePhase() {
    if (_currentPhaseIndex < _stateConfig.phases.length - 1) {
      _currentPhaseIndex++;
      _phaseSecondsRemaining = _currentPhase.durationSeconds;
      _preparePhase();
    } else {
      _completeSession();
    }
  }

  void _completeSession() {
    _timer?.cancel();
    setState(() {
      _isRunning = false;
      _isCompleted = true;
    });
  }

  void _exitSession() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: AppTheme.cardBackground,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(24),
        ),
        title: Text(
          'Exit Calibration?',
          style: AppTheme.headingMedium,
        ),
        content: Text(
          'Your progress will be lost. Are you sure you want to exit?',
          style: AppTheme.bodyRegular.copyWith(
            color: AppTheme.textSecondary,
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(
              'Cancel',
              style: AppTheme.bodyRegular.copyWith(
                color: AppTheme.textMuted,
              ),
            ),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              Navigator.pop(context);
            },
            child: Text(
              'Exit',
              style: AppTheme.bodyRegular.copyWith(
                color: AppTheme.stressedColor,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final color = _stateConfig.color;
    
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: AppTheme.backgroundGradient,
        ),
        child: SafeArea(
          child: Column(
            children: [
              // Header
              _buildHeader(color),
              
              // Progress bar
              _buildProgressBar(color),
              
              // Main content
              Expanded(
                child: _isCompleted
                    ? _buildCompletionScreen(color)
                    : _buildTaskArea(),
              ),
              
              // Controls
              _buildControls(color),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader(Color color) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          GestureDetector(
            onTap: _isRunning ? _exitSession : () => Navigator.pop(context),
            child: Container(
              width: 44,
              height: 44,
              decoration: BoxDecoration(
                color: Colors.white.withAlpha(10),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.white.withAlpha(20)),
              ),
              child: const Icon(
                LucideIcons.x,
                color: AppTheme.textSecondary,
                size: 20,
              ),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '${widget.stateName} Calibration',
                  style: AppTheme.headingSmall.copyWith(color: color),
                ),
                Text(
                  _currentPhase.name,
                  style: AppTheme.bodySmall.copyWith(
                    color: AppTheme.textMuted,
                  ),
                ),
              ],
            ),
          ),
          // Timer
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            decoration: BoxDecoration(
              color: color.withAlpha(30),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: color.withAlpha(80)),
            ),
            child: Text(
              _formatTime(_phaseSecondsRemaining),
              style: AppTheme.monoMedium.copyWith(
                color: color,
                fontSize: 20,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildProgressBar(Color color) {
    final totalSeconds = _stateConfig.totalSeconds;
    final overallProgress = _totalElapsedSeconds / totalSeconds;
    final phaseProgress = 1 - (_phaseSecondsRemaining / _currentPhase.durationSeconds);
    
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Phase indicators
          Row(
            children: List.generate(_stateConfig.phases.length, (index) {
              final isActive = index == _currentPhaseIndex;
              final isComplete = index < _currentPhaseIndex;
              return Expanded(
                child: Container(
                  margin: EdgeInsets.only(right: index < _stateConfig.phases.length - 1 ? 4 : 0),
                  height: 6,
                  decoration: BoxDecoration(
                    color: isComplete
                        ? color
                        : isActive
                            ? color.withAlpha(100)
                            : Colors.white.withAlpha(20),
                    borderRadius: BorderRadius.circular(3),
                  ),
                  child: isActive
                      ? ClipRRect(
                          borderRadius: BorderRadius.circular(3),
                          child: LinearProgressIndicator(
                            value: phaseProgress,
                            backgroundColor: Colors.transparent,
                            valueColor: AlwaysStoppedAnimation(color),
                          ),
                        )
                      : null,
                ),
              );
            }),
          ),
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Phase ${_currentPhaseIndex + 1} of ${_stateConfig.phases.length}',
                style: AppTheme.bodySmall.copyWith(color: AppTheme.textMuted),
              ),
              Text(
                '${(overallProgress * 100).toInt()}% complete',
                style: AppTheme.bodySmall.copyWith(color: color),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildTaskArea() {
    if (!_isRunning) {
      return _buildStartScreen();
    }
    
    return Padding(
      padding: const EdgeInsets.all(16),
      child: _buildTaskWidget(),
    );
  }

  Widget _buildStartScreen() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Instructions
            GlassCard(
              padding: const EdgeInsets.all(24),
              child: Column(
                children: [
                  Icon(
                    _getPhaseIcon(_currentPhase.mode),
                    color: _stateConfig.color,
                    size: 48,
                  ),
                  const SizedBox(height: 16),
                  Text(
                    _currentPhase.name,
                    style: AppTheme.headingMedium,
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 12),
                  Text(
                    _currentPhase.instructions,
                    style: AppTheme.bodyRegular.copyWith(
                      color: AppTheme.textSecondary,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 16),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        LucideIcons.clock,
                        color: AppTheme.textMuted,
                        size: 16,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        '${_currentPhase.durationSeconds ~/ 60} minutes',
                        style: AppTheme.bodySmall.copyWith(
                          color: AppTheme.textMuted,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            
            const SizedBox(height: 24),
            
            // Start hint
            Text(
              'Press Start to begin',
              style: AppTheme.bodySmall.copyWith(
                color: AppTheme.textMuted,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTaskWidget() {
    switch (_currentPhase.mode) {
      case PhaseMode.breathing:
        return Center(
          child: BreathingWidget(
            breathPattern: _currentPhase.breathPattern ?? [4, 4, 4, 4],
          ),
        );
        
      case PhaseMode.math:
        return Center(
          child: MathWidget(
            operation: _currentPhase.mathOperation ?? MathOp.subtract,
            startValue: _currentPhase.startValue ?? 100,
            stepValue: _currentPhase.stepValue,
            onScoreUpdate: (correct, total) {
              setState(() {
                _phaseCorrect = correct;
                _phaseTotal = total;
              });
            },
          ),
        );
        
      case PhaseMode.stroop:
        return Center(
          child: StroopWidget(
            onScoreUpdate: (correct, total) {
              setState(() {
                _phaseCorrect = correct;
                _phaseTotal = total;
              });
            },
          ),
        );
        
      case PhaseMode.listing:
        return Center(
          child: ListingWidget(
            category: _listingCategory,
          ),
        );
        
      case PhaseMode.reading:
        if (_currentArticle == null) {
          return const Center(child: CircularProgressIndicator());
        }
        return ReadingWidget(
          article: _currentArticle!,
          keywords: _selectedKeywords,
        );
        
      case PhaseMode.recall:
        return RecallWidget(
          articleTitle: _currentArticle?.title ?? 'Previous Article',
          keywords: _selectedKeywords,
        );
    }
  }

  Widget _buildControls(Color color) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          if (_isRunning && !_isCompleted) ...[
            // Pause/Resume
            Expanded(
              child: GestureDetector(
                onTap: _isPaused ? _resumeSession : _pauseSession,
                child: Container(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  decoration: BoxDecoration(
                    color: Colors.white.withAlpha(10),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: Colors.white.withAlpha(20)),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        _isPaused ? LucideIcons.play : LucideIcons.pause,
                        color: AppTheme.textSecondary,
                        size: 20,
                      ),
                      const SizedBox(width: 8),
                      Text(
                        _isPaused ? 'Resume' : 'Pause',
                        style: AppTheme.bodyLarge.copyWith(
                          color: AppTheme.textSecondary,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
            const SizedBox(width: 12),
            // Skip phase
            Expanded(
              child: GestureDetector(
                onTap: _advancePhase,
                child: Container(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  decoration: BoxDecoration(
                    color: color.withAlpha(40),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: color.withAlpha(80)),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        LucideIcons.skipForward,
                        color: color,
                        size: 20,
                      ),
                      const SizedBox(width: 8),
                      Text(
                        'Skip',
                        style: AppTheme.bodyLarge.copyWith(color: color),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ] else if (!_isCompleted) ...[
            // Start button
            Expanded(
              child: GestureDetector(
                onTap: _startSession,
                child: Container(
                  padding: const EdgeInsets.symmetric(vertical: 18),
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [color, color.withAlpha(180)],
                    ),
                    borderRadius: BorderRadius.circular(16),
                    boxShadow: [
                      BoxShadow(
                        color: color.withAlpha(80),
                        blurRadius: 20,
                      ),
                    ],
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(
                        LucideIcons.play,
                        color: Colors.white,
                        size: 24,
                      ),
                      const SizedBox(width: 8),
                      Text(
                        'Start Session',
                        style: AppTheme.headingSmall.copyWith(
                          color: Colors.white,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildCompletionScreen(Color color) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 80,
              height: 80,
              decoration: BoxDecoration(
                color: color.withAlpha(40),
                shape: BoxShape.circle,
              ),
              child: Icon(
                LucideIcons.checkCircle,
                color: color,
                size: 48,
              ),
            ),
            const SizedBox(height: 24),
            Text(
              '${widget.stateName} Calibration Complete!',
              style: AppTheme.headingLarge,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 12),
            Text(
              'Your ${widget.stateName.toLowerCase()} state baseline has been recorded.',
              style: AppTheme.bodyRegular.copyWith(
                color: AppTheme.textSecondary,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 32),
            GestureDetector(
              onTap: () => Navigator.pop(context),
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [color, color.withAlpha(180)],
                  ),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Text(
                  'Continue',
                  style: AppTheme.bodyLarge.copyWith(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _formatTime(int seconds) {
    final mins = seconds ~/ 60;
    final secs = seconds % 60;
    return '${mins.toString().padLeft(2, '0')}:${secs.toString().padLeft(2, '0')}';
  }

  IconData _getPhaseIcon(PhaseMode mode) {
    switch (mode) {
      case PhaseMode.breathing:
        return LucideIcons.wind;
      case PhaseMode.math:
        return LucideIcons.calculator;
      case PhaseMode.stroop:
        return LucideIcons.palette;
      case PhaseMode.listing:
        return LucideIcons.list;
      case PhaseMode.reading:
        return LucideIcons.bookOpen;
      case PhaseMode.recall:
        return LucideIcons.brain;
    }
  }
}
