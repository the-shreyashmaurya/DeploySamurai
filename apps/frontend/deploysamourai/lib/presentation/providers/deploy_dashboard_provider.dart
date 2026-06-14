import 'package:flutter/foundation.dart';

import '../../domain/entities/dashboard_snapshot.dart';
import '../../domain/repositories/deploy_dashboard_repository.dart';

class DeployDashboardProvider extends ChangeNotifier {
  DeployDashboardProvider(this._repository);

  final DeployDashboardRepository _repository;

  DashboardSnapshot? _snapshot;
  bool _isLoading = true;
  bool _isAnalyzing = false;

  bool get isLoading => _isLoading;
  bool get isAnalyzing => _isAnalyzing;

  DashboardSnapshot get snapshot {
    final value = _snapshot;
    if (value == null) {
      throw StateError('Dashboard snapshot has not loaded.');
    }
    return value;
  }

  Future<void> load() async {
    _snapshot = await _repository.loadSnapshot();
    _isLoading = false;
    notifyListeners();
  }

  void setRepoUrl(String repoUrl) {
    _snapshot = snapshot.copyWith(repoUrl: repoUrl);
    notifyListeners();
  }

  void selectMode(AnalysisMode mode) {
    _snapshot = snapshot.copyWith(selectedMode: mode);
    notifyListeners();
  }

  Future<void> analyzeRepository() async {
    final repoUrl = snapshot.repoUrl.trim();
    if (repoUrl.isEmpty || _isAnalyzing) {
      return;
    }

    _isAnalyzing = true;
    _snapshot = snapshot.copyWith(
      runStatus: DashboardRunStatus.running,
      statusMessage: 'Connecting to DeploySamurai API...',
    );
    notifyListeners();

    _snapshot = await _repository.analyzeRepository(
      repoUrl: repoUrl,
      mode: snapshot.selectedMode,
    );
    _isAnalyzing = false;
    notifyListeners();
  }
}
