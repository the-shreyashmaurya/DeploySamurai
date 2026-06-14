enum AnalysisMode { advisor, autonomous }

enum PipelineStepStatus { completed, inProgress, pending, locked }

enum ArchitectureResourceType { apiGateway, lambda, sqs, dynamoDb }

enum DashboardRunStatus { idle, running, succeeded, failed }

const Object _unset = Object();

class DashboardSnapshot {
  const DashboardSnapshot({
    this.jobId,
    required this.repoUrl,
    required this.selectedMode,
    required this.region,
    required this.version,
    required this.connected,
    required this.runStatus,
    required this.elapsed,
    required this.statusMessage,
    required this.pipelineSteps,
    required this.architectureResources,
    required this.architectureConnections,
    required this.stackFacts,
    required this.artifacts,
    required this.consoleLogs,
    required this.samPlanSummary,
    required this.architectureSummary,
    required this.notes,
  });

  final String? jobId;
  final String repoUrl;
  final AnalysisMode selectedMode;
  final String region;
  final String version;
  final bool connected;
  final DashboardRunStatus runStatus;
  final String elapsed;
  final String statusMessage;
  final List<PipelineStep> pipelineSteps;
  final List<ArchitectureResource> architectureResources;
  final List<ArchitectureConnection> architectureConnections;
  final List<StackFact> stackFacts;
  final List<SamArtifact> artifacts;
  final List<ConsoleLog> consoleLogs;
  final List<String> samPlanSummary;
  final String architectureSummary;
  final List<String> notes;

  String? get samTemplateArtifactPath {
    for (final artifact in artifacts) {
      if (artifact.name == 'template.yaml' && artifact.artifactPath != null) {
        return artifact.artifactPath;
      }
    }
    return null;
  }

  String? get samTemplateDownloadUrl {
    for (final artifact in artifacts) {
      if (artifact.name == 'template.yaml' && artifact.downloadUrl != null) {
        return artifact.downloadUrl;
      }
    }
    return null;
  }

  DashboardSnapshot copyWith({
    Object? jobId = _unset,
    String? repoUrl,
    AnalysisMode? selectedMode,
    bool? connected,
    DashboardRunStatus? runStatus,
    String? elapsed,
    String? statusMessage,
    List<PipelineStep>? pipelineSteps,
    List<ArchitectureResource>? architectureResources,
    List<ArchitectureConnection>? architectureConnections,
    List<StackFact>? stackFacts,
    List<SamArtifact>? artifacts,
    List<ConsoleLog>? consoleLogs,
    List<String>? samPlanSummary,
    String? architectureSummary,
    List<String>? notes,
  }) {
    return DashboardSnapshot(
      jobId: identical(jobId, _unset) ? this.jobId : jobId as String?,
      repoUrl: repoUrl ?? this.repoUrl,
      selectedMode: selectedMode ?? this.selectedMode,
      region: region,
      version: version,
      connected: connected ?? this.connected,
      runStatus: runStatus ?? this.runStatus,
      elapsed: elapsed ?? this.elapsed,
      statusMessage: statusMessage ?? this.statusMessage,
      pipelineSteps: pipelineSteps ?? this.pipelineSteps,
      architectureResources:
          architectureResources ?? this.architectureResources,
      architectureConnections:
          architectureConnections ?? this.architectureConnections,
      stackFacts: stackFacts ?? this.stackFacts,
      artifacts: artifacts ?? this.artifacts,
      consoleLogs: consoleLogs ?? this.consoleLogs,
      samPlanSummary: samPlanSummary ?? this.samPlanSummary,
      architectureSummary: architectureSummary ?? this.architectureSummary,
      notes: notes ?? this.notes,
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
    this.artifactPath,
    this.downloadUrl,
  });

  final String name;
  final String size;
  final bool isFolder;
  final String? artifactPath;
  final String? downloadUrl;
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
