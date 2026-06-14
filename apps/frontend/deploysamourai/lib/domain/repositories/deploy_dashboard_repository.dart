import '../entities/dashboard_snapshot.dart';

abstract class DeployDashboardRepository {
  Future<DashboardSnapshot> loadSnapshot();

  Future<DashboardSnapshot> analyzeRepository({
    required String repoUrl,
    required AnalysisMode mode,
  });
}
