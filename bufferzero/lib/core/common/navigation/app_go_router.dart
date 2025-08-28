import 'package:bufferzero/core/common/cubit/app_user_cubit.dart';
import 'package:bufferzero/features/auth/presentation/pages/sign_in_page.dart';
import 'package:bufferzero/features/auth/presentation/pages/sign_up_page.dart';
import 'package:bufferzero/features/dashboard/presentation/pages/dashboard_page.dart';
import 'package:bufferzero/features/home/presentation/pages/home_page.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'dart:async';

class AppGoRouter {
  static GoRouter createRouter(AppUserCubit appUserCubit) {
    return GoRouter(
      debugLogDiagnostics: true,
      initialLocation: '/',
      refreshListenable: AppUserChangeNotifier(appUserCubit),
      redirect: (context, state) {
        final isAuthenticated = appUserCubit.state is AppUserLoggedIn;
        print("Auth:|$isAuthenticated");

        final intendedLocation = state.uri.toString();

        final isGoingToHome = intendedLocation == '/';
        final isGoingToTest = intendedLocation == '/test';

        if (isGoingToTest) {
          return '/test';
        }

        if (isGoingToHome) {
          //Open Route
          return '/';
        }

        final isGoingToSignIn = intendedLocation.startsWith('/sign-in');
        final isGoingToSignUp = intendedLocation.startsWith('/sign-up');

        if (isAuthenticated) {
          return intendedLocation;
        }

        if (!isAuthenticated && !isGoingToSignIn && !isGoingToSignUp) {
          return '/sign-in?redirect=${Uri.encodeComponent(intendedLocation)}';
        }

        if (isAuthenticated && isGoingToSignIn) {
          final redirectUri =
              state.uri.queryParameters['redirect'] ?? '/dashboard';
          return redirectUri;
        }

        return null;
      },
      routes: [
        GoRoute(
          path: '/',
          name: 'home',
          builder: (context, state) => HomePage(),
        ),
        GoRoute(
          path: '/dashboard',
          name: 'dashboard',
          builder: (context, state) =>
              DashboardPage(appUserCubit: appUserCubit),
        ),
        GoRoute(
          path: '/sign-in',
          name: 'sign-in',
          builder: (context, state) {
            final redirectUrl =
                state.uri.queryParameters['redirect'] ?? '/dashboard';
            final newSignUp =
                state.uri.queryParameters['new-sign-up'] == 'true';
            return SignInPage(redirectUrl: redirectUrl, newSignUp: newSignUp);
          },
        ),
        GoRoute(
          path: '/sign-up',
          name: 'sign-up',
          builder: (context, state) {
            final redirectUrl =
                state.uri.queryParameters['redirect'] ?? '/dashboard';
            return SignUpPage(redirectUrl: redirectUrl);
          },
        ),
        GoRoute(
          path: '/test',
          name: 'test',
          builder: (context, state) {
            return SignUpPage(redirectUrl: '/dashboard');
          },
        ),
      ],
      errorBuilder: (context, state) => const ErrorPage(),
    );
  }
}

// Custom ChangeNotifier to listen to AppUserCubit state changes
class AppUserChangeNotifier extends ChangeNotifier {
  final AppUserCubit _appUserCubit;
  late final StreamSubscription _subscription;

  AppUserChangeNotifier(this._appUserCubit) {
    _subscription = _appUserCubit.stream.listen((_) {
      // Use addPostFrameCallback to prevent setState during build
      WidgetsBinding.instance.addPostFrameCallback((_) {
        notifyListeners();
      });
    });
  }

  @override
  void dispose() {
    _subscription.cancel();
    super.dispose();
  }
}

class ErrorPage extends StatelessWidget {
  const ErrorPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error, size: 64, color: Colors.red),
            const SizedBox(height: 16),
            const Text(
              '404 - Page Not Found',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            ElevatedButton(
              onPressed: () => context.go('/'),
              child: const Text('Go Home'),
            ),
          ],
        ),
      ),
    );
  }
}
