part of 'auth_bloc.dart';

@immutable
sealed class AuthState {
  const AuthState();
}

final class AuthInitial extends AuthState {}

final class AuthLoading extends AuthState {}

final class AuthSuccess extends AuthState {
  final User user;
  const AuthSuccess(this.user);

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is AuthSuccess && other.user == user;
  }

  @override
  int get hashCode => user.hashCode;
}

final class AuthFailure extends AuthState {
  final String message;
  const AuthFailure(this.message);

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is AuthFailure && other.message == message;
  }

  @override
  int get hashCode => message.hashCode;
}

@immutable
sealed class EmailVerification extends AuthState {
  final String email;
  const EmailVerification(this.email);

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is EmailVerification && other.email == email;
  }

  @override
  int get hashCode => email.hashCode;
}

final class AuthEmailVerificationInitial extends EmailVerification {
  const AuthEmailVerificationInitial(super.email);
}

final class AuthResendEmailVerificationLoading extends EmailVerification {
  const AuthResendEmailVerificationLoading(super.email);
}

final class AuthResendEmailVerificationSuccess extends EmailVerification {
  const AuthResendEmailVerificationSuccess(super.email);
}

final class AuthResendEmailVerificationFailure extends EmailVerification {
  final String message;
  const AuthResendEmailVerificationFailure(super.email, this.message);

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is AuthResendEmailVerificationFailure &&
        other.email == email &&
        other.message == message;
  }

  @override
  int get hashCode => Object.hash(email, message);
}
