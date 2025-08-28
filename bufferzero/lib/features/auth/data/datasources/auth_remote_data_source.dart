import 'dart:async';
import 'dart:io';

import 'package:bufferzero/core/error/exceptions.dart';
import 'package:bufferzero/features/auth/data/models/user_model.dart';
import 'package:flutter/foundation.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:shelf/shelf.dart';
import 'package:shelf/shelf_io.dart' as io;
import 'package:supabase_flutter/supabase_flutter.dart';

/// Contract for authentication data source operations
abstract interface class AuthRemoteDataSource {
  /// Current user session
  Session? get currentSession;

  /// Sign up with email and password
  Future<UserModel> signUpWithEmailPassword({
    required String name,
    required String email,
    required String password,
  });

  /// Sign in with email and password
  Future<UserModel> signInWithEmailPassword({
    required String email,
    required String password,
  });

  /// Sign in with Google OAuth
  Future<UserModel> signInWithGoogle();

  /// Sign in anonymously
  Future<UserModel> signInAnonymously();

  /// Get current user data
  Future<UserModel?> getCurrentUserData();

  /// Sign out current user
  Future<void> logout();

  /// Resend email verification
  Future<void> resendEmailVerification({required String email});
}

/// Implementation of authentication data source using Supabase
class AuthRemoteDataSourceImpl implements AuthRemoteDataSource {
  final SupabaseClient supabaseClient;

  // OAuth client IDs
  static const _webClientId =
      '827146341594-cqm5rgvj5nf70tt5kjveeijdhgto70ud.apps.googleusercontent.com';
  static const _iosClientId =
      '827146341594-se5r95rug7iv02vkkbgfd4dah6h03l88.apps.googleusercontent.com';
  static const _redirectUrl = 'http://localhost:54321/auth/callback';
  static const _emailRedirectUrl =
      'http://localhost:3000/sign-in?new-sign-up=true';

  AuthRemoteDataSourceImpl({required this.supabaseClient});

