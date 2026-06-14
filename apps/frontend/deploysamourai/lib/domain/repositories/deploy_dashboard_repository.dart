import '../entities/dashboard_snapshot.dart';

abstract class DeployDashboardRepository {
  DashboardSnapshot loadSnapshot();
}
