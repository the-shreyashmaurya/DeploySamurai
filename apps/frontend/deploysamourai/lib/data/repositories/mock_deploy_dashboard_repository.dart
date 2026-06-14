import '../../domain/entities/dashboard_snapshot.dart';
import '../../domain/repositories/deploy_dashboard_repository.dart';

class MockDeployDashboardRepository implements DeployDashboardRepository {
  @override
  DashboardSnapshot loadSnapshot() {
    return const DashboardSnapshot(
      repoUrl: 'https://github.com/acme-inc/order-service',
      selectedMode: AnalysisMode.advisor,
      region: 'AWS - us-east-1',
      version: 'v2.4.1',
      connected: true,
      elapsed: '00:00:28',
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
          caption: 'In Progress',
          status: PipelineStepStatus.inProgress,
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
      architectureResources: [
        ArchitectureResource(
          id: 'api',
          title: 'API Gateway',
          caption: 'REST API',
          type: ArchitectureResourceType.apiGateway,
        ),
        ArchitectureResource(
          id: 'lambda',
          title: 'Lambda',
          caption: '1 function',
          type: ArchitectureResourceType.lambda,
        ),
        ArchitectureResource(
          id: 'queue',
          title: 'SQS',
          caption: 'Order Queue',
          type: ArchitectureResourceType.sqs,
        ),
        ArchitectureResource(
          id: 'db',
          title: 'DynamoDB',
          caption: 'Orders Table',
          type: ArchitectureResourceType.dynamoDb,
        ),
      ],
      architectureConnections: [
        ArchitectureConnection(fromId: 'api', toId: 'lambda'),
        ArchitectureConnection(fromId: 'api', toId: 'queue'),
        ArchitectureConnection(fromId: 'lambda', toId: 'db'),
        ArchitectureConnection(fromId: 'queue', toId: 'db'),
      ],
      stackFacts: [
        StackFact(label: 'Detected Stack', value: 'AWS Serverless'),
        StackFact(label: 'Runtime', value: 'Python 3.11'),
        StackFact(label: 'Region', value: 'us-east-1'),
        StackFact(label: 'Components', value: '4 resources'),
      ],
      artifacts: [
        SamArtifact(name: 'template.yaml', size: '18.4 KB', isFolder: false),
        SamArtifact(name: 'samconfig.toml', size: '2.1 KB', isFolder: false),
        SamArtifact(name: 'events/', size: '--', isFolder: true),
        SamArtifact(name: 'functions/', size: '--', isFolder: true),
        SamArtifact(name: 'requirements.txt', size: '0.7 KB', isFolder: false),
      ],
      consoleLogs: [
        ConsoleLog(
          time: '12:14:02',
          level: 'INFO',
          message: 'Starting analysis for acme-inc/order-service',
        ),
        ConsoleLog(
          time: '12:14:03',
          level: 'INFO',
          message: 'Cloning repository (branch: main)',
        ),
        ConsoleLog(
          time: '12:14:06',
          level: 'INFO',
          message: 'Repository cloned successfully',
        ),
        ConsoleLog(
          time: '12:14:08',
          level: 'INFO',
          message: 'Detecting project type and stack',
        ),
        ConsoleLog(
          time: '12:14:10',
          level: 'INFO',
          message: 'Detected: AWS Serverless Application (SAM)',
        ),
        ConsoleLog(
          time: '12:14:12',
          level: 'INFO',
          message: 'Runtime: Python3.11 | Architecture: x86_64',
        ),
        ConsoleLog(
          time: '12:14:14',
          level: 'INFO',
          message: 'Identifying boundaries and resources',
        ),
        ConsoleLog(
          time: '12:14:28',
          level: 'INFO',
          message: 'Mapping project structure and identifying components...',
        ),
      ],
      samPlanSummary: ['4 resources to create', 'No destructive changes'],
    );
  }
}
