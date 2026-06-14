import 'dart:convert';

import 'package:http/http.dart' as http;

import '../../domain/entities/dashboard_snapshot.dart';

class DeploySamuraiApiClient {
  DeploySamuraiApiClient({
    required http.Client httpClient,
    required String baseUrl,
  }) : _httpClient = httpClient,
       _baseUri = Uri.parse(
         baseUrl.endsWith('/')
             ? baseUrl.substring(0, baseUrl.length - 1)
             : baseUrl,
       );

  final http.Client _httpClient;
  final Uri _baseUri;

  Future<JobCreateDto> createJob({
    required String repoUrl,
    required AnalysisMode mode,
  }) async {
    final response = await _postJson('/jobs', {
      'repo_url': repoUrl,
      'mode': mode.apiValue,
      'target': 'aws-sam',
      'allow_deploy': mode == AnalysisMode.autonomous,
    });
    return JobCreateDto.fromJson(response);
  }

  Future<RepoAnalysisDto> analyzeRepo({
    required String repoUrl,
    required String jobId,
  }) async {
    final response = await _postJson('/analyze/repo', {
      'repo_url': repoUrl,
      'job_id': jobId,
    });
    return RepoAnalysisDto.fromJson(response);
  }

  Future<ArchitectureReasoningDto> reasonArchitecture({
    required String jobId,
    required RepoAnalysisDto analysis,
  }) async {
    final response = await _postJson('/reason/architecture', {
      'job_id': jobId,
      'repo_summary': analysis.repoSummary.toJson(),
      'structure': analysis.structure.toJson(),
    });
    return ArchitectureReasoningDto.fromJson(response);
  }

  Future<DeploymentPreflightDto> runDeploymentPreflight() async {
    final response = await _postJson('/deploy/preflight', {});
    return DeploymentPreflightDto.fromJson(response);
  }

  Future<VerificationResultDto> verifyDeployment({
    required String jobId,
    required String deploymentId,
    String? stackName,
    String? baseUrl,
    required List<String> expectedEndpoints,
  }) async {
    final response = await _postJson('/verify', {
      'job_id': jobId,
      'deployment_id': deploymentId,
      'stack_name': stackName,
      'base_url': baseUrl,
      'expected_endpoints': expectedEndpoints,
    });
    return VerificationResultDto.fromJson(response);
  }

  Future<Map<String, dynamic>> _postJson(
    String path,
    Map<String, dynamic> body,
  ) async {
    final response = await _httpClient.post(
      _baseUri.resolve('${_baseUri.path}$path'),
      headers: const {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
      body: jsonEncode(body),
    );

    final decoded = _decodeJson(response.body);
    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw DeploySamuraiApiException(
        statusCode: response.statusCode,
        message: _errorMessage(decoded),
      );
    }
    if (decoded is! Map<String, dynamic>) {
      throw const DeploySamuraiApiException(
        statusCode: 0,
        message: 'Backend returned an unexpected response.',
      );
    }
    return decoded;
  }

  Object? _decodeJson(String body) {
    if (body.isEmpty) {
      return null;
    }
    try {
      return jsonDecode(body);
    } on FormatException {
      return body;
    }
  }

  String _errorMessage(Object? decoded) {
    if (decoded is Map<String, dynamic>) {
      final detail = decoded['detail'];
      if (detail is String && detail.isNotEmpty) {
        return detail;
      }
      final error = decoded['error'];
      if (error is Map<String, dynamic>) {
        final message = error['message'];
        if (message is String && message.isNotEmpty) {
          return message;
        }
      }
    }
    return 'Backend request failed.';
  }
}

class DeploySamuraiApiException implements Exception {
  const DeploySamuraiApiException({
    required this.statusCode,
    required this.message,
  });

  final int statusCode;
  final String message;

  @override
  String toString() {
    if (statusCode == 0) {
      return message;
    }
    return 'HTTP $statusCode: $message';
  }
}

class JobCreateDto {
  const JobCreateDto({
    required this.jobId,
    required this.status,
    required this.mode,
  });

  factory JobCreateDto.fromJson(Map<String, dynamic> json) {
    return JobCreateDto(
      jobId: json['job_id'] as String,
      status: json['status'] as String,
      mode: json['mode'] as String,
    );
  }

  final String jobId;
  final String status;
  final String mode;
}

class RepoAnalysisDto {
  const RepoAnalysisDto({required this.repoSummary, required this.structure});

  factory RepoAnalysisDto.fromJson(Map<String, dynamic> json) {
    return RepoAnalysisDto(
      repoSummary: RepoSummaryDto.fromJson(
        json['repo_summary'] as Map<String, dynamic>,
      ),
      structure: RepoStructureDto.fromJson(
        json['structure'] as Map<String, dynamic>,
      ),
    );
  }

  final RepoSummaryDto repoSummary;
  final RepoStructureDto structure;
}

class RepoSummaryDto {
  const RepoSummaryDto({
    required this.name,
    this.defaultBranch,
    this.language,
    this.framework,
    this.packageManager,
    required this.hasTests,
  });

  factory RepoSummaryDto.fromJson(Map<String, dynamic> json) {
    return RepoSummaryDto(
      name: json['name'] as String,
      defaultBranch: json['default_branch'] as String?,
      language: json['language'] as String?,
      framework: json['framework'] as String?,
      packageManager: json['package_manager'] as String?,
      hasTests: json['has_tests'] as bool? ?? false,
    );
  }

