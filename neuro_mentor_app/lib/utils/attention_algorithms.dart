import '../models/calibration_data.dart';
import '../models/attention_session.dart';

/// Attention detection algorithms ported from Python MonitoringWithRatios.py
/// Uses multi-criteria alerting for reliable state detection

class AttentionAlgorithms {
  // ============================================================
  // THRESHOLDS (from Python implementation)
  // ============================================================
  
  /// For STRESS detection:
  /// Live Beta/Alpha ratio must be 20% higher than calibrated "Stressed" ratio
  static const double stressRatioThreshold = 1.2;
  
  /// Live Beta power must ALSO be 10% higher than calibrated "Stressed" Beta
  static const double stressPowerThreshold = 1.1;
  
  /// For FOCUS LOSS detection:
  /// Live Alpha/Theta ratio must be 20% lower than calibrated "Focused" ratio
  static const double focusRatioThreshold = 0.8;
  
  /// Live Alpha power must ALSO be 10% lower than calibrated "Focused" Alpha
  static const double focusPowerThreshold = 0.9;
  
  /// Threshold for positive focus detection
  static const double positiveFocusThreshold = 1.1;
  
  // ============================================================
  // RATIO CALCULATIONS
  // ============================================================
  
  /// Calculate stress index (Beta/Alpha ratio)
  static double calculateStressIndex(Map<String, double> bandPowers) {
    final beta = bandPowers['beta'] ?? 0.0;
    final alpha = bandPowers['alpha'] ?? 1.0;
    return beta / (alpha + 1e-9);
  }
  
  /// Calculate focus index (Alpha/Theta ratio)
  static double calculateFocusIndex(Map<String, double> bandPowers) {
    final alpha = bandPowers['alpha'] ?? 0.0;
    final theta = bandPowers['theta'] ?? 1.0;
    return alpha / (theta + 1e-9);
  }
  
  /// Calculate relaxation index (Theta/Beta ratio)
  static double calculateRelaxationIndex(Map<String, double> bandPowers) {
    final theta = bandPowers['theta'] ?? 0.0;
    final beta = bandPowers['beta'] ?? 1.0;
    return theta / (beta + 1e-9);
  }
  
  // ============================================================
  // STATE DETECTION (Multi-Criteria Alerting)
  // ============================================================
  
  /// Detect mental state using multi-criteria alerting logic
  /// Both power and ratio conditions must be met for stress/focus-loss alerts
  static MentalState detectState({
    required Map<String, double> liveBandPowers,
    required CalibrationData baseline,
  }) {
    // Calculate live ratios
    final liveStressIndex = calculateStressIndex(liveBandPowers);
    final liveFocusIndex = calculateFocusIndex(liveBandPowers);
    
    // Get calibrated values
    final calibratedStressRatio = baseline.stressIndex;
    final calibratedFocusRatio = baseline.focusIndex;
    final calibratedStressedBeta = baseline.stressedState['beta'] ?? 0.0;
    final calibratedFocusedAlpha = baseline.focusedState['alpha'] ?? 0.0;
    
    // Get live band powers
    final liveBeta = liveBandPowers['beta'] ?? 0.0;
    final liveAlpha = liveBandPowers['alpha'] ?? 0.0;
    
    // ---- Check for STRESS ----
    // Condition 1: Live Beta/Alpha ratio significantly higher than calibrated
    final ratioStressCond = liveStressIndex > (calibratedStressRatio * stressRatioThreshold);
    // Condition 2: Live Beta power also significantly higher than calibrated
    final powerStressCond = liveBeta > (calibratedStressedBeta * stressPowerThreshold);
    
    // Alert only if BOTH conditions are true
    if (ratioStressCond && powerStressCond) {
      return MentalState.stressed;
    }
    
    // ---- Check for FOCUS LOSS ----
    // Condition 1: Live Alpha/Theta ratio significantly lower than calibrated
    final ratioFocusLossCond = liveFocusIndex < (calibratedFocusRatio * focusRatioThreshold);
    // Condition 2: Live Alpha power also significantly lower than calibrated
    final powerFocusLossCond = liveAlpha < (calibratedFocusedAlpha * focusPowerThreshold);
    
    // Alert only if BOTH conditions are true
    if (ratioFocusLossCond && powerFocusLossCond) {
      return MentalState.unfocused;
    }
    
    // ---- Check for POSITIVE FOCUS ----
    if (liveFocusIndex > (calibratedFocusRatio * positiveFocusThreshold)) {
      return MentalState.focused;
    }
    
    // Default state is calm
    return MentalState.calm;
  }
  
  // ============================================================
  // FOCUS/STRESS LEVEL CALCULATION (0.0 - 1.0)
  // ============================================================
  
  /// Calculate focus level as a normalized value (0.0 to 1.0)
  static double calculateFocusLevel({
    required Map<String, double> liveBandPowers,
    required CalibrationData baseline,
  }) {
    final liveFocusIndex = calculateFocusIndex(liveBandPowers);
    final calibratedFocusRatio = baseline.focusIndex;
    
    // Normalize: focused state = 1.0, unfocused = 0.0
    // Ratio of 0.5x calibrated = 0.0, 1.5x calibrated = 1.0
    final normalized = (liveFocusIndex / calibratedFocusRatio - 0.5) / 1.0;
    return normalized.clamp(0.0, 1.0);
  }
  
  /// Calculate stress level as a normalized value (0.0 to 1.0)
  static double calculateStressLevel({
    required Map<String, double> liveBandPowers,
    required CalibrationData baseline,
  }) {
    final liveStressIndex = calculateStressIndex(liveBandPowers);
    final calibratedStressRatio = baseline.stressIndex;
    
    // Normalize: calm = 0.0, high stress = 1.0
    // Ratio of 0.5x calibrated = 0.0, 1.5x calibrated = 1.0
    final normalized = (liveStressIndex / calibratedStressRatio - 0.5) / 1.0;
    return normalized.clamp(0.0, 1.0);
  }
  
  // ============================================================
  // DATA POINT CREATION
  // ============================================================
  
  /// Create an attention data point from live EEG readings
  static AttentionDataPoint createDataPoint({
    required Map<String, double> liveBandPowers,
    required CalibrationData baseline,
  }) {
    final focusLevel = calculateFocusLevel(
      liveBandPowers: liveBandPowers,
      baseline: baseline,
    );
    
    final stressLevel = calculateStressLevel(
      liveBandPowers: liveBandPowers,
      baseline: baseline,
    );
    
    final state = detectState(
      liveBandPowers: liveBandPowers,
      baseline: baseline,
    );
    
    return AttentionDataPoint(
      timestamp: DateTime.now(),
      focusLevel: focusLevel,
      stressLevel: stressLevel,
      state: state,
      rawBandPowers: Map.from(liveBandPowers),
    );
  }
}
