import '../../domain/entities/dashboard_snapshot.dart';
import '../api/deploy_samurai_api_client.dart';

DashboardSnapshot buildInitialDashboardSnapshot() {
  return const DashboardSnapshot(
    repoUrl: '',
    selectedMode: AnalysisMode.advisor,
    region: 'AWS - us-east-1',
    version: 'v2.4.1',
    connected: false,
    runStatus: DashboardRunStatus.idle,
    elapsed: '00:00:00',
    statusMessage: 'Enter a GitHub repository URL to start analysis.',
    pipelineSteps: [
      PipelineStep(
        title: 'Intake',
        caption: 'Pending',
        status: PipelineStepStatus.pending,
      ),
      PipelineStep(
        title: 'Clone',
        caption: 'Pending',
        status: PipelineStepStatus.pending,
      ),
      PipelineStep(
        title: 'Detect Stack',
        caption: 'Pending',
        status: PipelineStepStatus.pending,
      ),
      PipelineStep(
        title: 'Boundaries',
        caption: 'Pending',
        status: PipelineStepStatus.pending,
      ),
      PipelineStep(
        title: 'SAM Plan',
        caption: 'Pending',
        status: PipelineStepStatus.locked,
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
    stackFacts: [
      StackFact(label: 'Detected Stack', value: 'Not analyzed'),
      StackFact(label: 'Runtime', value: '--'),
      StackFact(label: 'Region', value: 'us-east-1'),
      StackFact(label: 'Components', value: '--'),
    ],
    artifacts: [],
    consoleLogs: [
      ConsoleLog(
        time: '00:00:00',
        level: 'INFO',
        message: 'Frontend ready. Backend API calls will run on Analyze Repo.',
      ),
    ],
    samPlanSummary: [
      'SAM generation API is not exposed yet',
      'Deployment remains approval-gated',
    ],
    architectureSummary: '',
    notes: [],
  );
}

DashboardSnapshot buildRunningDashboardSnapshot({
  required DashboardSnapshot current,
  required String repoUrl,
  required AnalysisMode mode,
}) {
  return current.copyWith(
    jobId: null,
    repoUrl: repoUrl,
    selectedMode: mode,
    connected: true,
    runStatus: DashboardRunStatus.running,
    elapsed: '00:00:00',
    statusMessage: 'Creating analysis job...',
    pipelineSteps: _pipeline([
      PipelineStepStatus.inProgress,
      PipelineStepStatus.pending,
      PipelineStepStatus.pending,
      PipelineStepStatus.pending,
      PipelineStepStatus.locked,
      PipelineStepStatus.locked,
      PipelineStepStatus.pending,
      PipelineStepStatus.pending,
    ]),
    consoleLogs: [
      _log('INFO', 'Creating advisor job for $repoUrl'),
      _log('INFO', 'Calling POST /v1/jobs'),
    ],
  );
}

DashboardSnapshot buildAnalyzedDashboardSnapshot({
  required DashboardSnapshot current,
  required JobCreateDto job,
  required RepoAnalysisDto analysis,
  required ArchitectureReasoningDto architecture,
  SamGenerationDto? sam,
  DeploymentPreflightDto? deploymentPreflight,
  VerificationResultDto? verification,
}) {
  final resources = _architectureResources(architecture);
  final connections = _architectureConnections(architecture);
  final deploymentPassed = deploymentPreflight?.passed;
  final verificationPassed = verification?.passed;
  final workflowFailed =
      deploymentPassed == false || verificationPassed == false;
  return current.copyWith(
    jobId: job.jobId,
    connected: true,
    runStatus: workflowFailed
        ? DashboardRunStatus.failed
        : DashboardRunStatus.succeeded,
    elapsed: 'live',
    statusMessage: workflowFailed
        ? 'Backend workflow completed with deployment or verification warnings.'
        : 'Analysis completed. Review the architecture and SAM plan before deployment.',
    pipelineSteps: _pipeline([
      PipelineStepStatus.completed,
      PipelineStepStatus.completed,
      PipelineStepStatus.completed,
      PipelineStepStatus.completed,
      sam == null ? PipelineStepStatus.locked : PipelineStepStatus.completed,
      PipelineStepStatus.locked,
      _optionalWorkflowStatus(deploymentPassed),
      _optionalWorkflowStatus(verificationPassed),
    ]),
    architectureResources: resources,
    architectureConnections: connections,
    stackFacts: [
      StackFact(
        label: 'Detected Stack',
        value: _stackLabel(analysis.repoSummary),
      ),
      StackFact(
        label: 'Runtime',
        value: _runtimeLabel(analysis.repoSummary.language),
      ),
      const StackFact(label: 'Region', value: 'us-east-1'),
      StackFact(label: 'Components', value: '${resources.length} services'),
      if (deploymentPreflight != null)
        StackFact(label: 'AWS Preflight', value: deploymentPreflight.status),
      if (verification != null)
        StackFact(label: 'Verification', value: verification.status),
    ],
    artifacts: _samArtifacts(sam),
    consoleLogs: [
      ...current.consoleLogs,
      _log('INFO', 'Job created: ${job.jobId} (${job.status})'),
      _log(
        'INFO',
        'Repository cloned and analyzed: ${analysis.repoSummary.name}',
      ),
      _log(
        'INFO',
        'Detected ${analysis.repoSummary.language ?? 'unknown'}'
            ' / ${analysis.repoSummary.framework ?? 'unknown'} stack',
      ),
      _log('INFO', 'Architecture type: ${architecture.architectureType}'),
      _log('INFO', 'Identified ${resources.length} candidate service(s)'),
      if (sam != null)
        _log('INFO', 'Generated SAM template: ${sam.templatePath}'),
      if (deploymentPreflight != null)
        _log('INFO', 'Deployment preflight: ${deploymentPreflight.message}'),
      if (deploymentPreflight?.accountId != null)
        _log('INFO', 'AWS account: ${deploymentPreflight!.accountId}'),
      if (verification != null)
        _log('INFO', 'Verification status: ${verification.status}'),
      if (verification != null)
        for (final check in verification.checks)
          _log(
            check.status == 'failed' ? 'ERROR' : 'INFO',
            '${check.name}: ${check.evidence ?? check.status}',
          ),
    ],
    samPlanSummary: [
      if (sam == null)
        'SAM generation API is not connected'
      else ...[
        'Generated template.yaml',
        '${sam.resourceSummaries.length} AWS resource recommendation(s)',
      ],
      'Deployment remains approval-gated',
      if (deploymentPreflight != null)
        'AWS credential preflight ${deploymentPreflight.status} '
            'in ${deploymentPreflight.region}',
      if (verification != null)
        'Verification returned ${verification.status} '
            'with ${verification.checks.length} check(s)',
      if (deploymentPreflight == null && verification == null)
        'Deployment and verification APIs are not connected',
    ],
    architectureSummary: architecture.summary,
    notes: architecture.notes,
  );
}

List<SamArtifact> _samArtifacts(SamGenerationDto? sam) {
  if (sam == null) {
    return const [];
  }
  return [
    SamArtifact(
      name: 'template.yaml',
      size: '${sam.resourceSummaries.length} resources',
      isFolder: false,
      downloadUrl: sam.templateDownloadUrl,
    ),
    for (final file in sam.files.where(
      (file) => file.purpose == 'lambda_handler',
    ))
      SamArtifact(
        name: _compactArtifactPath(file.path),
        size: 'handler',
        isFolder: false,
      ),
  ];
}

String _compactArtifactPath(String path) {
  final parts = path.split('/').where((part) => part.isNotEmpty).toList();
  if (parts.length <= 3) {
    return path;
  }
  return parts.sublist(parts.length - 3).join('/');
}

DashboardSnapshot buildFailedDashboardSnapshot({
  required DashboardSnapshot current,
  required Object error,
}) {
  return current.copyWith(
    connected: false,
    runStatus: DashboardRunStatus.failed,
    statusMessage: _friendlyError(error),
    pipelineSteps: _pipeline([
      PipelineStepStatus.completed,
      PipelineStepStatus.inProgress,
      PipelineStepStatus.pending,
      PipelineStepStatus.pending,
      PipelineStepStatus.locked,
      PipelineStepStatus.locked,
      PipelineStepStatus.pending,
      PipelineStepStatus.pending,
    ]),
    consoleLogs: [...current.consoleLogs, _log('ERROR', _friendlyError(error))],
  );
}

PipelineStepStatus _optionalWorkflowStatus(bool? passed) {
  if (passed == null) {
    return PipelineStepStatus.pending;
  }
  return passed ? PipelineStepStatus.completed : PipelineStepStatus.inProgress;
}

List<PipelineStep> _pipeline(List<PipelineStepStatus> statuses) {
  const titles = [
    'Intake',
    'Clone',
    'Detect Stack',
    'Boundaries',
    'SAM Plan',
    'Approval',
    'Deploy',
    'Verify',
  ];
  return [
    for (var index = 0; index < titles.length; index++)
      PipelineStep(
        title: titles[index],
        caption: _caption(statuses[index]),
        status: statuses[index],
      ),
  ];
}

String _caption(PipelineStepStatus status) {
  switch (status) {
    case PipelineStepStatus.completed:
      return 'Completed';
    case PipelineStepStatus.inProgress:
      return 'In Progress';
    case PipelineStepStatus.pending:
    case PipelineStepStatus.locked:
      return 'Pending';
  }
}

List<ArchitectureResource> _architectureResources(
  ArchitectureReasoningDto architecture,
) {
  final resources = <ArchitectureResource>[];
  for (final service in architecture.serviceCandidates) {
    resources.add(
      ArchitectureResource(
        id: service.name,
        title: _titleCase(service.name),
        caption: service.responsibility,
        type: _typeForService(service),
      ),
    );
  }
  if (resources.isEmpty) {
    resources.add(
      const ArchitectureResource(
        id: 'api',
        title: 'Application',
        caption: 'Backend service',
        type: ArchitectureResourceType.lambda,
      ),
    );
  }
  return resources.take(4).toList(growable: false);
}

List<ArchitectureConnection> _architectureConnections(
  ArchitectureReasoningDto architecture,
) {
  final ids = architecture.serviceCandidates
      .map((service) => service.name)
      .toSet();
  final connections = architecture.communicationFlows
      .where((flow) => ids.contains(flow.source) && ids.contains(flow.target))
      .map(
        (flow) =>
            ArchitectureConnection(fromId: flow.source, toId: flow.target),
      )
      .toList();
  if (connections.isNotEmpty) {
    return connections.take(4).toList(growable: false);
  }
  final services = architecture.serviceCandidates;
  if (services.length < 2) {
    return const [];
  }
  return [
    for (var index = 0; index < services.length - 1 && index < 3; index++)
      ArchitectureConnection(
        fromId: services[index].name,
        toId: services[index + 1].name,
      ),
  ];
}

ArchitectureResourceType _typeForService(ServiceCandidateDto service) {
  final name = service.name.toLowerCase();
  final responsibility = service.responsibility.toLowerCase();
  final dataStore = service.dataStore?.toLowerCase() ?? '';
  if (dataStore.contains('dynamo')) {
    return ArchitectureResourceType.dynamoDb;
  }
  if (name.contains('queue') ||
      name.contains('worker') ||
      responsibility.contains('async') ||
      responsibility.contains('job')) {
    return ArchitectureResourceType.sqs;
  }
  if (name.contains('api') || responsibility.contains('api')) {
    return ArchitectureResourceType.apiGateway;
  }
  return ArchitectureResourceType.lambda;
}

String _stackLabel(RepoSummaryDto summary) {
  final parts = [
    summary.language,
    summary.framework,
    summary.packageManager,
  ].whereType<String>().where((value) => value.isNotEmpty).toList();
  if (parts.isEmpty) {
    return 'Unknown';
  }
  return parts.map(_titleCase).join(' / ');
}

String _runtimeLabel(String? language) {
  switch (language?.toLowerCase()) {
    case 'python':
      return 'Python';
    case 'javascript':
    case 'typescript':
    case 'node':
      return 'Node.js';
    default:
      return language == null || language.isEmpty ? '--' : _titleCase(language);
  }
}

String _titleCase(String value) {
  return value
      .replaceAll('_', ' ')
      .replaceAll('-', ' ')
      .split(' ')
      .where((part) => part.isNotEmpty)
      .map((part) => '${part[0].toUpperCase()}${part.substring(1)}')
      .join(' ');
}

ConsoleLog _log(String level, String message) {
  final now = DateTime.now();
  final time =
      '${now.hour.toString().padLeft(2, '0')}:'
      '${now.minute.toString().padLeft(2, '0')}:'
      '${now.second.toString().padLeft(2, '0')}';
  return ConsoleLog(time: time, level: level, message: message);
}

String _friendlyError(Object error) {
  final text = error.toString();
  if (text.contains('XMLHttpRequest') || text.contains('Failed host lookup')) {
    return 'Unable to reach the DeploySamurai API. Check that FastAPI is running on the configured API_BASE_URL.';
  }
  return text.replaceFirst('Exception: ', '');
}
