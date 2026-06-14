import 'package:flutter/material.dart';

import '../../core/theme/app_colors.dart';

class SideNavigation extends StatelessWidget {
  const SideNavigation({super.key});

  @override
  Widget build(BuildContext context) {
    const items = [
      _NavItem(Icons.home_outlined, 'Overview', true),
      _NavItem(Icons.account_tree_outlined, 'Repositories', false),
      _NavItem(Icons.description_outlined, 'Plans', false),
      _NavItem(Icons.near_me_outlined, 'Deployments', false),
      _NavItem(Icons.cloud_queue_outlined, 'Environments', false),
      _NavItem(Icons.settings_outlined, 'Settings', false),
    ];

    return Container(
      width: 184,
      decoration: const BoxDecoration(
        color: AppColors.shell,
        border: Border(right: BorderSide(color: AppColors.border)),
      ),
      child: Column(
        children: [
          const SizedBox(height: 22),
          for (final item in items)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 4),
              child: _NavButton(item: item),
            ),
          const Spacer(),
          Padding(
            padding: const EdgeInsets.fromLTRB(18, 0, 18, 22),
            child: Row(
              children: [
                _SquareButton(
                  icon: Icons.wb_sunny_outlined,
                  tooltip: 'Toggle theme',
                  onPressed: () {},
                ),
                const Spacer(),
                _SquareButton(
                  icon: Icons.chevron_left_rounded,
                  tooltip: 'Collapse navigation',
                  onPressed: () {},
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _NavItem {
  const _NavItem(this.icon, this.label, this.selected);

  final IconData icon;
  final String label;
  final bool selected;
}

class _NavButton extends StatelessWidget {
  const _NavButton({required this.item});

  final _NavItem item;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 48,
      decoration: BoxDecoration(
        color: item.selected ? AppColors.surface : Colors.transparent,
        borderRadius: BorderRadius.circular(8),
        boxShadow: item.selected
            ? [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.06),
                  blurRadius: 12,
                  offset: const Offset(0, 6),
                ),
              ]
            : null,
      ),
      child: Stack(
        children: [
          if (item.selected)
            Positioned(
              left: 0,
              top: 8,
              bottom: 8,
              child: Container(
                width: 3,
                decoration: BoxDecoration(
                  color: AppColors.teal,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Row(
              children: [
                Icon(
                  item.icon,
                  size: 20,
                  color: item.selected ? AppColors.tealDark : AppColors.muted,
                ),
                const SizedBox(width: 14),
                Text(
                  item.label,
                  style: TextStyle(
                    color: item.selected ? AppColors.tealDark : AppColors.text,
                    fontSize: 13,
                    fontWeight: item.selected
                        ? FontWeight.w800
                        : FontWeight.w600,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _SquareButton extends StatelessWidget {
  const _SquareButton({
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
      icon: Icon(icon, size: 18),
      color: AppColors.muted,
      style: IconButton.styleFrom(
        fixedSize: const Size(42, 42),
        backgroundColor: AppColors.surface,
        side: const BorderSide(color: AppColors.border),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
      ),
    );
  }
}
