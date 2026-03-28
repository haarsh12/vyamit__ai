import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';
import 'dart:async';

class Premium3DOrb extends StatefulWidget {
  final bool isActive;
  final VoidCallback onTap;
  
  const Premium3DOrb({
    Key? key,
    required this.isActive,
    required this.onTap,
  }) : super(key: key);

  @override
  State<Premium3DOrb> createState() => _Premium3DOrbState();
}

class _Premium3DOrbState extends State<Premium3DOrb>
    with SingleTickerProviderStateMixin {
  late final Ticker _ticker;
  FragmentProgram? program;
  double time = 0.0;

  @override
  void initState() {
    super.initState();

    FragmentProgram.fromAsset('shaders/orb.frag').then((p) {
      setState(() {
        program = p;
      });
    }).catchError((e) {
      debugPrint('❌ Failed to load shader: $e');
    });

    _ticker = createTicker((elapsed) {
      if (widget.isActive && mounted) {
        setState(() {
          time += 0.016;
        });
      }
    });
    
    if (widget.isActive) {
      _ticker.start();
    }
  }

  @override
  void didUpdateWidget(Premium3DOrb oldWidget) {
    super.didUpdateWidget(oldWidget);
    
    if (widget.isActive != oldWidget.isActive) {
      if (widget.isActive) {
        _ticker.start();
      } else {
        _ticker.stop();
        setState(() {
          time = 0.0;
        });
      }
    }
  }

  @override
  void dispose() {
    _ticker.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (program == null) {
      // Fallback: Show loading or simple circle
      return GestureDetector(
        onTap: widget.onTap,
        child: Container(
          width: 180,
          height: 180,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            gradient: RadialGradient(
              colors: [
                const Color(0xFF00E676),
                const Color(0xFF00897B),
              ],
            ),
          ),
          child: const Center(
            child: CircularProgressIndicator(color: Colors.white),
          ),
        ),
      );
    }

    return GestureDetector(
      onTap: widget.onTap,
      child: CustomPaint(
        size: const Size(180, 180), // Smaller size
        painter: _OrbPainter(program!, time),
      ),
    );
  }
}

class _OrbPainter extends CustomPainter {
  final FragmentProgram program;
  final double time;

  _OrbPainter(this.program, this.time);

  @override
  void paint(Canvas canvas, Size size) {
    final shader = program.fragmentShader();

    shader.setFloat(0, time);
    shader.setFloat(1, size.width);
    shader.setFloat(2, size.height);

    final paint = Paint()..shader = shader;

    canvas.drawRect(
      Rect.fromLTWH(0, 0, size.width, size.height),
      paint,
    );
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}
