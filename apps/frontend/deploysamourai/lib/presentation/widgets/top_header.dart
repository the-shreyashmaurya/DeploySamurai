import 'package:flutter/material.dart';

import '../../core/theme/app_colors.dart';
import '../../domain/entities/dashboard_snapshot.dart';

class TopHeader extends StatelessWidget {
  const TopHeader({required this.snapshot, this.compact = false, super.key});

  final DashboardSnapshot snapshot;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    if (compact) {
      return Container(
        height: 64,
        padding: const EdgeInsets.symmetric(horizontal: 18),
        decoration: const BoxDecoration(
          color: AppColors.surface,
          border: Border(bottom: BorderSide(color: AppColors.border)),
        ),
        child: Row(
          children: [
            _IconButtonShell(icon: Icons.menu_rounded, onPressed: () {}),
            const Spacer(),
            const _Brand(compact: true),
            const Spacer(),
            _Avatar(compact: true),
          ],
        ),
      );
    }

    return Container(
      height: 82,
      padding: const EdgeInsets.symmetric(horizontal: 26),
      decoration: const BoxDecoration(
        color: AppColors.surface,
        border: Border(bottom: BorderSide(color: AppColors.border)),
      ),
      child: Row(
        children: [
          const _Brand(),
          const Spacer(),
          _StatusPill(icon: Icons.cloud_queue_outlined, label: snapshot.region),
          const SizedBox(width: 12),
          _StatusPill(
            label: snapshot.version,
            indicatorColor: AppColors.success,
          ),
          const SizedBox(width: 12),
          _StatusPill(
            label: snapshot.connected ? 'Connected' : 'Offline',
            indicatorColor: snapshot.connected
                ? AppColors.success
                : AppColors.warning,
          ),
          const SizedBox(width: 16),
          const _Avatar(),
        ],
      ),
    );
  }
}

class _Brand extends StatelessWidget {
  const _Brand({this.compact = false});

  final bool compact;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: compact ? 24 : 28,
          height: compact ? 24 : 28,
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [AppColors.teal, AppColors.tealDark],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(6),
            boxShadow: [
              BoxShadow(
                color: AppColors.teal.withValues(alpha: 0.22),
                blurRadius: 10,
                offset: const Offset(0, 4),
              ),
            ],
          ),
        ),
        SizedBox(width: compact ? 10 : 14),
        Text(
          'DeploySamurai',
          style: TextStyle(
            color: AppColors.tealDark,
            fontSize: compact ? 16 : 22,
            fontWeight: FontWeight.w800,
          ),
        ),
      ],
    );
  }
}

class _StatusPill extends StatelessWidget {
  const _StatusPill({required this.label, this.icon, this.indicatorColor});

  final String label;
  final IconData? icon;
  final Color? indicatorColor;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 38,
      padding: const EdgeInsets.symmetric(horizontal: 14),
      decoration: BoxDecoration(
        color: AppColors.surface,
        border: Border.all(color: AppColors.border),
        borderRadius: BorderRadius.circular(22),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (icon != null) ...[
            Icon(icon, size: 16, color: AppColors.muted),
            const SizedBox(width: 6),
          ],
          Text(
            label,
            style: const TextStyle(
              color: AppColors.text,
              fontSize: 13,
              fontWeight: FontWeight.w700,
            ),
          ),
          if (indicatorColor != null) ...[
            const SizedBox(width: 8),
            Container(
              width: 7,
              height: 7,
              decoration: BoxDecoration(
                color: indicatorColor,
                shape: BoxShape.circle,
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class _Avatar extends StatelessWidget {
  const _Avatar({this.compact = false});

  final bool compact;

  @override
  Widget build(BuildContext context) {
    return CircleAvatar(
      radius: compact ? 16 : 21,
      backgroundColor: AppColors.navySoft,
      child: Text(
        'AS',
        style: TextStyle(
          color: Colors.white,
          fontSize: compact ? 11 : 14,
          fontWeight: FontWeight.w800,
        ),
      ),
    );
  }
}

class _IconButtonShell extends StatelessWidget {
  const _IconButtonShell({required this.icon, required this.onPressed});

  final IconData icon;
  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) {
    return IconButton(
      onPressed: onPressed,
      icon: Icon(icon),
      color: AppColors.text,
      style: IconButton.styleFrom(
        backgroundColor: AppColors.surface,
        side: const BorderSide(color: AppColors.border),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
      ),
      tooltip: 'Open navigation',
    );
  }
}
