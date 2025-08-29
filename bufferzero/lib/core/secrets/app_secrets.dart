import 'package:flutter/foundation.dart';

class AppSecrets {
  // Environment configuration
  static const bool isProduction = bool.fromEnvironment(
    'IS_PRODUCTION',
    defaultValue: false,
  );

  // Supabase configuration (safe for all platforms)
  static const String supabaseUrl = String.fromEnvironment('SUPABASE_URL');
  static const String supabaseAnonKey = String.fromEnvironment(
    'SUPABASE_ANON_KEY',
  );
  static const String backendUrl = String.fromEnvironment('BACKEND_URL');

  // Razorpay configuration (platform-specific)
  // ⚠️ Key Secret is NEVER exposed on web builds for security
  static String? get razorpayKeyId {
    if (kIsWeb) {
      // For web builds, get key from backend
      return null;
    }
    // For mobile/desktop builds, use environment variable
    return const String.fromEnvironment('RAZORPAY_KEY_ID');
  }

  // static String? get razorpayKeySecret {
  //   if (kIsWeb) {
  //     // NEVER expose secret on web builds
  //     return null;
  //   }
  //   // Only available on mobile/desktop builds
  //   return const String.fromEnvironment('RAZORPAY_KEY_SECRET');
  // }

  // Backend endpoint for web payments
  static String get paymentEndpoint {
    return '$backendUrl/api/payments';
  }

  // Check if Razorpay is properly configured for current platform
  static bool get isRazorpayConfigured {
    if (kIsWeb) {
      // Web should use backend payment flow
      return backendUrl.isNotEmpty;
    }
    // Mobile/desktop can use direct Razorpay integration
    return razorpayKeyId?.isNotEmpty == true;
  }
}
