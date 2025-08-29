import 'package:bufferzero/core/error/failures.dart';
import 'package:bufferzero/core/usecase/usecase.dart';
import 'package:bufferzero/features/auth/domain/repository/auth_repository.dart';
import 'package:fpdart/fpdart.dart';

class SendPasswordResetEmail extends UseCase<void, String> {
  final AuthRepository authRepository;

  SendPasswordResetEmail(this.authRepository);

  @override
  Future<Either<Failure, void>> call(String email) async {
    return await authRepository.sendPasswordResetEmail(email: email);
  }
}
