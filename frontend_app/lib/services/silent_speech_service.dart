import 'dart:async';
import 'package:flutter/foundation.dart';

/// COMPLETELY SILENT Speech Service
/// Uses manual text input instead of speech recognition to avoid ALL sounds
class SilentSpeechService extends ChangeNotifier {
  // Singleton
  static final SilentSpeechService _instance = SilentSpeechService._internal();
  factory SilentSpeechService() => _instance;
  SilentSpeechService._internal();

  // State
  bool _isActive = false;
  String _transcript = '';
  
  bool get isActive => _isActive;
  String get transcript => _transcript;
  
  // Audio level for animations (simulated)
  double _audioLevel = 0.0;
  double get audioLevel => _audioLevel;
  
  Timer? _animationTimer;

  /// Initialize (no actual speech recognition)
  Future<void> initialize() async {
    debugPrint('✅ Silent Speech Service initialized - NO SOUNDS');
  }

  /// Start "listening" (just activates UI, no actual speech recognition)
  Future<void> startListening() async {
    if (_isActive) return;
    
    _isActive = true;
    _transcript = '';
    
    // Simulate audio level animation
    _startAnimation();
    
    notifyListeners();
    debugPrint('🎙️ Silent mode activated - NO SPEECH RECOGNITION, NO SOUNDS');
  }

  /// Stop "listening"
  Future<void> stopListening() async {
    if (!_isActive) return;
    
    _isActive = false;
    _animationTimer?.cancel();
    _audioLevel = 0.0;
    
    notifyListeners();
    debugPrint('🛑 Silent mode deactivated');
  }

  /// Set transcript manually (for testing or manual input)
  void setTranscript(String text) {
    _transcript = text;
    notifyListeners();
  }

  /// Simulate audio level animation
  void _startAnimation() {
    _animationTimer?.cancel();
    
    _animationTimer = Timer.periodic(
      const Duration(milliseconds: 100),
      (timer) {
        if (!_isActive) {
          timer.cancel();
          return;
        }
        
        // Simulate breathing animation
        _audioLevel = 0.3 + (0.2 * (timer.tick % 10) / 10);
        notifyListeners();
      },
    );
  }

  @override
  void dispose() {
    _animationTimer?.cancel();
    super.dispose();
  }
}
