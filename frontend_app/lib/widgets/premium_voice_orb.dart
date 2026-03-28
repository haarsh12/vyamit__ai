import 'dart:math' as math;
import 'package:flutter/material.dart';

/// Premium GPT-style voice orb with smooth animations
/// Features:
/// - Smooth breathing animation when idle
/// - Dynamic pulsing based on audio level
/// - Rotating gradient overlay when active
/// - No audio feedback (silent operation)
class PremiumVoiceOrb extends StatefulWidget {
  final bool isActive;
  final bool isProcessing;
  final double audioLevel; // 0.0 to 1.0
  final VoidCallback onTap;
  final double size;

  const PremiumVoiceOrb({
    super.key,
    required this.isActive,
    this.isProcessing = false,
    required this.audioLevel,
    required this.onTap,
    this.size = 140.0,
  });

  @override
  State<PremiumVoiceOrb> createState() => _PremiumVoiceOrbState();
}

class _PremiumVoiceOrbState extends State<PremiumVoiceOrb>
    with TickerProviderStateMixin {
  late AnimationController _breathingController;
  late AnimationController _pulseController;
  late AnimationController _rotationController;
  
  late Animation<double> _breathingAnimation;
  late Animation<double> _pulseAnimation;

  @override
  void initState() {
    super.initState();
    _setupAnimations();
  }

  void _setupAnimations() {
    // Breathing animation (idle state)
    _breathingController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 2000),
    );

    _breathingAnimation = Tween<double>(
      begin: 0.95,
      end: 1.05,
    ).animate(CurvedAnimation(
      parent: _breathingController,
      curve: Curves.easeInOut,
    ));

    // Pulse animation (active state)
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    );

    _pulseAnimation = Tween<double>(
      begin: 1.0,
      end: 1.15,
    ).animate(CurvedAnimation(
      parent: _pulseController,
      curve: Curves.easeInOut,
    ));

    // Rotation animation (continuous)
    _rotationController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 8),
    );

    // Start animations
    _breathingController.repeat(reverse: true);
    _rotationController.repeat();
  }

  @override
  void didUpdateWidget(PremiumVoiceOrb oldWidget) {
    super.didUpdateWidget(oldWidget);

    // Control pulse based on audio level
    if (widget.isActive && widget.audioLevel > 0.3) {
      if (!_pulseController.isAnimating) {
        _pulseController.repeat(reverse: true);
      }
    } else {
      if (_pulseController.isAnimating) {
        _pulseController.stop();
        _pulseController.reset();
      }
    }
  }

  @override
  void dispose() {
    _breathingController.dispose();
    _pulseController.dispose();
    _rotationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: widget.isProcessing ? null : widget.onTap,
      child: AnimatedBuilder(
        animation: Listenable.merge([
          _breathingController,
          _pulseController,
          _rotationController,
        ]),
        builder: (context, child) {
          // Calculate scale based on state
          double scale = 1.0;
          
          if (widget.isActive) {
            // Active: use audio level for dynamic scaling
            final audioScale = 1.0 + (widget.audioLevel * 0.15);
            final pulseScale = widget.audioLevel > 0.4 ? _pulseAnimation.value : 1.0;
            scale = audioScale * pulseScale;
          } else {
            // Idle: gentle breathing
            scale = _breathingAnimation.value;
          }

          return Transform.scale(
            scale: scale,
            child: Container(
              width: widget.size,
              height: widget.size,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: _buildGradient(),
                boxShadow: _buildShadows(),
              ),
              child: Stack(
                alignment: Alignment.center,
                children: [
                  // Rotating gradient overlay (active state)
                  if (widget.isActive && !widget.isProcessing)
                    Transform.rotate(
                      angle: _rotationController.value * 2 * math.pi,
                      child: Container(
                        width: widget.size * 0.85,
                        height: widget.size * 0.85,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          gradient: RadialGradient(
                            colors: [
                              Colors.white.withOpacity(0.15),
                              Colors.transparent,
                            ],
                          ),
                        ),
                      ),
                    ),
                  
                  // Pulsing rings (active state)
                  if (widget.isActive && !widget.isProcessing)
                    ...List.generate(3, (index) {
                      final delay = index * 0.3;
                      final opacity = (1.0 - delay) * widget.audioLevel * 0.3;
                      
                      return Transform.scale(
                        scale: 1.0 + (index * 0.1) + (widget.audioLevel * 0.2),
                        child: Container(
                          width: widget.size,
                          height: widget.size,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            border: Border.all(
                              color: Colors.white.withOpacity(opacity),
                              width: 2,
                            ),
                          ),
                        ),
                      );
                    }),
                  
                  // Icon
                  if (widget.isProcessing)
                    SizedBox(
                      width: widget.size * 0.4,
                      height: widget.size * 0.4,
                      child: const CircularProgressIndicator(
                        color: Colors.white,
                        strokeWidth: 3,
                      ),
                    )
                  else
                    Icon(
                      widget.isActive ? Icons.graphic_eq : Icons.mic_none_rounded,
                      size: widget.size * 0.35,
                      color: Colors.white,
                    ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  /// Build gradient based on state
  Gradient _buildGradient() {
    if (widget.isProcessing) {
      // Processing gradient (blue)
      return const RadialGradient(
        colors: [
          Color(0xFF2196F3),
          Color(0xFF1976D2),
        ],
      );
    } else if (widget.isActive) {
      // Active gradient with audio level intensity (green)
      return RadialGradient(
        colors: [
          Color.lerp(
            const Color(0xFF4CAF50),
            const Color(0xFF66BB6A),
            widget.audioLevel,
          )!,
          Color.lerp(
            const Color(0xFF2E7D32),
            const Color(0xFF4CAF50),
            widget.audioLevel,
          )!,
        ],
        stops: const [0.0, 1.0],
      );
    } else {
      // Idle gradient (light gray)
      return const RadialGradient(
        colors: [
          Color(0xFFE0E0E0),
          Color(0xFFBDBDBD),
        ],
      );
    }
  }

  /// Build shadows based on state
  List<BoxShadow> _buildShadows() {
    if (widget.isProcessing) {
      // Processing glow (blue)
      return [
        BoxShadow(
          color: const Color(0xFF2196F3).withOpacity(0.4),
          blurRadius: 30,
          spreadRadius: 8,
        ),
        BoxShadow(
          color: const Color(0xFF64B5F6).withOpacity(0.3),
          blurRadius: 50,
          spreadRadius: 15,
        ),
      ];
    } else if (widget.isActive) {
      // Active glow with audio level intensity (green)
      final glowIntensity = 0.4 + (widget.audioLevel * 0.3);
      final glowRadius = 25.0 + (widget.audioLevel * 25.0);
      
      return [
        BoxShadow(
          color: const Color(0xFF4CAF50).withOpacity(glowIntensity),
          blurRadius: glowRadius,
          spreadRadius: 8.0 + (widget.audioLevel * 8.0),
        ),
        BoxShadow(
          color: const Color(0xFF81C784).withOpacity(glowIntensity * 0.6),
          blurRadius: glowRadius * 1.5,
          spreadRadius: 15.0 + (widget.audioLevel * 12.0),
        ),
      ];
    } else {
      // Idle shadow
      return [
        BoxShadow(
          color: Colors.black.withOpacity(0.15),
          blurRadius: 20,
          spreadRadius: 3,
        ),
      ];
    }
  }
}
