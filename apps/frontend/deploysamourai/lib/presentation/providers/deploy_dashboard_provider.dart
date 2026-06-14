import 'package:flutter/foundation.dart';

import '../../domain/entities/dashboard_snapshot.dart';
import '../../domain/repositories/deploy_dashboard_repository.dart';

class DeployDashboardProvider extends ChangeNotifier {
  DeployDashboardProvider(this._repository);

  final DeployDashboardRepository _repository;

  DashboardSnapshot? _snapshot;
  bool _isLoading = true;

  bool get isLoading => _isLoading;

  DashboardSnapshot get snapshot {
    final value = _snapshot;
    if (value == null) {
      throw StateError('Dashboard snapshot has not loaded.');
    }
    return value;
  }

  void load() {
    _snapshot = _repository.loadSnapshot();
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

  void analyzeRepository() {
    _snapshot = snapshot.copyWith(elapsed: '00:00:29');
    notifyListeners();
  }
}