  @override
  Session? get currentSession => supabaseClient.auth.currentSession;

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
        data: {'name': name},
        emailRedirectTo: _emailRedirectUrl,
      );

      if (response.user == null) {
        throw const ServerException('User creation failed');
      }

      // Check if email verification is required
      if (response.user!.emailConfirmedAt == null) {
        throw EmailVerificationRequiredException(email);
      }

      return await _getUserData(response.user!.id, response.user!.email, name);
    } on EmailVerificationRequiredException {
      rethrow;
    } catch (e) {
      throw ServerException('Sign up failed: ${e.toString()}');
    }
  }

  @override
  Future<UserModel> signInWithEmailPassword({
    required String email,
    required String password,
  }) async {
    try {
      final response = await supabaseClient.auth.signInWithPassword(
        email: email,
        password: password,
      );

      if (response.user == null) {
        throw const ServerException('Sign in failed');
      }

      return await _getUserDataFromDb(response.user!.id, response.user!.email);
    } catch (e) {
      throw ServerException('Sign in failed: ${e.toString()}');
    }
  }

  @override
  Future<UserModel> signInWithGoogle() async {
    try {
      if (kIsWeb) {
        return await _handleWebGoogleSignIn();
      } else if (Platform.isLinux || Platform.isWindows) {
        return await _handleDesktopGoogleSignIn();
      } else {
        return await _handleMobileGoogleSignIn();
      }
    } catch (e) {
      throw ServerException('Google Sign-In failed: ${e.toString()}');
    }
  }

  @override
  Future<UserModel> signInAnonymously() async {
    try {
      final response = await supabaseClient.auth.signInAnonymously();

      if (response.user == null) {
        throw const ServerException('Anonymous sign in failed');
      }

      return await _getUserDataFromDb(response.user!.id, response.user!.email);
    } catch (e) {
      throw ServerException('Anonymous sign in failed: ${e.toString()}');
    }
  }

  @override
  Future<UserModel?> getCurrentUserData() async {
    try {
      final session = currentSession;
      if (session == null) return null;

      return await _getUserDataFromDb(session.user.id, session.user.email);
    } catch (e) {
      throw ServerException('Failed to get user data: ${e.toString()}');
    }
  }

  @override
  Future<void> logout() async {
    try {
      await supabaseClient.auth.signOut();
    } catch (e) {
      throw ServerException('Logout failed: ${e.toString()}');
    }
  }

  @override
  Future<void> resendEmailVerification({required String email}) async {
    try {
      await supabaseClient.auth.resend(type: OtpType.signup, email: email);
    } catch (e) {
      throw ServerException('Failed to resend verification: ${e.toString()}');
    }
  }

  // Private helper methods

  /// Handle Google Sign-In for web platform
  Future<UserModel> _handleWebGoogleSignIn() async {
    await supabaseClient.auth.signInWithOAuth(
      OAuthProvider.google,
      redirectTo: '${Uri.base.origin}/sign-in?redirect=/dashboard',
    );

    throw 'OAuth flow initiated - awaiting redirect';
  }

  /// Handle Google Sign-In for desktop platforms
  Future<UserModel> _handleDesktopGoogleSignIn() async {
    final completer = Completer<Session>();

    final server = await io.serve(
      _createAuthCallbackHandler(completer),
      InternetAddress.loopbackIPv4,
      54321,
    );

    try {
      await supabaseClient.auth.signInWithOAuth(
        OAuthProvider.google,
        redirectTo: _redirectUrl,
        authScreenLaunchMode: LaunchMode.externalApplication,
      );

      final session = await completer.future.timeout(
        const Duration(minutes: 2),
        onTimeout: () => throw TimeoutException('Login timed out'),
      );

      return await _getUserData(
        session.user.id,
        session.user.email,
        session.user.userMetadata?['name'] ?? 'Google User',
      );
    } finally {
      await server.close(force: true);
    }
  }

  /// Handle Google Sign-In for mobile platforms
  Future<UserModel> _handleMobileGoogleSignIn() async {
    final googleSignIn = GoogleSignIn(
      clientId: _iosClientId,
      serverClientId: _webClientId,
      scopes: ['email', 'profile', 'openid'],
    );

    final googleUser = await googleSignIn.signIn();
    if (googleUser == null) {
      throw 'User cancelled Google Sign-In';
    }

    final googleAuth = await googleUser.authentication;
    if (googleAuth.idToken == null) {
      throw 'No ID Token received from Google';
    }

    final response = await supabaseClient.auth.signInWithIdToken(
      provider: OAuthProvider.google,
      idToken: googleAuth.idToken!,
      accessToken: googleAuth.accessToken,
    );

    if (response.user == null) {
      throw 'Failed to authenticate with Supabase';
    }

    return await _getUserData(
      response.user!.id,
      response.user!.email ?? googleUser.email,
      response.user!.userMetadata?['name'] ??
          googleUser.displayName ??
          'Google User',
    );
  }

  /// Create HTTP handler for OAuth callback
  Handler _createAuthCallbackHandler(Completer<Session> completer) {
    return (Request req) async {
      final uri = req.requestedUri;

      if (uri.path != '/auth/callback') {
        return Response.notFound('Not Found');
      }

      final code = uri.queryParameters['code'];
      if (code == null) {
        return Response.badRequest(body: 'Missing authorization code');
      }

      try {
        final response = await supabaseClient.auth.exchangeCodeForSession(code);
        final session = response.session;

        if (!completer.isCompleted) {
          completer.complete(session);
        }

        return Response.ok(
          'Authentication successful. You may close this tab.',
          headers: {'content-type': 'text/plain'},
        );
      } catch (e) {
        if (!completer.isCompleted) {
          completer.completeError(e);
        }
        return Response.internalServerError(body: 'Authentication error: $e');
      }
    };
  }

  /// Get user data with fallback creation
  Future<UserModel> _getUserData(String id, String? email, String name) async {
    try {
      final userData = await supabaseClient
          .from('users')
          .select()
          .eq('id', id)
          .single();

      return UserModel.fromJson(userData).copyWith(email: email);
    } catch (e) {
      // Return user model with provided data if DB fetch fails
      return UserModel(id: id, email: email ?? 'unknown', name: name);
    }
  }

  /// Get user data from database
  Future<UserModel> _getUserDataFromDb(String id, String? email) async {
    final userData = await supabaseClient
        .from('users')
        .select()
        .eq('id', id)
        .single();

    return UserModel.fromJson(userData).copyWith(email: email);
  }
}
