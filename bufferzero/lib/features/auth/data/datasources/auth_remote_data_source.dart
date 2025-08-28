import 'dart:async';
import 'package:bufferzero/core/error/exceptions.dart';
import 'package:bufferzero/features/auth/data/models/user_model.dart';
import 'package:flutter/foundation.dart';
import 'package:google_sign_in/google_sign_in.dart';
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
}

class AuthRemoteDataSourceImpl implements AuthRemoteDataSource {
  final SupabaseClient supabaseClient;
  AuthRemoteDataSourceImpl({required this.supabaseClient});

  @override
  Session? get currentSession => supabaseClient.auth.currentSession;

  @override
  Future<UserModel> signInWithGoogle() async {
    try {
      print('Starting Google Sign-In...');

      // For web, use Supabase's native OAuth flow instead of google_sign_in plugin
      // This avoids the ID token issues on web
      if (kIsWeb) {
        print('Using Supabase OAuth for web...');

        await supabaseClient.auth.signInWithOAuth(
          OAuthProvider.google,
          redirectTo: '${Uri.base.origin}/sign-in?redirect=/dashboard',
        );

        // The OAuth flow will redirect to Google and back
        // We need to handle this differently - the auth state change will be handled
        // by the main app listener, so we throw a special exception to indicate
        // that the OAuth flow was initiated
        throw 'OAuth flow initiated - please wait for redirect';
      } else {
        // For mobile platforms, use google_sign_in plugin
        print('Using google_sign_in plugin for mobile...');

        /// Web Client ID that you registered with Google Cloud.
        const webClientId =
            '827146341594-cqm5rgvj5nf70tt5kjveeijdhgto70ud.apps.googleusercontent.com';

        /// iOS Client ID that you registered with Google Cloud.
        const iosClientId =
            '827146341594-se5r95rug7iv02vkkbgfd4dah6h03l88.apps.googleusercontent.com';

        final GoogleSignIn googleSignIn = GoogleSignIn(
          clientId: iosClientId,
          serverClientId: webClientId,
          scopes: ['email', 'profile', 'openid'],
        );

        final googleUser = await googleSignIn.signIn();
        if (googleUser == null) {
          throw 'User cancelled Google Sign-In';
        }

        final googleAuth = await googleUser.authentication;
        final accessToken = googleAuth.accessToken;
        final idToken = googleAuth.idToken;

        if (idToken == null) {
          throw 'No ID Token found for mobile sign-in';
        }

        print('Authenticating with Supabase using mobile tokens...');
        final response = await supabaseClient.auth.signInWithIdToken(
          provider: OAuthProvider.google,
          idToken: idToken,
          accessToken: accessToken,
        );

        if (response.user == null) {
          throw 'Failed to authenticate with Supabase.';
        }

        // Fetch user data from users table
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
          return UserModel(
            id: response.user!.id,
            email: response.user!.email ?? googleUser.email,
            name:
                response.user!.userMetadata?['name'] ??
                googleUser.displayName ??
                'Google User',
          );
        }
      }
    } catch (e) {
      print('Google Sign-In error: $e');
      throw ServerException('Google Sign-In failed: ${e.toString()}');
    }
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
}
