import 'package:bufferzero/core/error/failures.dart';
import 'package:bufferzero/core/usecase/usecase.dart';
import 'package:bufferzero/core/common/entities/user.dart' show User;
import 'package:bufferzero/features/auth/domain/repository/auth_repository.dart';
import 'package:fpdart/fpdart.dart';

class CurrentUser implements UseCase<User, NoParams> {
  final AuthRepository authRepository;

  CurrentUser(this.authRepository);

  @override
  Future<Either<Failure, User>> call(NoParams params) async {
    return await authRepository.currentUser();
  }
}
