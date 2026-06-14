enum AnalysisMode { advisor, autonomous }

enum PipelineStepStatus { completed, inProgress, pending, locked }

enum ArchitectureResourceType { apiGateway, lambda, sqs, dynamoDb }

class DashboardSnapshot {
  const DashboardSnapshot({
    required this.repoUrl,
    required this.selectedMode,
    required this.region,
    required this.version,
    required this.connected,
    required this.elapsed,
    required this.pipelineSteps,
    required this.architectureResources,
    required this.architectureConnections,
    required this.stackFacts,
    required this.artifacts,
    required this.consoleLogs,
    required this.samPlanSummary,
  });

  final String repoUrl;
  final AnalysisMode selectedMode;
  final String region;
  final String version;
  final bool connected;
  final String elapsed;
  final List<PipelineStep> pipelineSteps;
  final List<ArchitectureResource> architectureResources;
  final List<ArchitectureConnection> architectureConnections;
  final List<StackFact> stackFacts;
  final List<SamArtifact> artifacts;
  final List<ConsoleLog> consoleLogs;
  final List<String> samPlanSummary;

  DashboardSnapshot copyWith({
    String? repoUrl,
    AnalysisMode? selectedMode,
    String? elapsed,
  }) {
    return DashboardSnapshot(
      repoUrl: repoUrl ?? this.repoUrl,
      selectedMode: selectedMode ?? this.selectedMode,
      region: region,
      version: version,
      connected: connected,
      elapsed: elapsed ?? this.elapsed,
      pipelineSteps: pipelineSteps,
      architectureResources: architectureResources,
      architectureConnections: architectureConnections,
      stackFacts: stackFacts,
      artifacts: artifacts,
      consoleLogs: consoleLogs,
      samPlanSummary: samPlanSummary,
    );
  }
}

class PipelineStep {
  const PipelineStep({
    required this.title,
    required this.caption,
    required this.status,
  });

  final String title;
  final String caption;
  final PipelineStepStatus status;
}

class ArchitectureResource {
  const ArchitectureResource({
    required this.id,
    required this.title,
    required this.caption,
    required this.type,
  });

  final String id;
  final String title;
  final String caption;
  final ArchitectureResourceType type;
}

class ArchitectureConnection {
  const ArchitectureConnection({required this.fromId, required this.toId});

  final String fromId;
  final String toId;
}

class StackFact {
  const StackFact({required this.label, required this.value});

  final String label;
  final String value;
}

class SamArtifact {
  const SamArtifact({
    required this.name,
    required this.size,
    required this.isFolder,
  });

  final String name;
  final String size;
  final bool isFolder;
}

class ConsoleLog {
  const ConsoleLog({
    required this.time,
    required this.level,
    required this.message,
  });

  final String time;
  final String level;
  final String message;
}
