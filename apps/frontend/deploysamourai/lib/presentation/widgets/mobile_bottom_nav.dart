import 'package:flutter/material.dart';

import '../../core/theme/app_colors.dart';

class MobileBottomNav extends StatelessWidget {
  const MobileBottomNav({super.key});

  @override
  Widget build(BuildContext context) {
    const items = [
      _BottomItem(Icons.home_outlined, 'Overview', true),
      _BottomItem(Icons.account_tree_outlined, 'Repos', false),
      _BottomItem(Icons.near_me_outlined, 'Deploys', false),
      _BottomItem(Icons.cloud_queue_outlined, 'Envs', false),
      _BottomItem(Icons.settings_outlined, 'Settings', false),
    ];

    return SafeArea(
      top: false,
      child: Container(
        height: 64,
        decoration: const BoxDecoration(
          color: AppColors.surface,
          border: Border(top: BorderSide(color: AppColors.border)),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: [for (final item in items) _BottomNavButton(item: item)],
        ),
      ),
    );
  }
}

class _BottomItem {
  const _BottomItem(this.icon, this.label, this.selected);

  final IconData icon;
  final String label;
  final bool selected;
}

class _BottomNavButton extends StatelessWidget {
  const _BottomNavButton({required this.item});

  final _BottomItem item;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 62,
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            item.icon,
            size: 20,
            color: item.selected ? AppColors.tealDark : AppColors.muted,
          ),
          const SizedBox(height: 3),
          Text(
            item.label,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: TextStyle(
              fontSize: 10,
              color: item.selected ? AppColors.tealDark : AppColors.muted,
              fontWeight: item.selected ? FontWeight.w800 : FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
}
