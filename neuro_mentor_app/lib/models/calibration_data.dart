/// Calibration data model storing EEG baselines for each mental state
/// Used to compare live readings against personalized baselines
class CalibrationData {
  /// Average EEG band powers during calm state
  /// Keys: delta, theta, alpha, beta, gamma
  final Map<String, double> calmState;
  
  /// Average EEG band powers during stressed state
  final Map<String, double> stressedState;
  
  /// Average EEG band powers during focused state
  final Map<String, double> focusedState;
  
  /// When this calibration was performed
  final DateTime calibratedAt;
  
  /// True if this is user-specific calibration, false if using default dataset
  final bool isPersonalized;
  
  /// Source of calibration: "personal" or "default_sample_v1"
  final String datasetSource;

  CalibrationData({
    required this.calmState,
    required this.stressedState,
    required this.focusedState,
    required this.calibratedAt,
    this.isPersonalized = true,
    this.datasetSource = 'personal',
  });

  /// Stress Index: Beta/Alpha ratio during stressed state
  /// Higher values indicate more stress
  double get stressIndex {
    final beta = stressedState['beta'] ?? 0.0;
    final alpha = stressedState['alpha'] ?? 1.0;
    return beta / (alpha + 1e-9); // Epsilon to prevent division by zero
  }

  /// Focus Index: Alpha/Theta ratio during focused state
  /// Higher values indicate better focus
  double get focusIndex {
    final alpha = focusedState['alpha'] ?? 0.0;
    final theta = focusedState['theta'] ?? 1.0;
    return alpha / (theta + 1e-9);
  }

  /// Relaxation Index: Theta/Beta ratio during calm state
  /// Higher values indicate more relaxation
  double get relaxationIndex {
    final theta = calmState['theta'] ?? 0.0;
    final beta = calmState['beta'] ?? 1.0;
    return theta / (beta + 1e-9);
  }

  /// Create from JSON
  factory CalibrationData.fromJson(Map<String, dynamic> json) {
    return CalibrationData(
      calmState: Map<String, double>.from(json['calmState'] as Map),
      stressedState: Map<String, double>.from(json['stressedState'] as Map),
      focusedState: Map<String, double>.from(json['focusedState'] as Map),
      calibratedAt: DateTime.parse(json['calibratedAt'] as String),
      isPersonalized: json['isPersonalized'] as bool? ?? true,
      datasetSource: json['datasetSource'] as String? ?? 'personal',
    );
  }

  /// Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      'calmState': calmState,
      'stressedState': stressedState,
      'focusedState': focusedState,
      'calibratedAt': calibratedAt.toIso8601String(),
      'isPersonalized': isPersonalized,
      'datasetSource': datasetSource,
    };
  }

  /// Create default calibration data (sample dataset)
  /// These are average values for reference when user hasn't calibrated
  factory CalibrationData.defaultSample() {
    return CalibrationData(
      calmState: {
        'delta': 35.0,
        'theta': 25.0,
        'alpha': 30.0,
        'beta': 8.0,
        'gamma': 2.0,
      },
      stressedState: {
        'delta': 20.0,
        'theta': 15.0,
        'alpha': 12.0,
        'beta': 40.0,
        'gamma': 13.0,
      },
      focusedState: {
        'delta': 18.0,
        'theta': 12.0,
        'alpha': 35.0,
        'beta': 28.0,
        'gamma': 7.0,
      },
      calibratedAt: DateTime.now(),
      isPersonalized: false,
      datasetSource: 'default_sample_v1',
    );
  }
}
