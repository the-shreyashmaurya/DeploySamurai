import 'dart:convert';

import 'package:deploysamourai/data/api/deploy_samurai_api_client.dart';
import 'package:deploysamourai/data/repositories/api_deploy_dashboard_repository.dart';
import 'package:deploysamourai/domain/entities/dashboard_snapshot.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

void main() {
  test(
    'analyzeRepository calls backend workflow and maps dashboard state',
    () async {
      final requestedPaths = <String>[];
      final client = MockClient((request) async {
        requestedPaths.add(request.url.path);

        switch (request.url.path) {
          case '/v1/jobs':
            return _json({
              'job_id': 'job_123',
              'status': 'queued',
              'mode': 'advisor',
            });
          case '/v1/analyze/repo':
            return _json({
              'repo_summary': {
                'name': 'orders-api',
                'default_branch': 'main',
                'language': 'python',
                'framework': 'fastapi',
                'package_manager': 'uv',
                'has_tests': true,
              },
              'structure': {
                'root_files': ['pyproject.toml'],
                'folder_tree': ['app', 'workers'],
                'entrypoints': ['app/main.py'],
              },
            });
          case '/v1/reason/architecture':
            return _json({
              'architecture_type': 'microservices',
              'summary': 'Split API and worker boundaries.',
              'service_candidates': [
                {
                  'name': 'api',
                  'responsibility': 'Serve HTTP requests',
                  'runtime': 'lambda',
                },
                {
                  'name': 'worker',
                  'responsibility': 'Process async jobs',
                  'runtime': 'lambda',
                  'data_store': 'dynamodb',
                },
              ],
              'communication_flows': [
                {
                  'from': 'api',
                  'to': 'worker',
                  'style': 'async',
                  'transport': 'sqs',
                },
              ],
              'notes': ['Review boundaries before deployment.'],
            });
          case '/v1/deploy/preflight':
            return _json({
              'status': 'passed',
              'region': 'us-east-1',
              'account_id': '123456789012',
              'arn': 'arn:aws:iam::123456789012:user/deploy-samurai',
              'message': 'AWS credentials are valid.',
            });
          case '/v1/verify':
            return _json({
              'status': 'passed',
              'checks': [
                {
                  'name': 'stack_status',
                  'status': 'skipped',
                  'evidence': 'Stack status check skipped.',
                  'evidence_items': [],
                },
                {
                  'name': 'endpoint_smoke',
                  'status': 'skipped',
                  'evidence': 'Endpoint smoke checks skipped.',
                  'evidence_items': [],
                },
              ],
            });
        }

        return http.Response('Not found', 404);
      });
      final repository = ApiDeployDashboardRepository(
        DeploySamuraiApiClient(
          httpClient: client,
          baseUrl: 'http://127.0.0.1:8000/v1',
        ),
      );

      final snapshot = await repository.analyzeRepository(
        repoUrl: 'https://github.com/acme/orders-api',
        mode: AnalysisMode.advisor,
      );

      expect(requestedPaths, [
        '/v1/jobs',
        '/v1/analyze/repo',
        '/v1/reason/architecture',
        '/v1/deploy/preflight',
        '/v1/verify',
      ]);
      expect(snapshot.runStatus, DashboardRunStatus.succeeded);
      expect(snapshot.jobId, 'job_123');
      expect(snapshot.architectureSummary, 'Split API and worker boundaries.');
      expect(snapshot.architectureResources, hasLength(2));
      expect(snapshot.architectureConnections, hasLength(1));
      expect(
        snapshot.samPlanSummary,
        contains('AWS credential preflight passed in us-east-1'),
      );
      expect(snapshot.stackFacts.any((fact) => fact.label == 'Verification'), isTrue);
    },
  );
}

http.Response _json(Map<String, Object?> body) {
  return http.Response(
    jsonEncode(body),
    200,
    headers: {'Content-Type': 'application/json'},
  );
}
