import 'package:flutter/material.dart';

import '../../core/download/artifact_downloader.dart';
import '../../core/theme/app_colors.dart';
import '../../domain/entities/dashboard_snapshot.dart';
import 'app_panel.dart';

class SamArtifactsPanel extends StatelessWidget {
  const SamArtifactsPanel({
    required this.snapshot,
    this.compact = false,
    super.key,
  });

  final DashboardSnapshot snapshot;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    return AppPanel(
      compact: compact,
      padding: EdgeInsets.all(compact ? 16 : 20),
      title: 'SAM Artifacts',
      leading: const Icon(
        Icons.folder_open_outlined,
        size: 19,
        color: AppColors.muted,
      ),
      child: Column(
        children: [
          for (final artifact in snapshot.artifacts)
            Padding(
              padding: const EdgeInsets.only(bottom: 14),
              child: Row(
                children: [
                  Icon(
                    artifact.isFolder
                        ? Icons.folder_outlined
                        : Icons.insert_drive_file_outlined,
                    size: 19,
                    color: AppColors.muted,
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      artifact.name,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        color: AppColors.text,
                        fontSize: 13,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ),
                  Text(
                    artifact.size,
                    style: const TextStyle(
                      color: AppColors.muted,
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
            ),
          const SizedBox(height: 4),
          SizedBox(
            width: double.infinity,
            height: 42,
            child: OutlinedButton.icon(
              onPressed: _templateDownloadUrl(snapshot) == null
                  ? null
                  : () => downloadArtifact(_templateDownloadUrl(snapshot)!),
              icon: const Icon(Icons.file_download_outlined, size: 18),
              label: const Text('Download template.yaml'),
              style: OutlinedButton.styleFrom(
                foregroundColor: AppColors.text,
                side: const BorderSide(color: AppColors.border),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
                textStyle: const TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w800,
                ),
              ),
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
