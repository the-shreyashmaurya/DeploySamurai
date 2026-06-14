import '../../domain/entities/dashboard_snapshot.dart';
import '../../domain/repositories/deploy_dashboard_repository.dart';
import '../api/deploy_samurai_api_client.dart';
import '../mappers/dashboard_snapshot_mapper.dart';

class ApiDeployDashboardRepository implements DeployDashboardRepository {
  ApiDeployDashboardRepository(this._apiClient);

  final DeploySamuraiApiClient _apiClient;

  @override
  Future<DashboardSnapshot> loadSnapshot() async {
    return buildInitialDashboardSnapshot();
  }

  @override
  Future<DashboardSnapshot> analyzeRepository({
    required String repoUrl,
    required AnalysisMode mode,
  }) async {
    final initial = buildRunningDashboardSnapshot(
      current: buildInitialDashboardSnapshot(),
      repoUrl: repoUrl,
      mode: mode,
    );

    try {
      final job = await _apiClient.createJob(repoUrl: repoUrl, mode: mode);
      final analysis = await _apiClient.analyzeRepo(
        repoUrl: repoUrl,
        jobId: job.jobId,
      );
      final architecture = await _apiClient.reasonArchitecture(
        jobId: job.jobId,
        analysis: analysis,
      );
      final sam = await _apiClient.generateSamArtifacts(
        jobId: job.jobId,
        architecture: architecture,
      );
      return buildAnalyzedDashboardSnapshot(
        current: initial,
        job: job,
        analysis: analysis,
        architecture: architecture,
        sam: sam,
      );
    } catch (error) {
      return buildFailedDashboardSnapshot(current: initial, error: error);
    }
  }
}
