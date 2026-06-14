import 'dart:convert';

import 'package:deploysamourai/data/api/deploy_samurai_api_client.dart';
import 'package:deploysamourai/data/repositories/api_deploy_dashboard_repository.dart';
import 'package:deploysamourai/domain/entities/dashboard_snapshot.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

void main() {
  test(
    'analyzeRepository calls analysis workflow and maps dashboard state',
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
          case '/v1/sam/generate':
            return _json({
              'files': [
                {
                  'path': 'artifacts/job_123/template.yaml',
                  'content_type': 'text/yaml',
                  'purpose': 'sam_template',
                },
                {
                  'path': 'artifacts/job_123/src/api/app.py',
                  'content_type': 'text/x-python',
                  'purpose': 'lambda_handler',
                },
              ],
              'artifacts': {
                'template_path': 'artifacts/job_123/template.yaml',
                'handler_paths': ['artifacts/job_123/src/api/app.py'],
                'resource_summaries': [
                  {
                    'logical_id': 'HttpApi',
                    'resource_type': 'AWS::Serverless::HttpApi',
                    'service_name': null,
                    'reason': 'Expose synchronous service endpoints',
                  },
                  {
                    'logical_id': 'ApiFunction',
                    'resource_type': 'AWS::Serverless::Function',
                    'service_name': 'api',
                    'reason': 'Serve HTTP requests',
                  },
                ],
              },
              'handlers': [],
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
        '/v1/sam/generate',
      ]);
      expect(snapshot.runStatus, DashboardRunStatus.succeeded);
      expect(snapshot.jobId, 'job_123');
      expect(snapshot.architectureSummary, 'Split API and worker boundaries.');
      expect(snapshot.architectureResources, hasLength(2));
      expect(snapshot.architectureConnections, hasLength(1));
      expect(snapshot.artifacts.first.name, 'template.yaml');
      expect(
        snapshot.artifacts.first.downloadUrl,
        endsWith('/v1/sam/artifacts/job_123/template.yaml'),
      );
      expect(snapshot.samPlanSummary, contains('Generated template.yaml'));
      expect(
        snapshot.statusMessage,
        'Analysis completed. Review the architecture and SAM plan before deployment.',
      );
      expect(
        snapshot.stackFacts.any((fact) => fact.label == 'Verification'),
        isFalse,
      );
    },
  );

  test('loadSnapshot starts without a fake repository URL', () async {
    final repository = ApiDeployDashboardRepository(
      DeploySamuraiApiClient(
        httpClient: MockClient((request) async {
          return http.Response('Not found', 404);
        }),
        baseUrl: 'http://127.0.0.1:8000/v1',
      ),
    );

    final snapshot = await repository.loadSnapshot();

    expect(snapshot.repoUrl, isEmpty);
  });

  test(
    'approveAndDeploy calls deployment and verification endpoints',
    () async {
      final requestedPaths = <String>[];
      final client = MockClient((request) async {
        requestedPaths.add(request.url.path);

        switch (request.url.path) {
          case '/v1/deploy/sam':
            return _json({
              'deployment_id': 'dep_123',
              'status': 'succeeded',
              'stack_name': 'deploy-samurai-job-123',
              'outputs': {'ApiUrl': 'https://api.example.com'},
              'logs': ['sam build exited 0: ok', 'sam deploy exited 0: ok'],
            });
          case '/v1/verify':
            return _json({
              'status': 'passed',
              'checks': [
                {
                  'name': 'stack_status',
                  'status': 'passed',
                  'evidence': 'Stack is CREATE_COMPLETE.',
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

      final snapshot = await repository.approveAndDeploy(
        current: buildDeployableSnapshot(),
      );

      expect(requestedPaths, ['/v1/deploy/sam', '/v1/verify']);
      expect(snapshot.runStatus, DashboardRunStatus.succeeded);
      expect(snapshot.statusMessage, 'Deployment completed successfully.');
      expect(snapshot.stackFacts.any((fact) => fact.label == 'Stack'), isTrue);
    },
  );
}

DashboardSnapshot buildDeployableSnapshot() {
  return const DashboardSnapshot(
    jobId: 'job_123',
    repoUrl: 'https://github.com/acme/orders-api',
    selectedMode: AnalysisMode.advisor,
    region: 'AWS - us-east-1',
    version: 'v2.4.1',
    connected: true,
    runStatus: DashboardRunStatus.succeeded,
    elapsed: 'live',
    statusMessage: 'Analysis completed.',
    pipelineSteps: [
      PipelineStep(
        title: 'Intake',
        caption: 'Completed',
        status: PipelineStepStatus.completed,
      ),
      PipelineStep(
        title: 'Clone',
        caption: 'Completed',
        status: PipelineStepStatus.completed,
      ),
      PipelineStep(
        title: 'Detect Stack',
        caption: 'Completed',
        status: PipelineStepStatus.completed,
      ),
      PipelineStep(
        title: 'Boundaries',
        caption: 'Completed',
        status: PipelineStepStatus.completed,
      ),
      PipelineStep(
        title: 'SAM Plan',
        caption: 'Completed',
        status: PipelineStepStatus.completed,
      ),
      PipelineStep(
        title: 'Approval',
        caption: 'Pending',
        status: PipelineStepStatus.locked,
      ),
      PipelineStep(
        title: 'Deploy',
        caption: 'Pending',
        status: PipelineStepStatus.pending,
      ),
      PipelineStep(
        title: 'Verify',
        caption: 'Pending',
        status: PipelineStepStatus.pending,
      ),
    ],
    architectureResources: [],
    architectureConnections: [],
    stackFacts: [],
    artifacts: [
      SamArtifact(
        name: 'template.yaml',
        size: '2 resources',
        isFolder: false,
        artifactPath: 'artifacts/job_123/template.yaml',
        downloadUrl:
            'http://127.0.0.1:8000/v1/sam/artifacts/job_123/template.yaml',
      ),
    ],
    consoleLogs: [],
    samPlanSummary: ['Generated template.yaml'],
    architectureSummary: 'Architecture summary.',
    notes: [],
  );
}

http.Response _json(Map<String, Object?> body) {
  return http.Response(
    jsonEncode(body),
    200,
    headers: {'Content-Type': 'application/json'},
  );
}
