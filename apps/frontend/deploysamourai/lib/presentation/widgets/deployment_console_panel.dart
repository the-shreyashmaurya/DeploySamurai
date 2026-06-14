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
