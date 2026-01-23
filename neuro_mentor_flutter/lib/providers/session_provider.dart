import 'dart:async';
import 'dart:math';
import 'package:flutter/foundation.dart';
import '../config/state_config.dart';

/// Session Provider - Manages the entire training session state
/// Ported from Python BrainStateApp class logic

class SessionProvider extends ChangeNotifier {
  // Current state
  String _currentStateName = 'Calm';
  int _currentPhaseIndex = 0;
  int _stateElapsedSeconds = 0;
  int _phaseRemainingSeconds = 0;
  
  // Timer
  Timer? _timer;
  Timer? _breathTimer;
  bool _isRunning = false;
  bool _autoSequence = false;
  
  // Scoring (for Stressed state)
  int _scoreCorrect = 0;
  int _scoreAttempts = 0;
  
  // Breathing state
  int _breathCyclePos = 0;
  String _breathCue = '';
  
  // Math state
  int _mathCurrentValue = 1000;
  String _mathFeedback = '';
  
  // Stroop state
  String? _stroopCurrentWord;
  int? _stroopCurrentColorValue;
  String? _stroopCorrectColorName;
  String _stroopFeedback = '';
  
  // Reading state
  String _currentArticleTitle = '';
  String _currentArticleText = '';
  
  // Session completion callback
  Function(String message)? onStateComplete;

  SessionProvider() {
    _initializePhase();
  }

  // Getters
  String get currentStateName => _currentStateName;
  StateConfig get currentConfig => stateConfigs[_currentStateName]!;
  Phase get currentPhase => currentConfig.phases[_currentPhaseIndex];
  int get currentPhaseIndex => _currentPhaseIndex;
  int get totalPhases => currentConfig.phases.length;
  int get stateElapsedSeconds => _stateElapsedSeconds;
  int get phaseRemainingSeconds => _phaseRemainingSeconds;
  bool get isRunning => _isRunning;
  bool get autoSequence => _autoSequence;
  int get scoreCorrect => _scoreCorrect;
  int get scoreAttempts => _scoreAttempts;
  String get breathCue => _breathCue;
  int get mathCurrentValue => _mathCurrentValue;
  String get mathFeedback => _mathFeedback;
  String? get stroopCurrentWord => _stroopCurrentWord;
  int? get stroopCurrentColorValue => _stroopCurrentColorValue;
  String get stroopFeedback => _stroopFeedback;
  String get currentArticleTitle => _currentArticleTitle;
  String get currentArticleText => _currentArticleText;

  String get timerDisplay {
    int minutes = _phaseRemainingSeconds ~/ 60;
    int seconds = _phaseRemainingSeconds % 60;
    return '${minutes.toString().padLeft(2, '0')}:${seconds.toString().padLeft(2, '0')}';
  }

  double get progressPercent {
    int totalSec = currentConfig.totalSeconds;
    if (totalSec == 0) return 0;
    return _stateElapsedSeconds / totalSec;
  }

  void _initializePhase() {
    _phaseRemainingSeconds = currentPhase.durationSeconds;
    
    // Reset mode-specific state
    if (currentPhase.mode == 'breathing') {
      _breathCyclePos = 0;
      _updateBreathCue();
    } else if (currentPhase.mode == 'math') {
      _mathCurrentValue = currentPhase.startValue ?? 1000;
      _mathFeedback = '';
    } else if (currentPhase.mode == 'stroop') {
      _generateStroopTrial();
    } else if (currentPhase.mode == 'reading') {
      if (_currentArticleTitle.isEmpty) {
        loadRandomArticle();
      }
    }
    
    notifyListeners();
  }

  // State Changes
  void changeState(String newState) {
    if (_isRunning) {
      stop();
    }
    _currentStateName = newState;
    _currentPhaseIndex = 0;
    _stateElapsedSeconds = 0;
    _scoreCorrect = 0;
    _scoreAttempts = 0;
    _mathCurrentValue = 1000;
    _currentArticleTitle = '';
    _currentArticleText = '';
    _initializePhase();
  }

  void toggleAutoSequence() {
    _autoSequence = !_autoSequence;
    notifyListeners();
  }

  // Timer Controls
  void start() {
    if (_isRunning) return;
    _isRunning = true;
    
    _timer = Timer.periodic(const Duration(seconds: 1), (_) => _onTimerTick());
    
    if (currentPhase.mode == 'breathing') {
      _breathTimer = Timer.periodic(const Duration(seconds: 1), (_) => _onBreathTick());
    }
    
    notifyListeners();
  }

  void stop() {
    _isRunning = false;
    _timer?.cancel();
    _breathTimer?.cancel();
    notifyListeners();
  }

  void reset() {
    stop();
    _currentPhaseIndex = 0;
    _stateElapsedSeconds = 0;
    _scoreCorrect = 0;
    _scoreAttempts = 0;
    _mathCurrentValue = currentPhase.startValue ?? 1000;
    _initializePhase();
  }

