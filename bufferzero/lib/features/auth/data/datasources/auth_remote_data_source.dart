import 'package:bufferzero/core/error/exceptions.dart';
import 'package:bufferzero/features/auth/data/models/user_model.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

abstract interface class AuthRemoteDataSource {
  Session? get currentSession;

  Future<UserModel> signUpWithEmailPassword({
    required String name,
    required String email,
    required String password,
  });
  Future<UserModel> signInWithEmailPassword({
    required String email,
    required String password,
  });

  Future<UserModel> signInWithGoogle();
  Future<UserModel> signInAnonymously();

  Future<UserModel?> getCurrentUserData();
  Future<void> logout();
  Future<void> resendEmailVerification({required String email});
  Future<bool> checkEmailVerificationStatus({required String email});
}

class AuthRemoteDataSourceImpl implements AuthRemoteDataSource {
  final SupabaseClient supabaseClient;
  AuthRemoteDataSourceImpl({required this.supabaseClient});

  @override
  Session? get currentSession => supabaseClient.auth.currentSession;

  @override
  Future<UserModel> signInWithGoogle() async {
    return UserModel(id: "test", email: "test@test.com", name: "Test User");
  }

  @override
  Future<UserModel> signUpWithEmailPassword({
    required String name,
    required String email,
    required String password,
  }) async {
    try {
      final response = await supabaseClient.auth.signUp(
        password: password,
        email: email,
        data: {"name": name},
        emailRedirectTo: "http://localhost:3000/sign-in?new-sign-up=true",
      );
      print("SignUp response: ${response.user}");

      // Check if email confirmation is required
      if (response.user != null && response.user!.emailConfirmedAt == null) {
        // User is created but email needs verification
        // We'll throw a specific exception to handle this case
        throw EmailVerificationRequiredException(email);
      }

      if (response.user == null) {
        throw const ServerException("User is null");
      }

      // Try to fetch complete user data from users table
      // If it doesn't exist yet, create UserModel with the provided data
      try {
        final userData = await supabaseClient
            .from('users')
            .select()
            .eq('id', response.user!.id)
            .single();

        return UserModel.fromJson(
          userData,
        ).copyWith(email: response.user!.email);
      } catch (e) {
        // If user data doesn't exist in users table yet, use the auth data
        return UserModel(
          id: response.user!.id,
          email: response.user!.email ?? email,
          name: name,
        );
      }
    } on EmailVerificationRequiredException {
      rethrow;
    } catch (e) {
      throw ServerException(e.toString());
    }
  }

  @override
  Future<UserModel> signInWithEmailPassword({
    required String email,
    required String password,
  }) async {
    try {
      final response = await supabaseClient.auth.signInWithPassword(
        password: password,
        email: email,
      );

      if (response.user == null) {
        throw const ServerException("User is null");
      }

      // Fetch complete user data including name from users table
      final userData = await supabaseClient
          .from('users')
          .select()
          .eq('id', response.user!.id)
          .single();

      return UserModel.fromJson(userData).copyWith(email: response.user!.email);
    } catch (e) {
      throw ServerException(e.toString());
    }
  }

  @override
  Future<UserModel?> getCurrentUserData() async {
    try {
      if (currentSession != null) {
        final userData = await supabaseClient
            .from('users')
            .select()
            .eq('id', currentSession!.user.id)
            .single();
        return UserModel.fromJson(
          userData,
        ).copyWith(email: currentSession!.user.email);
      }
      return null;
    } catch (e) {
      throw ServerException(e.toString());
    }
  }

  @override
  Future<void> logout() async {
    try {
      await supabaseClient.auth.signOut();
    } catch (e) {
      throw ServerException(e.toString());
    }
  }

  @override
  Future<UserModel> signInAnonymously() async {
    try {
      final response = await supabaseClient.auth.signInAnonymously();

      if (response.user == null) {
        throw const ServerException("User is null");
      }

      // Fetch complete user data including name from users table
      final userData = await supabaseClient
          .from('users')
          .select()
          .eq('id', response.user!.id)
          .single();

      return UserModel.fromJson(userData).copyWith(email: response.user!.email);
    } catch (e) {
      throw ServerException(e.toString());
    }
  }

  @override
  Future<void> resendEmailVerification({required String email}) async {
    try {
      print("Resending email verification to $email");
      await supabaseClient.auth.resend(type: OtpType.signup, email: email);
    } catch (e) {
      print("Error resending email verification: $e");
      throw ServerException(e.toString());
    }
  }

  @override
  Future<bool> checkEmailVerificationStatus({required String email}) async {
    try {
      // Fetch the latest user state from Supabase
      final response = await supabaseClient.auth.getUser();
      final currentUser = response.user;

      if (currentUser != null && currentUser.emailConfirmedAt != null) {
        return true; // ✅ Email verified
      }

      return false; // ❌ Email not verified yet
    } catch (e) {
      print("Error checking email verification: $e");
      return false;
    }
  }
}
