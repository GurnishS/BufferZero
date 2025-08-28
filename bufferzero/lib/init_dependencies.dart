import 'package:bufferzero/core/common/cubit/app_user_cubit.dart';
import 'package:bufferzero/core/secrets/app_secrets.dart';
import 'package:bufferzero/features/auth/data/datasources/auth_remote_data_source.dart';
import 'package:bufferzero/features/auth/data/repositories/auth_repository_impl.dart';
import 'package:bufferzero/features/auth/domain/repository/auth_repository.dart';
import 'package:bufferzero/features/auth/domain/usecases/anonymous_sign_in.dart';
import 'package:bufferzero/features/auth/domain/usecases/current_user.dart';
import 'package:bufferzero/features/auth/domain/usecases/google_sign_in.dart';
import 'package:bufferzero/features/auth/domain/usecases/resend_email_verification.dart';
import 'package:bufferzero/features/auth/domain/usecases/user_sign_in.dart';
import 'package:bufferzero/features/auth/domain/usecases/user_sign_up.dart';
import 'package:bufferzero/features/auth/presentation/bloc/auth_bloc.dart';
import 'package:bufferzero/features/auth/domain/usecases/logout_user_usecase.dart';
import 'package:get_it/get_it.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

final serviceLocator = GetIt.instance;

Future<void> initDependencies() async {
  // Initialize external dependencies first
  final supabase = await Supabase.initialize(
    url: AppSecrets.supabaseUrl,
    anonKey: AppSecrets.supabaseAnonKey,
  );
  serviceLocator.registerLazySingleton(() => supabase.client);

  //core
  serviceLocator.registerLazySingleton(() => AppUserCubit());

  //auth
  _initAuth();
  //dashboard
}

void _initAuth() {
  serviceLocator
    // Datasource
    ..registerFactory<AuthRemoteDataSource>(
      () => AuthRemoteDataSourceImpl(supabaseClient: serviceLocator()),
    )
    // Repository
    ..registerFactory<AuthRepository>(
      () => AuthRepositoryImpl(serviceLocator()),
    )
    //Use cases
    ..registerFactory(() => UserSignUp(serviceLocator()))
    ..registerFactory(() => UserSignIn(serviceLocator()))
    ..registerFactory(() => GoogleSignIn(serviceLocator()))
    ..registerFactory(() => AnonymousSignIn(serviceLocator()))
    ..registerFactory(() => CurrentUser(serviceLocator()))
    ..registerFactory(() => ResendEmailVerification(serviceLocator()))
    ..registerFactory(() => LogoutUserUsecase(serviceLocator()))
    // Bloc
    ..registerLazySingleton(
      () => AuthBloc(
        userSignUp: serviceLocator(),
        userSignIn: serviceLocator(),
        currentUser: serviceLocator(),
        appUserCubit: serviceLocator(),
        googleSignIn: serviceLocator(),
        anonymousSignIn: serviceLocator(),
        resendEmailVerification: serviceLocator(),
        logoutUserUsecase: serviceLocator(),
      ),
    );
}
