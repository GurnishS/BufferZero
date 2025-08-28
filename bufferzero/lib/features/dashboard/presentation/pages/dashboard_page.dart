import 'package:bufferzero/core/common/cubit/app_user_cubit.dart';
import 'package:bufferzero/features/auth/presentation/bloc/auth_bloc.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

class DashboardPage extends StatelessWidget {
  final AppUserCubit appUserCubit;

  const DashboardPage({super.key, required this.appUserCubit});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('Dashboard'),
            SizedBox(height: 16),
            ElevatedButton(
              onPressed: () {
                context.read<AuthBloc>().add(AuthLogout());
              },
              child: Text('Log Out'),
            ),
          ],
        ),
      ),
    );
  }
}
