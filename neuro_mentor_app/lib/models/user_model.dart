import 'calibration_data.dart';

/// User model for NeuroMentor app
/// Stores user profile and calibration status
class UserModel {
  final String uid;
  final String email;
  final String name;
  final String studentId;
  final DateTime createdAt;
  bool hasCompletedCalibration;
  CalibrationData? calibrationBaseline;

  UserModel({
    required this.uid,
    required this.email,
    required this.name,
    this.studentId = '',
    required this.createdAt,
    this.hasCompletedCalibration = false,
    this.calibrationBaseline,
  });

  /// Create UserModel from JSON (for storage)
  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      uid: json['uid'] as String,
      email: json['email'] as String,
      name: json['name'] as String,
      studentId: json['studentId'] as String? ?? '',
      createdAt: DateTime.parse(json['createdAt'] as String),
      hasCompletedCalibration: json['hasCompletedCalibration'] as bool? ?? false,
      calibrationBaseline: json['calibrationBaseline'] != null
          ? CalibrationData.fromJson(json['calibrationBaseline'] as Map<String, dynamic>)
          : null,
    );
  }

  /// Convert to JSON for storage
  Map<String, dynamic> toJson() {
    return {
      'uid': uid,
      'email': email,
      'name': name,
      'studentId': studentId,
      'createdAt': createdAt.toIso8601String(),
      'hasCompletedCalibration': hasCompletedCalibration,
      'calibrationBaseline': calibrationBaseline?.toJson(),
    };
  }

  /// Create a copy with updated fields
  UserModel copyWith({
    String? uid,
    String? email,
    String? name,
    String? studentId,
    DateTime? createdAt,
    bool? hasCompletedCalibration,
    CalibrationData? calibrationBaseline,
  }) {
    return UserModel(
      uid: uid ?? this.uid,
      email: email ?? this.email,
      name: name ?? this.name,
      studentId: studentId ?? this.studentId,
      createdAt: createdAt ?? this.createdAt,
      hasCompletedCalibration: hasCompletedCalibration ?? this.hasCompletedCalibration,
      calibrationBaseline: calibrationBaseline ?? this.calibrationBaseline,
    );
  }

  @override
  String toString() {
    return 'UserModel(uid: $uid, email: $email, name: $name)';
  }
}
