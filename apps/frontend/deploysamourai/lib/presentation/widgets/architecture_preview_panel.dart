import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../../core/theme/app_colors.dart';
import '../../domain/entities/dashboard_snapshot.dart';
import 'app_panel.dart';

class ArchitecturePreviewPanel extends StatelessWidget {
  const ArchitecturePreviewPanel({
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
      title: 'Architecture Preview',
      trailing: TextButton.icon(
        onPressed: () {},
        icon: Icon(
          compact ? Icons.open_in_full_rounded : Icons.open_in_new_rounded,
          size: 14,
        ),
        label: Text(compact ? 'View full' : 'View full'),
        style: TextButton.styleFrom(
          foregroundColor: AppColors.muted,
          textStyle: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800),
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
          minimumSize: Size.zero,
          tapTargetSize: MaterialTapTargetSize.shrinkWrap,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
            side: const BorderSide(color: AppColors.border),
          ),
        ),
      ),
      child: Column(
        children: [
          ArchitectureDiagram(
            resources: snapshot.architectureResources,
            connections: snapshot.architectureConnections,
            compact: compact,
          ),
          if (snapshot.architectureSummary.isNotEmpty) ...[
            const SizedBox(height: 12),
            Text(
              snapshot.architectureSummary,
              maxLines: compact ? 3 : 4,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(
                color: AppColors.muted,
                fontSize: 12,
                height: 1.35,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
          if (!compact) ...[
            const SizedBox(height: 18),
            for (final fact in snapshot.stackFacts)
              Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: _StackFactRow(fact: fact),
              ),
          ],
        ],
      ),
    );
  }
}

class ArchitectureDiagram extends StatelessWidget {
  const ArchitectureDiagram({
    required this.resources,
    required this.connections,
    required this.compact,
    super.key,
  });

  final List<ArchitectureResource> resources;
  final List<ArchitectureConnection> connections;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: compact ? 176 : 238,
      child: LayoutBuilder(
        builder: (context, constraints) {
          final width = constraints.maxWidth;
          final cardWidth = math.min(compact ? 124.0 : 132.0, width * 0.43);
          final cardHeight = compact ? 48.0 : 62.0;
          final left = 8.0;
          final right = width - cardWidth - 8;
          final top = compact ? 6.0 : 12.0;
          final bottom = compact ? 104.0 : 136.0;
          final slots = [
            Rect.fromLTWH(left, top, cardWidth, cardHeight),
            Rect.fromLTWH(right, top, cardWidth, cardHeight),
            Rect.fromLTWH(left, bottom, cardWidth, cardHeight),
            Rect.fromLTWH(right, bottom, cardWidth, cardHeight),
          ];
          final visibleResources = resources.take(4).toList();
          final positions = <String, Rect>{
            for (var index = 0; index < visibleResources.length; index++)
              visibleResources[index].id: slots[index],
          };

          return Stack(
            children: [
              if (visibleResources.isEmpty)
                const Center(
                  child: Text(
                    'Run analysis to preview service boundaries.',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: AppColors.muted,
                      fontSize: 12,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              Positioned.fill(
                child: CustomPaint(
                  painter: _ArchitectureConnectorPainter(
                    positions: positions,
                    connections: connections,
                  ),
                ),
              ),
              for (final resource in visibleResources)
                if (positions.containsKey(resource.id))
                  Positioned.fromRect(
                    rect: positions[resource.id]!,
                    child: _ArchitectureResourceCard(
                      resource: resource,
                      compact: compact,
                    ),
                  ),
            ],
          );
        },
      ),
    );
  }
}

class _ArchitectureResourceCard extends StatelessWidget {
  const _ArchitectureResourceCard({
    required this.resource,
    required this.compact,
  });

  final ArchitectureResource resource;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    final iconMeta = _iconMeta(resource.type);