  final String name;
  final String? defaultBranch;
  final String? language;
  final String? framework;
  final String? packageManager;
  final bool hasTests;

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'default_branch': defaultBranch,
      'language': language,
      'framework': framework,
      'package_manager': packageManager,
      'has_tests': hasTests,
    };
  }
}

class RepoStructureDto {
  const RepoStructureDto({
    required this.rootFiles,
    required this.folderTree,
    required this.entrypoints,
  });

  factory RepoStructureDto.fromJson(Map<String, dynamic> json) {
    return RepoStructureDto(
      rootFiles: _stringList(json['root_files']),
      folderTree: _stringList(json['folder_tree']),
      entrypoints: _stringList(json['entrypoints']),
    );
  }

  final List<String> rootFiles;
  final List<String> folderTree;
  final List<String> entrypoints;

  Map<String, dynamic> toJson() {
    return {
      'root_files': rootFiles,
      'folder_tree': folderTree,
      'entrypoints': entrypoints,
    };
  }
}

class ArchitectureReasoningDto {
  const ArchitectureReasoningDto({
    required this.architectureType,
    required this.summary,
    required this.serviceCandidates,
    required this.communicationFlows,
    required this.notes,
  });

  factory ArchitectureReasoningDto.fromJson(Map<String, dynamic> json) {
    return ArchitectureReasoningDto(
      architectureType: json['architecture_type'] as String,
      summary: json['summary'] as String? ?? '',
      serviceCandidates: (json['service_candidates'] as List<dynamic>? ?? [])
          .whereType<Map<String, dynamic>>()
          .map(ServiceCandidateDto.fromJson)
          .toList(),
      communicationFlows: (json['communication_flows'] as List<dynamic>? ?? [])
          .whereType<Map<String, dynamic>>()
          .map(CommunicationFlowDto.fromJson)
          .toList(),
      notes: _stringList(json['notes']),
    );
  }

  final String architectureType;
  final String summary;
  final List<ServiceCandidateDto> serviceCandidates;
  final List<CommunicationFlowDto> communicationFlows;
  final List<String> notes;
}

class ServiceCandidateDto {
  const ServiceCandidateDto({
    required this.name,
    required this.responsibility,
    required this.runtime,
    this.dataStore,
  });

  factory ServiceCandidateDto.fromJson(Map<String, dynamic> json) {
    return ServiceCandidateDto(
      name: json['name'] as String,
      responsibility: json['responsibility'] as String,
      runtime: json['runtime'] as String? ?? 'lambda',
      dataStore: json['data_store'] as String?,
    );
  }

  final String name;
  final String responsibility;
  final String runtime;
  final String? dataStore;
}

class CommunicationFlowDto {
  const CommunicationFlowDto({
    required this.source,
    required this.target,
    required this.style,
    required this.transport,
  });

  factory CommunicationFlowDto.fromJson(Map<String, dynamic> json) {
    return CommunicationFlowDto(
      source: json['from'] as String,
      target: json['to'] as String,
      style: json['style'] as String,
      transport: json['transport'] as String,
    );
  }

  final String source;
  final String target;
  final String style;
  final String transport;
}

class DeploymentPreflightDto {
  const DeploymentPreflightDto({
    required this.status,
    required this.region,
    this.accountId,
    this.arn,
    required this.message,
  });

  factory DeploymentPreflightDto.fromJson(Map<String, dynamic> json) {
    return DeploymentPreflightDto(
      status: json['status'] as String,
      region: json['region'] as String,
      accountId: json['account_id'] as String?,
      arn: json['arn'] as String?,
      message: json['message'] as String? ?? '',
    );
  }

  final String status;
  final String region;
  final String? accountId;
  final String? arn;
  final String message;

  bool get passed => status == 'passed';
}

class VerificationResultDto {
  const VerificationResultDto({required this.status, required this.checks});

  factory VerificationResultDto.fromJson(Map<String, dynamic> json) {
    return VerificationResultDto(
      status: json['status'] as String,
      checks: (json['checks'] as List<dynamic>? ?? [])
          .whereType<Map<String, dynamic>>()
          .map(VerificationCheckDto.fromJson)
          .toList(growable: false),
    );
  }

  final String status;
  final List<VerificationCheckDto> checks;

  bool get passed => status == 'passed';
}

class VerificationCheckDto {
  const VerificationCheckDto({
    required this.name,
    required this.status,
    this.evidence,
  });

  factory VerificationCheckDto.fromJson(Map<String, dynamic> json) {
    return VerificationCheckDto(
      name: json['name'] as String,
      status: json['status'] as String,
      evidence: json['evidence'] as String?,
    );
  }

  final String name;
  final String status;
  final String? evidence;
}

List<String> _stringList(Object? value) {
  return (value as List<dynamic>? ?? []).whereType<String>().toList(
    growable: false,
  );
}

extension AnalysisModeApiValue on AnalysisMode {
  String get apiValue {
    switch (this) {
      case AnalysisMode.advisor:
        return 'advisor';
      case AnalysisMode.autonomous:
        return 'autonomous';
    }
  }
}
