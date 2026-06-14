import 'package:flutter/material.dart';

import '../../core/theme/app_colors.dart';
import '../../domain/entities/dashboard_snapshot.dart';
import 'app_panel.dart';

class PipelinePanel extends StatelessWidget {
  const PipelinePanel({
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
      title: 'Pipeline',
      trailing: const _LiveProgressLabel(),
      child: compact
          ? _VerticalPipeline(steps: snapshot.pipelineSteps)
          : _HorizontalPipeline(
              steps: snapshot.pipelineSteps,
              elapsed: snapshot.elapsed,
            ),
    );
  }
}

class _LiveProgressLabel extends StatelessWidget {
  const _LiveProgressLabel();

  @override
  Widget build(BuildContext context) {
    return const Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(Icons.circle, size: 7, color: AppColors.teal),
        SizedBox(width: 6),
        Text(
          'Live progress',
          style: TextStyle(
            color: AppColors.tealDark,
            fontSize: 12,
            fontWeight: FontWeight.w700,
          ),
        ),
      ],
    );
  }
}

class _HorizontalPipeline extends StatelessWidget {
  const _HorizontalPipeline({required this.steps, required this.elapsed});

  final List<PipelineStep> steps;
  final String elapsed;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        SizedBox(
          height: 94,
          child: LayoutBuilder(
            builder: (context, constraints) {
              return Stack(
                children: [
                  Positioned.fill(
                    top: 19,
                    bottom: 50,
                    child: CustomPaint(
                      painter: _HorizontalConnectorPainter(steps),
                    ),
                  ),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      for (final step in steps)
                        SizedBox(
                          width: constraints.maxWidth / steps.length,
                          child: _PipelineStepColumn(step: step),
                        ),
                    ],
                  ),
                ],
              );
            },
          ),
        ),
        Container(
          height: 38,
          padding: const EdgeInsets.symmetric(horizontal: 14),
          decoration: BoxDecoration(
            color: AppColors.surfaceMuted,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: AppColors.border),
          ),
          child: Row(
            children: [
              const Expanded(
                child: Text(
                  'Mapping project structure and identifying components...',
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(
                    color: AppColors.muted,
                    fontSize: 12,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
              Text(
                'Elapsed: $elapsed',
                style: const TextStyle(
                  color: AppColors.muted,
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _VerticalPipeline extends StatelessWidget {
  const _VerticalPipeline({required this.steps});

  final List<PipelineStep> steps;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        for (var index = 0; index < steps.length; index++)
          _VerticalStep(step: steps[index], isLast: index == steps.length - 1),
      ],
    );
  }
}

class _VerticalStep extends StatelessWidget {
  const _VerticalStep({required this.step, required this.isLast});

  final PipelineStep step;
  final bool isLast;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 42,
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 28,
            child: Stack(
              alignment: Alignment.topCenter,
              children: [
                if (!isLast)
                  Positioned(
                    top: 22,
                    bottom: 0,
                    child: Container(
                      width: 2,
                      color: _isActive(step.status)
                          ? AppColors.tealLine
                          : AppColors.borderStrong,
                    ),
                  ),
                _StepBadge(step: step, size: 22),
              ],
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Padding(
              padding: const EdgeInsets.only(top: 1),
              child: Row(
                children: [
                  Expanded(
                    child: Text(
                      step.title,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        color: AppColors.text,
                        fontSize: 12,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                  ),
                  Text(
                    step.caption,
                    style: TextStyle(
                      color: step.status == PipelineStepStatus.inProgress
                          ? AppColors.tealDark
                          : AppColors.muted,
                      fontSize: 11,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _PipelineStepColumn extends StatelessWidget {
  const _PipelineStepColumn({required this.step});

  final PipelineStep step;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        _StepBadge(step: step, size: 38),
        const SizedBox(height: 9),
        Text(
          step.title,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          textAlign: TextAlign.center,
          style: const TextStyle(
            color: AppColors.text,
            fontSize: 12,
            fontWeight: FontWeight.w800,
          ),
        ),
        const SizedBox(height: 3),
        Text(
          step.caption,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          textAlign: TextAlign.center,
          style: TextStyle(
            color: step.status == PipelineStepStatus.inProgress
                ? AppColors.tealDark
                : AppColors.muted,
            fontSize: 10,
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }
}

class _StepBadge extends StatelessWidget {
  const _StepBadge({required this.step, required this.size});

  final PipelineStep step;
  final double size;

  @override
  Widget build(BuildContext context) {
    final status = step.status;
    final completed = status == PipelineStepStatus.completed;
    final inProgress = status == PipelineStepStatus.inProgress;
    final locked = status == PipelineStepStatus.locked;
    final iconColor = completed ? Colors.white : AppColors.muted;
    final background = completed ? AppColors.teal : AppColors.surface;

    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: background,
        shape: BoxShape.circle,
        border: Border.all(
          color: inProgress ? AppColors.teal : AppColors.borderStrong,
          width: inProgress ? 2 : 1,
        ),
        boxShadow: completed
            ? [
                BoxShadow(
                  color: AppColors.teal.withValues(alpha: 0.24),
                  blurRadius: 10,
                  offset: const Offset(0, 5),
                ),
              ]
            : null,
      ),
      child: Center(
        child: completed
            ? Icon(Icons.check_rounded, size: size * 0.52, color: iconColor)
            : inProgress
            ? Container(
                width: size * 0.28,
                height: size * 0.28,
                decoration: const BoxDecoration(
                  color: AppColors.teal,
                  shape: BoxShape.circle,
                ),
              )
            : Icon(
                locked
                    ? Icons.lock_outline_rounded
                    : Icons.radio_button_unchecked_rounded,
                size: size * 0.44,
                color: iconColor,
              ),
      ),
    );
  }
}

class _HorizontalConnectorPainter extends CustomPainter {
  const _HorizontalConnectorPainter(this.steps);

  final List<PipelineStep> steps;

  @override
  void paint(Canvas canvas, Size size) {
    if (steps.length < 2) {
      return;
    }

    final inactivePaint = Paint()
      ..color = AppColors.borderStrong
      ..strokeWidth = 2
      ..style = PaintingStyle.stroke;
    final activePaint = Paint()
      ..color = AppColors.tealLine
      ..strokeWidth = 3
      ..style = PaintingStyle.stroke;

    final spacing = size.width / steps.length;
    final y = size.height / 2;

    for (var index = 0; index < steps.length - 1; index++) {
      final start = Offset(spacing * index + spacing / 2, y);
      final end = Offset(spacing * (index + 1) + spacing / 2, y);
      final active =
          _isActive(steps[index].status) &&
          steps[index + 1].status != PipelineStepStatus.pending &&
          steps[index + 1].status != PipelineStepStatus.locked;
      canvas.drawLine(start, end, active ? activePaint : inactivePaint);
    }
  }

  @override
  bool shouldRepaint(covariant _HorizontalConnectorPainter oldDelegate) {
    return oldDelegate.steps != steps;
  }
}

bool _isActive(PipelineStepStatus status) {
  return status == PipelineStepStatus.completed ||
      status == PipelineStepStatus.inProgress;
}
