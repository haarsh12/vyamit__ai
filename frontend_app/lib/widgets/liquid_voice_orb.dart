import 'dart:math';
import 'package:flutter/material.dart';

/// Premium Liquid Morphing Voice Orb
/// Tap to start listening, tap again to stop
/// Features:
/// - Static grey circle when idle
/// - Liquid morphing animation when active
/// - Premium green gradient with glow
/// - AI-style breathing motion
class LiquidVoiceOrb extends StatefulWidget {
  final bool isListening;
  final VoidCallback onTap;
  final double size;

  const LiquidVoiceOrb({
    super.key,
    required this.isListening,
    required this.onTap,
    this.size = 170,
  });

  @override
  State<LiquidVoiceOrb> createState() => _LiquidVoiceOrbState();
}

class _LiquidVoiceOrbState extends State<LiquidVoiceOrb>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();

    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 4),
    );

    if (widget.isListening) {
      _controller.repeat();
    }
  }

  @override
  void didUpdateWidget(covariant LiquidVoiceOrb oldWidget) {
    super.didUpdateWidget(oldWidget);

    if (widget.isListening) {
      _controller.repeat();
    } else {
      _controller.stop();
    }
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: widget.onTap,
      child: AnimatedBuilder(
        animation: _controller,
        builder: (_, __) {
          if (!widget.isListening) {
            // Static grey circle when idle
            return Container(
              width: widget.size,
              height: widget.size,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: Colors.grey.shade300,
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.1),
                    blurRadius: 15,
                    spreadRadius: 2,
                  ),
                ],
              ),
              child: const Icon(
                Icons.mic_none_rounded,
                size: 60,
                color: Colors.white,
              ),
            );
          }

          // Liquid morphing orb when listening
          return Container(
            width: widget.size,
            height: widget.size,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(
                  color: Colors.greenAccent.withOpacity(0.6),
                  blurRadius: 40,
                  spreadRadius: 10,
                ),
              ],
            ),
            child: CustomPaint(
              painter: _LiquidPainter(_controller.value),
              child: const Center(
                child: Icon(
                  Icons.graphic_eq,
                  size: 60,
                  color: Colors.white,
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }
}

class _LiquidPainter extends CustomPainter {
  final double animationValue;

  _LiquidPainter(this.animationValue);

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2;

    final paint = Paint()
      ..shader = const RadialGradient(
        colors: [
          Color(0xFF00C896),
          Color(0xFF00A86B),
          Color(0xFF00695C),
        ],
      ).createShader(Rect.fromCircle(center: center, radius: radius));

    final path = Path();

    const int waveCount = 6;
    const double amplitude = 12;

    for (int i = 0; i <= 360; i++) {
      final angle = i * pi / 180;

      final wave = sin(
        waveCount * angle + (animationValue * 2 * pi),
      );

      final r = radius + wave * amplitude;

      final x = center.dx + r * cos(angle);
      final y = center.dy + r * sin(angle);

      if (i == 0) {
        path.moveTo(x, y);
      } else {
        path.lineTo(x, y);
      }
    }

    path.close();
    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}
