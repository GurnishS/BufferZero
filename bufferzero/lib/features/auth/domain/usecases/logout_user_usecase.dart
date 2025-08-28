import 'package:bufferzero/core/error/failures.dart';
import 'package:bufferzero/core/usecase/usecase.dart';
import 'package:bufferzero/features/auth/domain/repository/auth_repository.dart';
import 'package:fpdart/fpdart.dart';

class LogoutUserUsecase extends UseCase<void, NoParams> {
  final AuthRepository authRepository;

  LogoutUserUsecase(this.authRepository);

  @override
  Future<Either<Failure, void>> call(NoParams params) {
    return authRepository.logout();
  }
}