  void nextPhase() {
    if (_currentPhaseIndex < currentConfig.phases.length - 1) {
      // Calculate elapsed time for previous phases
      _stateElapsedSeconds = 0;
      for (int i = 0; i <= _currentPhaseIndex; i++) {
        _stateElapsedSeconds += currentConfig.phases[i].durationSeconds;
      }
      _currentPhaseIndex++;
      _breathTimer?.cancel();
      _initializePhase();
      
      if (_isRunning && currentPhase.mode == 'breathing') {
        _breathTimer = Timer.periodic(const Duration(seconds: 1), (_) => _onBreathTick());
      }
    }
  }

  void _onTimerTick() {
    if (!_isRunning) return;
    
    if (_phaseRemainingSeconds > 0) {
      _phaseRemainingSeconds--;
      _stateElapsedSeconds++;
      notifyListeners();
    } else {
      // Phase complete
      if (_currentPhaseIndex < currentConfig.phases.length - 1) {
        nextPhase();
      } else {
        // State complete
        stop();
        String msg = '$_currentStateName session completed.';
        if (_currentStateName == 'Stressed') {
          msg += '\n\nPerformance Score: $_scoreCorrect/$_scoreAttempts';
          if (_scoreAttempts > 0) {
            int percent = ((_scoreCorrect / _scoreAttempts) * 100).round();
            msg += ' ($percent%)';
            if (percent > 80) {
              msg += '\nGreat focus under pressure!';
            } else {
              msg += '\nKeep practicing to improve resilience.';
            }
          }
        }
        
        if (_autoSequence) {
          _goToNextStateInSequence();
        } else {
          onStateComplete?.call(msg);
        }
      }
    }
  }

  void _goToNextStateInSequence() {
    List<String> states = stateConfigs.keys.toList();
    int idx = states.indexOf(_currentStateName);
    if (idx < states.length - 1) {
      changeState(states[idx + 1]);
      start();
    } else {
      onStateComplete?.call('All states (Calm → Stressed → Focused) completed.');
    }
  }

  // Breathing Logic
  void _onBreathTick() {
    if (currentPhase.mode != 'breathing') return;
    
    List<int> pattern = currentPhase.breathPattern ?? [4, 4, 4, 4];
    int cycleLength = pattern.reduce((a, b) => a + b);
    
    _breathCyclePos = (_breathCyclePos + 1) % cycleLength;
    _updateBreathCue();
    notifyListeners();
  }

  void _updateBreathCue() {
    List<int> pattern = currentPhase.breathPattern ?? [4, 4, 4, 4];
    int t = _breathCyclePos;
    int p1 = pattern[0], p2 = pattern[1], p3 = pattern[2], p4 = pattern[3];
    
    if (t < p1) {
      _breathCue = 'Inhale (${p1 - t})';
    } else if (t < p1 + p2) {
      _breathCue = 'Hold (${p1 + p2 - t})';
    } else if (t < p1 + p2 + p3) {
      _breathCue = 'Exhale (${p1 + p2 + p3 - t})';
    } else if (p4 > 0) {
      _breathCue = 'Hold (${p1 + p2 + p3 + p4 - t})';
    } else {
      _breathCue = '';
    }
  }

  // Math Logic
  void submitMathAnswer(String answer) {
    int? userAnswer = int.tryParse(answer);
    if (userAnswer == null) {
      _mathFeedback = 'Enter a number';
      notifyListeners();
      return;
    }
    
    _scoreAttempts++;
    String op = currentPhase.mathOperation ?? 'subtract';
    int expected = op == 'add' ? _mathCurrentValue + 7 : _mathCurrentValue - 7;
    
    if (userAnswer == expected) {
      _scoreCorrect++;
      _mathCurrentValue = expected;
      _mathFeedback = '✓ Correct!';
    } else {
      _mathFeedback = '✗ Wrong. Expected: $expected';
    }
    notifyListeners();
  }

  // Stroop Logic
  void _generateStroopTrial() {
    final random = Random();
    // Pick a random word
    int wordIdx = random.nextInt(stroopColors.length);
    _stroopCurrentWord = stroopColors[wordIdx]['name'];
    
    // Pick a random (potentially different) color for the text
    int colorIdx = random.nextInt(stroopColors.length);
    _stroopCurrentColorValue = stroopColors[colorIdx]['color'];
    _stroopCorrectColorName = stroopColors[colorIdx]['name'];
    
    _stroopFeedback = '';
    notifyListeners();
  }

  void selectStroopColor(String colorName) {
    _scoreAttempts++;
    if (colorName == _stroopCorrectColorName) {
      _scoreCorrect++;
      _stroopFeedback = '✓ Correct!';
    } else {
      _stroopFeedback = '✗ Wrong. It was ${_stroopCorrectColorName}';
    }
    notifyListeners();
    
    // Generate next trial after a short delay
    Future.delayed(const Duration(milliseconds: 500), () {
      _generateStroopTrial();
    });
  }

  // Reading Logic
  void loadRandomArticle() {
    final random = Random();
    int idx = random.nextInt(localArticles.length);
    _currentArticleTitle = localArticles[idx]['title']!;
    _currentArticleText = localArticles[idx]['text']!;
    notifyListeners();
  }

  @override
  void dispose() {
    _timer?.cancel();
    _breathTimer?.cancel();
    super.dispose();
  }
}
