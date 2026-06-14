import 'package:flutter/material.dart';

import '../../core/theme/app_colors.dart';

class AppPanel extends StatelessWidget {
  const AppPanel({
    required this.child,
    this.padding = const EdgeInsets.all(20),
    this.title,
    this.leading,
    this.trailing,
    this.compact = false,
    super.key,
  });

  final Widget child;
  final EdgeInsetsGeometry padding;
  final String? title;
  final Widget? leading;
  final Widget? trailing;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    final titleText = title;

    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        color: AppColors.surface,
        border: Border.all(color: AppColors.border),
        borderRadius: BorderRadius.circular(8),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.06),
            blurRadius: 18,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Padding(
        padding: padding,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            if (titleText != null) ...[
              Row(
                children: [
                  if (leading != null) ...[leading!, const SizedBox(width: 8)],
                  Expanded(
                    child: Text(
                      titleText,
                      style: TextStyle(
                        color: AppColors.text,
                        fontSize: compact ? 15 : 18,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ),
                  ?trailing,
                ],
              ),
              SizedBox(height: compact ? 12 : 16),
            ],
            child,
          ],
        ),
      ),
    );
  }
}
