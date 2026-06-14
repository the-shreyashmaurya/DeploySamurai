import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'data/repositories/mock_deploy_dashboard_repository.dart';
import 'domain/repositories/deploy_dashboard_repository.dart';
import 'presentation/app/deploy_samurai_app.dart';
import 'presentation/providers/deploy_dashboard_provider.dart';

void main() {
  runApp(const DeploySamuraiBootstrap());
}

class DeploySamuraiBootstrap extends StatelessWidget {
  const DeploySamuraiBootstrap({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        Provider<DeployDashboardRepository>(
          create: (_) => MockDeployDashboardRepository(),
        ),
        ChangeNotifierProvider<DeployDashboardProvider>(
          create: (context) {
            final repository = context.read<DeployDashboardRepository>();
            return DeployDashboardProvider(repository)..load();
          },
        ),
      ],
      child: const DeploySamuraiApp(),
    );
  }
}