    return Container(
      padding: EdgeInsets.all(compact ? 8 : 10),
      decoration: BoxDecoration(
        color: AppColors.surface,
        border: Border.all(color: AppColors.border),
        borderRadius: BorderRadius.circular(8),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.08),
            blurRadius: 12,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: Row(
        children: [
          Container(
            width: compact ? 26 : 34,
            height: compact ? 26 : 38,
            decoration: BoxDecoration(
              color: iconMeta.color,
              borderRadius: BorderRadius.circular(6),
            ),
            child: Icon(
              iconMeta.icon,
              color: Colors.white,
              size: compact ? 16 : 20,
            ),
          ),
          SizedBox(width: compact ? 7 : 10),
          Expanded(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  resource.title,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(
                    color: AppColors.text,
                    fontSize: compact ? 10.5 : 12,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  resource.caption,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(
                    color: AppColors.muted,
                    fontSize: compact ? 9 : 10,
                    fontWeight: FontWeight.w600,
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

class _StackFactRow extends StatelessWidget {
  const _StackFactRow({required this.fact});

  final StackFact fact;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: Text(
            fact.label,
            style: const TextStyle(
              color: AppColors.muted,
              fontSize: 12,
              fontWeight: FontWeight.w700,
            ),
          ),
        ),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
          decoration: BoxDecoration(
            color: AppColors.surfaceMuted,
            border: Border.all(color: AppColors.border),
            borderRadius: BorderRadius.circular(6),
          ),
          child: Text(
            fact.value,
            style: const TextStyle(
              color: AppColors.text,
              fontSize: 12,
              fontWeight: FontWeight.w700,
            ),
          ),
        ),
      ],
    );
  }
}

class _ArchitectureConnectorPainter extends CustomPainter {
  const _ArchitectureConnectorPainter({
    required this.positions,
    required this.connections,
  });

  final Map<String, Rect> positions;
  final List<ArchitectureConnection> connections;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = AppColors.faint
      ..strokeWidth = 1.4
      ..style = PaintingStyle.stroke;

    for (final connection in connections) {
      final from = positions[connection.fromId];
      final to = positions[connection.toId];
      if (from == null || to == null) {
        continue;
      }

      final start = _edgePoint(from, to.center);
      final end = _edgePoint(to, from.center);
      canvas.drawLine(start, end, paint);
      _drawArrowHead(canvas, paint, start, end);
    }
  }

  Offset _edgePoint(Rect rect, Offset target) {
    final center = rect.center;
    final dx = target.dx - center.dx;
    final dy = target.dy - center.dy;
    if (dx.abs() > dy.abs()) {
      return Offset(dx > 0 ? rect.right : rect.left, center.dy);
    }
    return Offset(center.dx, dy > 0 ? rect.bottom : rect.top);
  }

  void _drawArrowHead(Canvas canvas, Paint paint, Offset start, Offset end) {
    final angle = math.atan2(end.dy - start.dy, end.dx - start.dx);
    const length = 7.0;
    const spread = math.pi / 7;
    final path = Path()
      ..moveTo(end.dx, end.dy)
      ..lineTo(
        end.dx - length * math.cos(angle - spread),
        end.dy - length * math.sin(angle - spread),
      )
      ..moveTo(end.dx, end.dy)
      ..lineTo(
        end.dx - length * math.cos(angle + spread),
        end.dy - length * math.sin(angle + spread),
      );
    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant _ArchitectureConnectorPainter oldDelegate) {
    return oldDelegate.positions != positions ||
        oldDelegate.connections != connections;
  }
}

_IconMeta _iconMeta(ArchitectureResourceType type) {
  switch (type) {
    case ArchitectureResourceType.apiGateway:
      return const _IconMeta(Icons.api_rounded, AppColors.purple);
    case ArchitectureResourceType.lambda:
      return const _IconMeta(Icons.functions_rounded, AppColors.orange);
    case ArchitectureResourceType.sqs:
      return const _IconMeta(Icons.hub_rounded, AppColors.pink);
    case ArchitectureResourceType.dynamoDb:
      return const _IconMeta(Icons.storage_rounded, AppColors.blue);
  }
}

class _IconMeta {
  const _IconMeta(this.icon, this.color);

  final IconData icon;
  final Color color;
}
