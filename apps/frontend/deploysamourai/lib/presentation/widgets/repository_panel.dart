import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/theme/app_colors.dart';
import '../../domain/entities/dashboard_snapshot.dart';
import '../providers/deploy_dashboard_provider.dart';
import 'app_panel.dart';

class RepositoryPanel extends StatelessWidget {
  const RepositoryPanel({
    required this.snapshot,
    this.compact = false,
    super.key,
  });

  final DashboardSnapshot snapshot;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<DeployDashboardProvider>();

    return AppPanel(
      compact: compact,
      padding: EdgeInsets.all(compact ? 16 : 24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Repository',
            style: TextStyle(
              color: AppColors.text,
              fontSize: compact ? 16 : 20,
              fontWeight: FontWeight.w800,
            ),
          ),
          if (!compact) ...[
            const SizedBox(height: 6),
            const Text(
              'Start an analysis of your serverless application.',
              style: TextStyle(
                color: AppColors.muted,
                fontSize: 13,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
          SizedBox(height: compact ? 14 : 22),
          if (compact)
            Column(
              children: [
                RepositoryInput(
                  repoUrl: snapshot.repoUrl,
                  onChanged: provider.setRepoUrl,
                ),
                const SizedBox(height: 12),
                AnalyzeButton(
                  onPressed: provider.isAnalyzing
                      ? null
                      : provider.analyzeRepository,
                  compact: true,
                ),
              ],
            )
          else
            Row(
              children: [
                Expanded(
                  child: RepositoryInput(
                    repoUrl: snapshot.repoUrl,
                    onChanged: provider.setRepoUrl,
                  ),
                ),
                const SizedBox(width: 28),
                SizedBox(
                  width: 194,
                  child: AnalyzeButton(
                    onPressed: provider.isAnalyzing
                        ? null
                        : provider.analyzeRepository,
                  ),
                ),
              ],
            ),
          SizedBox(height: compact ? 12 : 16),
          _StatusMessage(snapshot: snapshot),
          SizedBox(height: compact ? 18 : 26),
          const Text(
            'Analysis mode',
            style: TextStyle(
              color: AppColors.text,
              fontSize: 13,
              fontWeight: FontWeight.w800,
            ),
          ),
          const SizedBox(height: 10),
          _ModeSelector(snapshot: snapshot, compact: compact),
          SizedBox(height: compact ? 12 : 22),
          Row(
            children: [
              const Icon(
                Icons.shield_outlined,
                size: 18,
                color: AppColors.muted,
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  'Autonomous mode is locked until requirements are met and plan approved.',
                  maxLines: compact ? 2 : 1,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    color: AppColors.muted,
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class RepositoryInput extends StatefulWidget {
  const RepositoryInput({
    required this.repoUrl,
    required this.onChanged,
    super.key,
  });

  final String repoUrl;
  final ValueChanged<String> onChanged;

  @override
  State<RepositoryInput> createState() => _RepositoryInputState();
}

class _RepositoryInputState extends State<RepositoryInput> {
  late final TextEditingController _controller;

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController(text: widget.repoUrl);
  }

  @override
  void didUpdateWidget(covariant RepositoryInput oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.repoUrl != widget.repoUrl &&
        _controller.text != widget.repoUrl) {
      _controller.text = widget.repoUrl;
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 54,
      child: TextField(
        controller: _controller,
        onChanged: widget.onChanged,
        textInputAction: TextInputAction.done,
        style: const TextStyle(
          color: AppColors.text,
          fontSize: 14,
          fontWeight: FontWeight.w600,
        ),
        decoration: InputDecoration(
          filled: true,
          fillColor: AppColors.surface,
          prefixIcon: Padding(
            padding: const EdgeInsets.all(13),
            child: Container(
              decoration: const BoxDecoration(
                color: AppColors.navy,
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.code_rounded,
                size: 16,
                color: Colors.white,
              ),
            ),
          ),
          suffixIcon: IconButton(
            icon: const Icon(Icons.close_rounded, size: 19),
            color: AppColors.muted,
            tooltip: 'Clear repository URL',
            onPressed: () {
              _controller.clear();
              widget.onChanged('');
            },
          ),
          contentPadding: const EdgeInsets.symmetric(horizontal: 16),
          border: _inputBorder(AppColors.border),
          enabledBorder: _inputBorder(AppColors.border),
          focusedBorder: _inputBorder(AppColors.teal),
        ),
      ),
    );
  }

  OutlineInputBorder _inputBorder(Color color) {
    return OutlineInputBorder(
      borderRadius: BorderRadius.circular(8),
      borderSide: BorderSide(color: color),
    );
  }
}

class AnalyzeButton extends StatelessWidget {
  const AnalyzeButton({
    required this.onPressed,
    this.compact = false,
    super.key,
  });

  final VoidCallback? onPressed;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: compact ? 44 : 58,
      width: double.infinity,
      child: DecoratedBox(
        decoration: BoxDecoration(
          gradient: const LinearGradient(
            colors: [AppColors.teal, AppColors.tealDark],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.circular(8),
          boxShadow: [
            BoxShadow(
              color: AppColors.teal.withValues(alpha: 0.26),
              blurRadius: 18,
              offset: const Offset(0, 8),
            ),
          ],
        ),
        child: FilledButton.icon(
          onPressed: onPressed,
          icon: onPressed == null
              ? const SizedBox(
                  width: 17,
                  height: 17,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    color: Colors.white,
                  ),
                )
              : const Icon(Icons.auto_awesome_rounded, size: 19),
          label: Text(onPressed == null ? 'Analyzing' : 'Analyze Repo'),
          style: FilledButton.styleFrom(
            foregroundColor: Colors.white,
            backgroundColor: Colors.transparent,
            shadowColor: Colors.transparent,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
            textStyle: TextStyle(
              fontSize: compact ? 13 : 15,
              fontWeight: FontWeight.w800,
            ),
          ),
        ),
      ),
    );
  }
}

class _StatusMessage extends StatelessWidget {
  const _StatusMessage({required this.snapshot});

  final DashboardSnapshot snapshot;

  @override
  Widget build(BuildContext context) {
    final color = switch (snapshot.runStatus) {
      DashboardRunStatus.succeeded => AppColors.success,
      DashboardRunStatus.failed => Colors.redAccent,
      DashboardRunStatus.running => AppColors.teal,
      DashboardRunStatus.idle => AppColors.muted,
    };

    return Row(
      children: [
        Icon(Icons.circle, size: 8, color: color),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            snapshot.statusMessage,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
            style: TextStyle(
              color: color,
              fontSize: 12,
              fontWeight: FontWeight.w700,
            ),
          ),
        ),
      ],
    );
  }
}

class _ModeSelector extends StatelessWidget {
  const _ModeSelector({required this.snapshot, required this.compact});

  final DashboardSnapshot snapshot;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    final provider = context.read<DeployDashboardProvider>();

    return Container(
      decoration: BoxDecoration(
        color: AppColors.surfaceMuted,
        border: Border.all(color: AppColors.border),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Expanded(
            child: _ModeTile(
              title: 'Advisor',
              subtitle: 'AI guidance and recommendations',
              icon: Icons.support_agent_rounded,
              selected: snapshot.selectedMode == AnalysisMode.advisor,
              compact: compact,
              onTap: () => provider.selectMode(AnalysisMode.advisor),
            ),
          ),
          Expanded(
            child: _ModeTile(
              title: 'Autonomous',
              subtitle: 'AI plans and deploys with guardrails',
              icon: Icons.lock_open_outlined,
              selected: snapshot.selectedMode == AnalysisMode.autonomous,
              locked: true,
              compact: compact,
              onTap: () => provider.selectMode(AnalysisMode.autonomous),
            ),
          ),
        ],
      ),
    );
  }
}

