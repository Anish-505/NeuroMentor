/// Attention session model for storing monitoring history
class AttentionSession {
  final String sessionId;
  final String userId;
  final DateTime startTime;
  DateTime? endTime;
  final List<AttentionDataPoint> attentionLog;
  String? audioFilePath;

  AttentionSession({
    required this.sessionId,
    required this.userId,
    required this.startTime,
    this.endTime,
    List<AttentionDataPoint>? attentionLog,
    this.audioFilePath,
  }) : attentionLog = attentionLog ?? [];

  /// Duration of the session
  Duration get duration {
    final end = endTime ?? DateTime.now();
    return end.difference(startTime);
  }

  /// Average focus level across the session
  double get averageFocusLevel {
    if (attentionLog.isEmpty) return 0.0;
    return attentionLog.map((p) => p.focusLevel).reduce((a, b) => a + b) / 
           attentionLog.length;
  }

  /// Average stress level across the session
  double get averageStressLevel {
    if (attentionLog.isEmpty) return 0.0;
    return attentionLog.map((p) => p.stressLevel).reduce((a, b) => a + b) / 
           attentionLog.length;
  }

  /// Total time spent focused (focus > 0.6)
  Duration get totalFocusedTime {
    int focusedSeconds = 0;
    for (var point in attentionLog) {
      if (point.focusLevel > 0.6) {
        focusedSeconds++;
      }
    }
    return Duration(seconds: focusedSeconds);
  }

  /// Total time spent unfocused (focus < 0.4)
  Duration get totalUnfocusedTime {
    int unfocusedSeconds = 0;
    for (var point in attentionLog) {
      if (point.focusLevel < 0.4) {
        unfocusedSeconds++;
      }
    }
    return Duration(seconds: unfocusedSeconds);
  }

  /// Number of peak stress moments (stress > 0.7)
  int get peakStressMoments {
    return attentionLog.where((p) => p.stressLevel > 0.7).length;
  }

  /// Add a data point to the session
  void addDataPoint(AttentionDataPoint point) {
    attentionLog.add(point);
  }

  /// End the session
  void endSession() {
    endTime = DateTime.now();
  }

  /// Create from JSON
  factory AttentionSession.fromJson(Map<String, dynamic> json) {
    return AttentionSession(
      sessionId: json['sessionId'] as String,
      userId: json['userId'] as String,
      startTime: DateTime.parse(json['startTime'] as String),
      endTime: json['endTime'] != null 
          ? DateTime.parse(json['endTime'] as String) 
          : null,
      attentionLog: (json['attentionLog'] as List?)
          ?.map((p) => AttentionDataPoint.fromJson(p as Map<String, dynamic>))
          .toList(),
      audioFilePath: json['audioFilePath'] as String?,
    );
  }

  /// Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      'sessionId': sessionId,
      'userId': userId,
      'startTime': startTime.toIso8601String(),
      'endTime': endTime?.toIso8601String(),
      'attentionLog': attentionLog.map((p) => p.toJson()).toList(),
      'audioFilePath': audioFilePath,
    };
  }
}

/// Enum representing detected mental states
enum MentalState {
  calm,
  focused,
  stressed,
  unfocused,
}

/// Extension to get display properties for mental states
extension MentalStateExtension on MentalState {
  String get displayName {
    switch (this) {
      case MentalState.calm:
        return 'Calm';
      case MentalState.focused:
        return 'Focused';
      case MentalState.stressed:
        return 'Stressed';
      case MentalState.unfocused:
        return 'Unfocused';
    }
  }

  int get colorValue {
    switch (this) {
      case MentalState.calm:
        return 0xFF2563EB; // Blue
      case MentalState.focused:
        return 0xFF16A34A; // Green
      case MentalState.stressed:
        return 0xFFEA0C0C; // Red
      case MentalState.unfocused:
        return 0xFFF59E0B; // Amber
    }
  }
}

/// Single attention data point recorded during monitoring
class AttentionDataPoint {
  final DateTime timestamp;
  final double focusLevel;   // 0.0 to 1.0
  final double stressLevel;  // 0.0 to 1.0
  final MentalState state;
  
  /// Raw EEG band powers (optional, for detailed analysis)
  final Map<String, double>? rawBandPowers;

  AttentionDataPoint({
    required this.timestamp,
    required this.focusLevel,
    required this.stressLevel,
    required this.state,
    this.rawBandPowers,
  });

  /// Create from JSON
  factory AttentionDataPoint.fromJson(Map<String, dynamic> json) {
    return AttentionDataPoint(
      timestamp: DateTime.parse(json['timestamp'] as String),
      focusLevel: (json['focusLevel'] as num).toDouble(),
      stressLevel: (json['stressLevel'] as num).toDouble(),
      state: MentalState.values.firstWhere(
        (s) => s.name == json['state'],
        orElse: () => MentalState.calm,
      ),
      rawBandPowers: json['rawBandPowers'] != null
          ? Map<String, double>.from(json['rawBandPowers'] as Map)
          : null,
    );
  }

  /// Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      'timestamp': timestamp.toIso8601String(),
      'focusLevel': focusLevel,
      'stressLevel': stressLevel,
      'state': state.name,
      'rawBandPowers': rawBandPowers,
    };
  }
}
