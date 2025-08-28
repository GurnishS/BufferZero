import 'package:bufferzero/features/auth/presentation/bloc/auth_bloc.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          children: [
            const Text('Home Page'),
            TextButton(
              onPressed: () {
                context.read<AuthBloc>().add(ResetAuthState());
                context.go("/sign-in");
              },
              child: const Text('Sign In'),
            ),
            TextButton(
              onPressed: () {
                context.go("/sign-up");
              },
              child: const Text('Sign Up'),
            ),
          ],
        ),
      ),
    );
  }
}
