class AppSecrets {
  // Environment configuration
  static const bool isProduction = false;

  // Supabase configuration (safe for all platforms)
  static const String supabaseUrl = "https://rwnparhykrxgdbduoqvy.supabase.co";
  static const String supabaseAnonKey =
      "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ3bnBhcmh5a3J4Z2RiZHVvcXZ5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTIwNzc4MjQsImV4cCI6MjA2NzY1MzgyNH0.c1qbN3pai99a0-iGQKsLDXhI8QPf5npyZP7dbBpLTSg";
  static const String backendUrl = "http://127.0.0.1:8000";

  // Razorpay configuration (platform-specific)
  // ⚠️ Key Secret is NEVER exposed on web builds for security
  static const String razorpayKeyId = "rzp_test_y44HHuzJuuauzV";
}

// import 'package:flutter/foundation.dart';

// class AppSecrets {
//   // Environment configuration
//   static const bool isProduction = bool.fromEnvironment(
//     'IS_PRODUCTION',
//     defaultValue: false,
//   );

//   // Supabase configuration (safe for all platforms)
//   static const String supabaseUrl = String.fromEnvironment('SUPABASE_URL');
//   static const String supabaseAnonKey = String.fromEnvironment(
//     'SUPABASE_ANON_KEY',
//   );
//   static const String backendUrl = String.fromEnvironment('BACKEND_URL');

//   // Razorpay configuration (platform-specific)
//   // ⚠️ Key Secret is NEVER exposed on web builds for security
//   static String? get razorpayKeyId {
//     if (kIsWeb) {
//       // For web builds, get key from backend
//       return null;
//     }
//     // For mobile/desktop builds, use environment variable
//     return const String.fromEnvironment('RAZORPAY_KEY_ID');
//   }

//   // static String? get razorpayKeySecret {
//   //   if (kIsWeb) {
//   //     // NEVER expose secret on web builds
//   //     return null;
//   //   }
//   //   // Only available on mobile/desktop builds
//   //   return const String.fromEnvironment('RAZORPAY_KEY_SECRET');
//   // }

//   // Backend endpoint for web payments
//   static String get paymentEndpoint {
//     return '$backendUrl/api/payments';
//   }

//   // Check if Razorpay is properly configured for current platform
//   static bool get isRazorpayConfigured {
//     if (kIsWeb) {
//       // Web should use backend payment flow
//       return backendUrl.isNotEmpty;
//     }
//     // Mobile/desktop can use direct Razorpay integration
//     return razorpayKeyId?.isNotEmpty == true;
//   }
// }
