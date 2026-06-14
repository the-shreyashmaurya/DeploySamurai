import 'package:flutter/material.dart';

import '../../core/theme/app_colors.dart';
import '../../domain/entities/dashboard_snapshot.dart';
import 'app_panel.dart';

class DeploymentConsolePanel extends StatelessWidget {
  const DeploymentConsolePanel({
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
      title: 'Deployment Console',
      leading: const Icon(
        Icons.terminal_rounded,
        size: 18,
        color: AppColors.muted,
      ),
      trailing: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          _ConsoleActionButton(label: 'Clear', onPressed: () {}),
          const SizedBox(width: 8),
          _ConsoleIconButton(
            icon: Icons.pause_rounded,
            tooltip: 'Pause log stream',
            onPressed: () {},
          ),
        ],
      ),
      child: Container(
        height: compact ? 190 : 208,
        width: double.infinity,
        decoration: BoxDecoration(
          color: AppColors.navy,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: AppColors.navySoft),
        ),
        child: Scrollbar(
          thumbVisibility: !compact,
          child: ListView.separated(
            padding: const EdgeInsets.fromLTRB(16, 14, 16, 14),
            itemBuilder: (context, index) {
              return _ConsoleLine(log: snapshot.consoleLogs[index]);
            },
            separatorBuilder: (context, index) => const SizedBox(height: 8),
            itemCount: snapshot.consoleLogs.length,
          ),
        ),
      ),
    );
  }
}

class _ConsoleLine extends StatelessWidget {
  const _ConsoleLine({required this.log});

  final ConsoleLog log;

  @override
  Widget build(BuildContext context) {
    return RichText(
      maxLines: 1,
      overflow: TextOverflow.ellipsis,
      text: TextSpan(
        style: const TextStyle(
          fontFamily: 'monospace',
          fontSize: 12,
          height: 1.25,
        ),
        children: [
          TextSpan(
            text: '${log.time}  ',
            style: const TextStyle(color: Color(0xffb5c5d2)),
          ),
          TextSpan(
            text: '${log.level}  ',
            style: const TextStyle(
              color: Color(0xff4bd07f),
              fontWeight: FontWeight.w700,
            ),
          ),
          TextSpan(
            text: log.message,
            style: const TextStyle(color: Color(0xffe8f1f6)),
          ),
        ],
      ),
    );
  }
}

class _ConsoleActionButton extends StatelessWidget {
  const _ConsoleActionButton({required this.label, required this.onPressed});

  final String label;
  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 34,
      child: OutlinedButton(
        onPressed: onPressed,
        style: OutlinedButton.styleFrom(
          foregroundColor: AppColors.text,
          side: const BorderSide(color: AppColors.border),
          padding: const EdgeInsets.symmetric(horizontal: 14),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
          textStyle: const TextStyle(fontSize: 12, fontWeight: FontWeight.w800),
        ),
        child: Text(label),
      ),
    );
  }
}

class _ConsoleIconButton extends StatelessWidget {
  const _ConsoleIconButton({
    required this.icon,
    required this.tooltip,
    required this.onPressed,
  });

  final IconData icon;
  final String tooltip;
  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) {
    return IconButton(
      tooltip: tooltip,
      onPressed: onPressed,
      icon: Icon(icon, size: 17),
      color: AppColors.text,
      style: IconButton.styleFrom(
        fixedSize: const Size(34, 34),
        backgroundColor: AppColors.surface,
        side: const BorderSide(color: AppColors.border),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
      ),
    );
  }
}
