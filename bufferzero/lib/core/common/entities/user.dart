class User {
  final String id;
  final String email;
  final String name;

  User({required this.id, required this.email, required this.name});

  // Convert User to Map for serialization
  Map<String, dynamic> toJson() {
    return {'id': id, 'email': email, 'name': name};
  }

  // Create User from Map for deserialization
  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as String,
      email: json['email'] as String,
      name: json['name'] as String,
    );
  }
}
