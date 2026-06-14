import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/download/artifact_downloader.dart';
import '../../core/theme/app_colors.dart';
import '../../domain/entities/dashboard_snapshot.dart';
import '../providers/deploy_dashboard_provider.dart';
import 'app_panel.dart';

class ApprovalGatePanel extends StatelessWidget {
  const ApprovalGatePanel({
    required this.snapshot,
    this.compact = false,
    super.key,
  });

  final DashboardSnapshot snapshot;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<DeployDashboardProvider>();
    final canDeploy =
        snapshot.samTemplateArtifactPath != null && !provider.isDeploying;

    return AppPanel(
      compact: compact,
      padding: EdgeInsets.all(compact ? 16 : 20),
      title: 'Approval Gate',
      leading: const Icon(
        Icons.lock_outline_rounded,
        size: 19,
        color: AppColors.muted,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: AppColors.warningSoft,
              border: Border.all(color: const Color(0xffffdf9c)),
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Row(
              children: [
                Icon(
                  Icons.warning_amber_rounded,
                  color: AppColors.warning,
                  size: 22,
                ),
                SizedBox(width: 10),
                Expanded(
                  child: Text(
                    'Autonomous deployment requires approval. Review the SAM plan to continue.',
                    style: TextStyle(
                      color: AppColors.text,
                      fontSize: 12,
                      height: 1.35,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 18),
          const Text(
            'SAM Plan Summary',
            style: TextStyle(
              color: AppColors.text,
              fontSize: 12,
              fontWeight: FontWeight.w900,
            ),
          ),
          const SizedBox(height: 10),
          for (final item in snapshot.samPlanSummary)
            Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Row(
                children: [
                  const Icon(
                    Icons.check_circle_outline_rounded,
                    size: 16,
                    color: AppColors.success,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      item,
                      style: const TextStyle(
                        color: AppColors.text,
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          const SizedBox(height: 8),
          SizedBox(
            width: double.infinity,
            height: compact ? 40 : 44,
            child: OutlinedButton.icon(
              onPressed: _templateDownloadUrl(snapshot) == null
                  ? null
                  : () => downloadArtifact(_templateDownloadUrl(snapshot)!),
              icon: const Icon(Icons.open_in_new_rounded, size: 15),
              label: const Text('Review SAM Plan'),
              style: OutlinedButton.styleFrom(
                foregroundColor: AppColors.text,
                side: const BorderSide(color: AppColors.border),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
                textStyle: const TextStyle(fontWeight: FontWeight.w800),
              ),
            ),
          ),
          const SizedBox(height: 12),
          SizedBox(
            width: double.infinity,
            height: compact ? 40 : 50,
            child: FilledButton.icon(
              onPressed: canDeploy ? provider.approveAndDeploy : null,
              icon: provider.isDeploying
                  ? const SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Colors.white,
                      ),
                    )
                  : Icon(
                      canDeploy
                          ? Icons.rocket_launch_outlined
                          : Icons.lock_outline_rounded,
                      size: 16,
                    ),
              label: Text(
                provider.isDeploying ? 'Deploying' : 'Approve & Deploy',
              ),
              style: FilledButton.styleFrom(
                disabledBackgroundColor: const Color(0xffe2e8ee),
                disabledForegroundColor: AppColors.muted,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
                textStyle: const TextStyle(fontWeight: FontWeight.w800),
              ),
            ),
          ),
          const SizedBox(height: 10),
          Text(
            snapshot.samTemplateArtifactPath == null
                ? '* Generate a SAM plan to enable deployment.'
                : '* This runs SAM CLI using your configured AWS credentials.',
            style: TextStyle(
              color: AppColors.muted,
              fontSize: 11,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  String? _templateDownloadUrl(DashboardSnapshot snapshot) {
    for (final artifact in snapshot.artifacts) {
      if (artifact.name == 'template.yaml' && artifact.downloadUrl != null) {
        return artifact.downloadUrl;
      }
    }
    return null;
  }
}
