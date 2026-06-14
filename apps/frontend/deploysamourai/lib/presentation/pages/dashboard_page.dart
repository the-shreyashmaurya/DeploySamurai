import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/theme/app_colors.dart';
import '../../domain/entities/dashboard_snapshot.dart';
import '../providers/deploy_dashboard_provider.dart';
import '../widgets/approval_gate_panel.dart';
import '../widgets/architecture_preview_panel.dart';
import '../widgets/deployment_console_panel.dart';
import '../widgets/mobile_bottom_nav.dart';
import '../widgets/pipeline_panel.dart';
import '../widgets/repository_panel.dart';
import '../widgets/sam_artifacts_panel.dart';
import '../widgets/side_navigation.dart';
import '../widgets/top_header.dart';

class DashboardPage extends StatelessWidget {
  const DashboardPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<DeployDashboardProvider>(
      builder: (context, provider, child) {
        if (provider.isLoading) {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }

        return LayoutBuilder(
          builder: (context, constraints) {
            final snapshot = provider.snapshot;
            if (constraints.maxWidth < 980) {
              return _MobileDashboard(snapshot: snapshot);
            }
            return _DesktopDashboard(snapshot: snapshot);
          },
        );
      },
    );
  }
}

class _DesktopDashboard extends StatelessWidget {
  const _DesktopDashboard({required this.snapshot});

  final DashboardSnapshot snapshot;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 1420),
          child: Padding(
            padding: const EdgeInsets.all(14),
            child: DecoratedBox(
              decoration: BoxDecoration(
                color: AppColors.surface,
                border: Border.all(color: AppColors.border),
                borderRadius: BorderRadius.circular(8),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.12),
                    blurRadius: 28,
                    offset: const Offset(0, 16),
                  ),
                ],
              ),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(8),
                child: Column(
                  children: [
                    TopHeader(snapshot: snapshot),
                    Expanded(
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          const SideNavigation(),
                          Expanded(
                            child: ColoredBox(
                              color: AppColors.shell,
                              child: SingleChildScrollView(
                                padding: const EdgeInsets.all(20),
                                child: Row(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Expanded(
                                      child: Column(
                                        children: [
                                          RepositoryPanel(snapshot: snapshot),
                                          const SizedBox(height: 16),
                                          PipelinePanel(snapshot: snapshot),
                                          const SizedBox(height: 16),
                                          SizedBox(
                                            height: 318,
                                            child: Row(
                                              crossAxisAlignment:
                                                  CrossAxisAlignment.stretch,
                                              children: [
                                                SizedBox(
                                                  width: 260,
                                                  child: SamArtifactsPanel(
                                                    snapshot: snapshot,
                                                  ),
                                                ),
                                                const SizedBox(width: 16),
                                                Expanded(
                                                  child: DeploymentConsolePanel(
                                                    snapshot: snapshot,
                                                  ),
                                                ),
                                              ],
                                            ),
                                          ),
                                        ],
                                      ),
                                    ),
                                    const SizedBox(width: 20),
                                    SizedBox(
                                      width: 342,
                                      child: Column(
                                        children: [
                                          ArchitecturePreviewPanel(
                                            snapshot: snapshot,
                                          ),
                                          const SizedBox(height: 16),
                                          ApprovalGatePanel(snapshot: snapshot),
                                        ],
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _MobileDashboard extends StatelessWidget {
  const _MobileDashboard({required this.snapshot});

  final DashboardSnapshot snapshot;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: Column(
          children: [
            TopHeader(snapshot: snapshot, compact: true),
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.fromLTRB(16, 10, 16, 20),
                child: Column(
                  children: [
                    RepositoryPanel(snapshot: snapshot, compact: true),
                    const SizedBox(height: 14),
                    PipelinePanel(snapshot: snapshot, compact: true),
                    const SizedBox(height: 14),
                    ArchitecturePreviewPanel(snapshot: snapshot, compact: true),
                    const SizedBox(height: 14),
                    ApprovalGatePanel(snapshot: snapshot, compact: true),
                    const SizedBox(height: 14),
                    SamArtifactsPanel(snapshot: snapshot, compact: true),
                    const SizedBox(height: 14),
                    DeploymentConsolePanel(snapshot: snapshot, compact: true),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
      bottomNavigationBar: const MobileBottomNav(),
    );
  }
}
