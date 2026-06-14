import 'package:deploysamourai/main.dart';
import 'package:deploysamourai/data/repositories/mock_deploy_dashboard_repository.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('renders DeploySamurai dashboard', (tester) async {
    await tester.pumpWidget(
      DeploySamuraiBootstrap(repository: MockDeployDashboardRepository()),
    );
    await tester.pumpAndSettle();

    expect(find.text('DeploySamurai'), findsWidgets);
    expect(find.text('Analyze Repo'), findsWidgets);
    expect(find.text('Architecture Preview'), findsWidgets);
    expect(find.byIcon(Icons.auto_awesome_rounded), findsWidgets);
  });
}
