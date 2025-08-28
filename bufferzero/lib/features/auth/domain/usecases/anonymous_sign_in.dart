import 'package:bufferzero/core/common/entities/user.dart';
import 'package:bufferzero/core/error/failures.dart';
import 'package:bufferzero/core/usecase/usecase.dart';
import 'package:bufferzero/features/auth/domain/repository/auth_repository.dart';
import 'package:fpdart/fpdart.dart';

class AnonymousSignIn implements UseCase<User, NoParams> {
  final AuthRepository authRepository;
  const AnonymousSignIn(this.authRepository);
  @override
  Future<Either<Failure, User>> call(NoParams params) async {
    return await authRepository.signInAnonymously();
  }
}
