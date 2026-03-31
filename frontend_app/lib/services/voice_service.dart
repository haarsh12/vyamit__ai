import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;

/// Clean voice service - Manual control only
/// Tap to start, tap to stop. Accumulates text until stopped.
class VoiceService extends ChangeNotifier {
  late stt.SpeechToText _speech;
  
  // State
  bool _isListening = false;
  bool get isListening => _isListening;
  
  bool _keepListeningLoop = false;
  
  // Accumulated transcript (full session)
  String _fullTranscript = '';
  String get fullTranscript => _fullTranscript;
  
  // Current chunk (live)
  String _currentChunk = '';
  String get currentChunk => _currentChunk;
  
  // Combined display text
  String get displayText {
    if (_fullTranscript.isEmpty && _currentChunk.isEmpty) {
      return '';
    }
    return (_fullTranscript + ' ' + _currentChunk).trim();
  }
  
  // Audio level for animation (0.0 to 1.0)
  double _audioLevel = 0.0;
  double get audioLevel => _audioLevel;
  
  Timer? _audioDecayTimer;
  
  /// Initialize speech recognition
  Future<bool> initialize() async {
    try {
      _speech = stt.SpeechToText();
      
      bool available = await _speech.initialize(
        onError: (error) {
          debugPrint('🎤 Speech error: $error');
        },
        onStatus: (status) {
          debugPrint('🎤 Status: $status');
          // Auto-restart if stopped unexpectedly while session is active
          if (_isListening && (status == 'done' || status == 'notListening')) {
            _restartListening();
          }
        },
      );
      
      if (available) {
        debugPrint('✅ Voice service ready');
        return true;
      } else {
        debugPrint('❌ Speech not available');
        return false;
      }
    } catch (e) {
      debugPrint('❌ Init failed: $e');
      return false;
    }
  }
  
  /// Start listening session
  Future<void> startListening() async {
    if (_isListening) return;
    
    try {
      _isListening = true;
      _fullTranscript = '';
      _currentChunk = '';
      _audioLevel = 0.3;
      notifyListeners();
      
      await _startSpeechRecognition();
      _startAudioAnimation();
      
      _keepListeningLoop = true;
      _startListeningLoop();
      
      debugPrint('🎙️ Listening started');
    } catch (e) {
      debugPrint('❌ Start failed: $e');
      _isListening = false;
      notifyListeners();
    }
  }
  
  /// Internal speech recognition start
  Future<void> _startSpeechRecognition() async {
    await _speech.listen(
      onResult: _handleResult,
      listenMode: stt.ListenMode.dictation,
      partialResults: true,
      localeId: 'en_IN',
      cancelOnError: false,
      listenFor: const Duration(minutes: 10), // Very long session
      pauseFor: const Duration(seconds: 30), // Allow long pauses
    );
  }
  
  void _startListeningLoop() async {
    while (_keepListeningLoop) {
      await Future.delayed(const Duration(seconds: 1));

      if (_isListening && !_speech.isListening) {
        try {
          await _startSpeechRecognition();
          debugPrint("🔄 Forced restart listening");
        } catch (e) {
          debugPrint("❌ Loop restart error: $e");
        }
      }
    }
  }
  
  /// Restart listening quietly (for continuous session)
  Future<void> _restartListening() async {
    if (!_isListening) return;
    
    try {
      await Future.delayed(const Duration(milliseconds: 100));
      if (_isListening) {
        await _startSpeechRecognition();
        debugPrint('🔄 Listening restarted');
      }
    } catch (e) {
      debugPrint('❌ Restart failed: $e');
    }
  }
  
  /// Stop listening and return final transcript
  Future<String> stopListening() async {
    if (!_isListening) return '';
    
    try {
      _keepListeningLoop = false;
      await _speech.stop();
      
      _audioDecayTimer?.cancel();
      _isListening = false;
      _audioLevel = 0.0;
      
      // Combine all text
      final finalText = (_fullTranscript + ' ' + _currentChunk).trim();
      
      // Clear state
      _fullTranscript = '';
      _currentChunk = '';
      
      notifyListeners();
      
      debugPrint('🛑 Stopped. Final text: $finalText');
      return finalText;
      
    } catch (e) {
      debugPrint('❌ Stop failed: $e');
      return '';
    }
  }
  
  /// Handle speech results
  void _handleResult(result) {
    if (!_isListening) return;
    
    _currentChunk = result.recognizedWords;
    
    // Update audio level
    if (_currentChunk.isNotEmpty) {
      _audioLevel = result.finalResult ? 0.9 : 0.7;
    }
    
    notifyListeners();
    
    // If final result, accumulate it
    if (result.finalResult && _currentChunk.isNotEmpty) {
      _fullTranscript += _currentChunk + ' ';
      _currentChunk = '';
      debugPrint('📝 Accumulated: $_fullTranscript');
    }
  }
  
  /// Audio level decay animation
  void _startAudioAnimation() {
    _audioDecayTimer?.cancel();
    
    _audioDecayTimer = Timer.periodic(
      const Duration(milliseconds: 50),
      (timer) {
        if (!_isListening) {
          timer.cancel();
          return;
        }
        
        // Smooth decay to idle level
        if (_audioLevel > 0.3) {
          _audioLevel = (_audioLevel - 0.02).clamp(0.3, 1.0);
        } else if (_audioLevel < 0.3) {
          _audioLevel = (_audioLevel + 0.02).clamp(0.3, 1.0);
        }
        
        notifyListeners();
      },
    );
  }
  
  @override
  void dispose() {
    _audioDecayTimer?.cancel();
    _speech.stop();
    super.dispose();
  }
}
