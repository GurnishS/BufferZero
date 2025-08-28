import 'package:flutter/foundation.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

class AppSecrets {
  // Environment configuration
  static const bool isProduction = bool.fromEnvironment(
    'IS_PRODUCTION',
    defaultValue: false,
  );

  // Supabase configuration (safe for all platforms)
  static final String supabaseUrl = dotenv.env['SUPABASE_URL'] ?? '';
  static final String supabaseAnonKey = dotenv.env['SUPABASE_ANON_KEY'] ?? '';
  static final String backendUrl = dotenv.env['BACKEND_URL'] ?? '';

  // Razorpay configuration (platform-specific)
  // ⚠️ Key Secret is NEVER exposed on web builds for security
  static String? get razorpayKeyId {
    if (kIsWeb) {
      // For web builds, get key from backend
      return null;
    }
    // For mobile/desktop builds, use environment variable
    return dotenv.env['RAZORPAY_KEY_ID'];
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
