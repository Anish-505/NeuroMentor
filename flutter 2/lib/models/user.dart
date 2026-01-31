/// Simple user model
class User {
  final String id;
  final String email;
  final String name;
  final DateTime createdAt;
  bool hasCalibration;

  User({
    required this.id,
    required this.email,
    required this.name,
    required this.createdAt,
    this.hasCalibration = false,
  });

  Map<String, dynamic> toJson() => {
    'id': id,
    'email': email,
    'name': name,
    'createdAt': createdAt.toIso8601String(),
    'hasCalibration': hasCalibration,
  };

  factory User.fromJson(Map<String, dynamic> json) => User(
    id: json['id'],
    email: json['email'],
    name: json['name'],
    createdAt: DateTime.parse(json['createdAt']),
    hasCalibration: json['hasCalibration'] ?? false,
  );
}
