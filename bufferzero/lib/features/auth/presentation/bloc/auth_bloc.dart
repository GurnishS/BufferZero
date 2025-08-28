import 'package:bufferzero/core/common/cubit/app_user_cubit.dart';
import 'package:bufferzero/core/usecase/usecase.dart';
import 'package:bufferzero/core/common/entities/user.dart';
import 'package:bufferzero/features/auth/domain/usecases/anonymous_sign_in.dart';
import 'package:bufferzero/features/auth/domain/usecases/current_user.dart';
import 'package:bufferzero/features/auth/domain/usecases/logout_user_usecase.dart';
import 'package:bufferzero/features/auth/domain/usecases/user_sign_in.dart';
import 'package:bufferzero/features/auth/domain/usecases/user_sign_up.dart';
import 'package:bufferzero/features/auth/domain/usecases/google_sign_in.dart';
import 'package:bufferzero/features/auth/domain/usecases/resend_email_verification.dart';
import 'package:bufferzero/core/error/failures.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

part 'auth_event.dart';
part 'auth_state.dart';

class AuthBloc extends Bloc<AuthEvent, AuthState> {
  final UserSignUp _userSignUp;
  final UserSignIn _userSignIn;
  final GoogleSignIn _googleSignIn;
  final AnonymousSignIn _anonymousSignIn;
  final CurrentUser _currentUser;
  final ResendEmailVerification _resendEmailVerification;
  final LogoutUserUsecase _logoutUserUsecase;
  final AppUserCubit _appUserCubit;

  AuthBloc({
    required UserSignUp userSignUp,
    required UserSignIn userSignIn,
    required CurrentUser currentUser,
    required AppUserCubit appUserCubit,
    required GoogleSignIn googleSignIn,
    required AnonymousSignIn anonymousSignIn,
    required ResendEmailVerification resendEmailVerification,
    required LogoutUserUsecase logoutUserUsecase,
  }) : _userSignUp = userSignUp,
       _userSignIn = userSignIn,
       _currentUser = currentUser,
       _appUserCubit = appUserCubit,
       _googleSignIn = googleSignIn,
       _anonymousSignIn = anonymousSignIn,
       _resendEmailVerification = resendEmailVerification,
       _logoutUserUsecase = logoutUserUsecase,
       super(AuthInitial()) {
    on<AuthSignUp>(_onAuthSignUp);
    on<AuthSignIn>(_onAuthSignIn);
    on<AuthSignInWithGoogle>(_onAuthSignInWithGoogle);
    on<AuthUserLoggedIn>(_onAuthUserLoggedIn);
    on<AuthSignInAnonymously>(_onAuthSignInAnonymously);
    on<AuthResendEmailVerification>(_onAuthResendEmailVerification);
    on<AuthCheckEmailVerification>(_onAuthCheckEmailVerification);
    on<AuthLogout>(_onAuthLogout);
    on<ResetAuthState>(_onResetAuthState);
  }

  Future<void> _onResetAuthState(
    ResetAuthState event,
    Emitter<AuthState> emit,
  ) async {
    emit(AuthInitial());
  }

  Future<void> _onAuthLogout(AuthLogout event, Emitter<AuthState> emit) async {
    emit(AuthLoading());
    final res = await _logoutUserUsecase(NoParams());
    res.fold((failure) => emit(AuthFailure(failure.message)), (_) {
      _appUserCubit.updateUser(null);
      emit(AuthInitial());
    });
  }

  Future<void> _onAuthSignInWithGoogle(
    AuthSignInWithGoogle event,
    Emitter<AuthState> emit,
  ) async {
    emit(AuthLoading());
    final res = await _googleSignIn(NoParams());
    res.fold(
      (failure) => emit(AuthFailure(failure.message)),
      (user) => _emitAuthSuccess(user, emit),
    );
  }

  Future<void> _onAuthSignInAnonymously(
    AuthSignInAnonymously event,
    Emitter<AuthState> emit,
  ) async {
    emit(AuthLoading());
    final res = await _anonymousSignIn(NoParams());
    res.fold(
      (failure) => emit(AuthFailure(failure.message)),
      (user) => _emitAuthSuccess(user, emit),
    );
  }

  Future<void> _onAuthUserLoggedIn(
    AuthUserLoggedIn event,
    Emitter<AuthState> emit,
  ) async {
    final res = await _currentUser(NoParams());

    res.fold(
      (failure) => emit(AuthFailure(failure.message)),
      (user) => _emitAuthSuccess(user, emit),
    );
  }

  Future<void> _onAuthSignUp(AuthSignUp event, Emitter<AuthState> emit) async {
    emit(AuthLoading());
    final params = UserSignUpParams(
      name: event.name,
      email: event.email,
      password: event.password,
    );

    final res = await _userSignUp(params);

    res.fold((failure) {
      if (failure is EmailVerificationFailure) {
        emit(AuthEmailVerificationInitial(failure.email));
      } else {
        emit(AuthFailure(failure.message));
      }
    }, (user) => _emitAuthSuccess(user, emit));
  }

  Future<void> _onAuthSignIn(AuthSignIn event, Emitter<AuthState> emit) async {
    emit(AuthLoading());
    final params = UserSignInParams(
      email: event.email,
      password: event.password,
    );

    final res = await _userSignIn(params);

    res.fold(
      (failure) => emit(AuthFailure(failure.message)),
      (user) => _emitAuthSuccess(user, emit),
    );
  }

  Future<void> _onAuthCheckEmailVerification(
    AuthCheckEmailVerification event,
    Emitter<AuthState> emit,
  ) async {
    // Check current user status to see if email is verified
    final res = await _currentUser(NoParams());
    res.fold(
      (failure) => emit(AuthFailure(failure.message)),
      (user) => _emitAuthSuccess(user, emit),
    );
  }

  void _emitAuthSuccess(User user, Emitter<AuthState> emit) {
    _appUserCubit.updateUser(user);
    emit(AuthSuccess(user));
  }

  Future<void> _onAuthResendEmailVerification(
    AuthResendEmailVerification event,
    Emitter<AuthState> emit,
  ) async {
    emit(AuthResendEmailVerificationLoading(event.email));
    final params = ResendEmailVerificationParams(email: event.email);
    final res = await _resendEmailVerification(params);

    res.fold(
      (failure) => emit(
        AuthResendEmailVerificationFailure(event.email, failure.message),
      ),
      (_) => emit(AuthResendEmailVerificationSuccess(event.email)),
    );
  }
}
