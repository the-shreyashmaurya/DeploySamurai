import 'dart:async';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:provider/provider.dart';

import 'core/config/api_config.dart';
import 'data/api/deploy_samurai_api_client.dart';
import 'data/repositories/api_deploy_dashboard_repository.dart';
import 'domain/repositories/deploy_dashboard_repository.dart';
import 'presentation/app/deploy_samurai_app.dart';
import 'presentation/providers/deploy_dashboard_provider.dart';

void main() {
  runApp(const DeploySamuraiBootstrap());
}

class DeploySamuraiBootstrap extends StatelessWidget {
  const DeploySamuraiBootstrap({super.key, this.repository});

  final DeployDashboardRepository? repository;

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        Provider<DeployDashboardRepository>(
          create: (_) =>
              repository ??
              ApiDeployDashboardRepository(
                DeploySamuraiApiClient(
                  httpClient: http.Client(),
                  baseUrl: ApiConfig.baseUrl,
                ),
              ),
        ),
        ChangeNotifierProvider<DeployDashboardProvider>(
          create: (context) {
            final repository = context.read<DeployDashboardRepository>();
            final provider = DeployDashboardProvider(repository);
            unawaited(provider.load());
            return provider;
          },
        ),
      ],
      child: const DeploySamuraiApp(),
    );
  }
}