class _ModeTile extends StatelessWidget {
  const _ModeTile({
    required this.title,
    required this.subtitle,
    required this.icon,
    required this.selected,
    required this.onTap,
    required this.compact,
    this.locked = false,
  });

  final String title;
  final String subtitle;
  final IconData icon;
  final bool selected;
  final bool locked;
  final bool compact;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: selected ? AppColors.surface : Colors.transparent,
      borderRadius: BorderRadius.circular(8),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(8),
        child: Container(
          height: compact ? 54 : 70,
          padding: EdgeInsets.symmetric(
            horizontal: compact ? 10 : 20,
            vertical: 10,
          ),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(8),
            boxShadow: selected
                ? [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: 0.06),
                      blurRadius: 14,
                      offset: const Offset(0, 7),
                    ),
                  ]
                : null,
          ),
          child: Row(
            children: [
              Icon(
                icon,
                size: compact ? 18 : 22,
                color: selected ? AppColors.tealDark : AppColors.muted,
              ),
              SizedBox(width: compact ? 8 : 14),
              Expanded(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: TextStyle(
                        color: selected ? AppColors.tealDark : AppColors.text,
                        fontSize: compact ? 12 : 14,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    if (!compact) ...[
                      const SizedBox(height: 3),
                      Text(
                        subtitle,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                          color: AppColors.muted,
                          fontSize: 11,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
              if (locked)
                Icon(
                  Icons.lock_outline_rounded,
                  size: compact ? 14 : 18,
                  color: AppColors.muted,
                ),
            ],
          ),
        ),
      ),
    );
  }
}
