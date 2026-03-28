import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:flutter_tts/flutter_tts.dart';
import 'api_client.dart';

/// Premium Voice Service - TRULY SILENT continuous listening
/// NO AUTO-RESTART - Single long session to avoid repeated sounds
class PremiumVoiceService extends ChangeNotifier {
  // Singleton
  static final PremiumVoiceService _instance = PremiumVoiceService._internal();
  factory PremiumVoiceService() => _instance;
  PremiumVoiceService._internal();

  // Core services
  late stt.SpeechToText _speech;
  late FlutterTts _tts;
  final ApiClient _apiClient = ApiClient();

  // State
  bool _isActive = false;
  bool _isProcessing = false;
  bool _isSpeaking = false;
  
  bool get isActive => _isActive;
  bool get isProcessing => _isProcessing;
  bool get isSpeaking => _isSpeaking;

  // Transcript management
  String _liveTranscript = '';
  String _accumulatedText = '';
  
  String get liveTranscript => _liveTranscript;
  String get fullTranscript => _accumulatedText + _liveTranscript;

  // Audio level for animations (0.0 to 1.0)
  double _audioLevel = 0.0;
  double get audioLevel => _audioLevel;

  // Timing
  DateTime _lastSpeechTime = DateTime.now();
  Timer? _silenceMonitor;
  Timer? _audioLevelDecay;
  
  // Configuration
  static const int silenceTimeoutSeconds = 40;
  static const int audioLevelDecayMs = 100;

  // User context
  List<Map<String, dynamic>> _inventory = [];
  int? _userId;

  // Callbacks
  Function(List<dynamic>)? onBillUpdate;
  Function(String)? onResponse;

  /// Initialize the service
  Future<void> initialize() async {
    _speech = stt.SpeechToText();
    _tts = FlutterTts();
    
    // Configure TTS (silent by default, only for responses)
    await _tts.setLanguage("hi-IN");
    await _tts.setPitch(1.0);
    await _tts.setSpeechRate(0.5);
    await _tts.setVolume(1.0);
    await _tts.awaitSpeakCompletion(true);
    
    _tts.setCompletionHandler(() {
      _isSpeaking = false;
      notifyListeners();
    });

    debugPrint('✅ PremiumVoiceService initialized - NO AUTO-RESTART MODE');
  }

  /// Set user context
  void setContext({
    required List<Map<String, dynamic>> inventory,
    required int userId,
  }) {
    _inventory = inventory;
    _userId = userId;
  }

  /// Start listening session - SINGLE LONG SESSION
  Future<void> startListening() async {
    if (_isActive) {
      debugPrint('⚠️ Already listening');
      return;
    }

    try {
      // Initialize speech recognition ONCE
      bool available = await _speech.initialize(
        onError: (error) {
          debugPrint('⚠️ Speech error: $error');
          // DO NOT AUTO-RESTART - just log the error
        },
        onStatus: (status) {
          debugPrint('📊 Status: $status');
          // DO NOT AUTO-RESTART - let it run
        },
      );

      if (!available) {
        debugPrint('❌ Speech not available');
        return;
      }

      // Start ONE LONG listening session
      await _speech.listen(
        onResult: _handleSpeechResult,
        listenMode: stt.ListenMode.dictation,
        partialResults: true,
        localeId: 'hi-IN',
        cancelOnError: false,
        // CRITICAL: Very long duration to avoid restarts
        listenFor: const Duration(minutes: 10), // 10 minutes!
        pauseFor: const Duration(seconds: 10),  // Allow long pauses
      );
      
      // Start monitoring
      _startSilenceMonitor();
      _startAudioLevelDecay();
      
      _isActive = true;
      _lastSpeechTime = DateTime.now();
      
      notifyListeners();
      debugPrint('🎙️ SINGLE LONG SESSION STARTED (10 min max) - NO RESTARTS');
      
    } catch (e) {
      debugPrint('❌ Start failed: $e');
    }
  }

  /// Handle speech results
  void _handleSpeechResult(result) {
    if (!_isActive) return;

    _liveTranscript = result.recognizedWords;
    
    if (_liveTranscript.isNotEmpty) {
      _lastSpeechTime = DateTime.now();
      
      // Update audio level based on speech activity
      _audioLevel = result.finalResult ? 0.8 : 0.6;
      notifyListeners();
    }

    // On final result, accumulate and check for query
    if (result.finalResult && _liveTranscript.isNotEmpty) {
      _accumulatedText += _liveTranscript + ' ';
      _liveTranscript = '';
      
      debugPrint('📝 Accumulated: $_accumulatedText');
      
      // Check if it's a query
      if (_isQuery(_accumulatedText)) {
        _handleQuery();
      }
    }
  }

  /// Start silence monitor
  void _startSilenceMonitor() {
    _silenceMonitor?.cancel();
    
    _silenceMonitor = Timer.periodic(
      const Duration(seconds: 1),
      (timer) {
        if (!_isActive) {
          timer.cancel();
          return;
        }

        final silenceDuration = DateTime.now().difference(_lastSpeechTime);
        
        // Timeout after 40 seconds
        if (silenceDuration.inSeconds >= silenceTimeoutSeconds) {
          debugPrint('⏱️ Silence timeout');
          _handleTimeout();
        }
      },
    );
  }

  /// Start audio level decay animation
  void _startAudioLevelDecay() {
    _audioLevelDecay?.cancel();
    
    _audioLevelDecay = Timer.periodic(
      const Duration(milliseconds: audioLevelDecayMs),
      (timer) {
        if (!_isActive) {
          timer.cancel();
          return;
        }

        // Decay audio level smoothly
        if (_audioLevel > 0.2) {
          _audioLevel = (_audioLevel - 0.05).clamp(0.2, 1.0);
          notifyListeners();
        }
      },
    );
  }

  /// Check if text is a query
  bool _isQuery(String text) {
    final lower = text.toLowerCase().trim();
    
    // Query patterns
    final patterns = [
      'kitna',
      'kya hai',
      'batao',
      'bata do',
      'price',
      'rate',
      'cost',
      'kya',
      '?',
    ];

    return patterns.any((p) => lower.contains(p));
  }

  /// Handle query mode
  Future<void> _handleQuery() async {
    final query = _accumulatedText.trim();
    
    if (query.isEmpty) return;

    try {
      // Stop listening ONCE
      if (_speech.isListening) {
        await _speech.stop();
      }
      
      _isProcessing = true;
      notifyListeners();
      
      debugPrint('❓ Processing query: $query');
      
      // Send to backend
      final response = await _apiClient.post('/voice/process-query', {
        'transcript': query,
        'user_id': _userId,
        'inventory': _inventory,
      });

      if (response['success'] == true) {
        final answer = response['answer'] as String?;
        final shouldContinue = response['continue_listening'] as bool? ?? false;
        
        // Speak answer if available
        if (answer != null && answer.isNotEmpty) {
          await _speakResponse(answer);
          
          if (onResponse != null) {
            onResponse!(answer);
          }
        }
        
        // Clear transcript
        _accumulatedText = '';
        _liveTranscript = '';
        
        // Continue or stop based on response
        if (shouldContinue) {
          _isProcessing = false;
          // Restart ONCE for continuation
          await startListening();
        } else {
          await stopListening();
        }
      } else {
        await stopListening();
      }
      
    } catch (e) {
      debugPrint('❌ Query failed: $e');
      await stopListening();
    }
  }

  /// Handle timeout
  Future<void> _handleTimeout() async {
    final text = _accumulatedText.trim();
    
    if (text.isEmpty) {
      await stopListening();
      return;
    }

    try {
      // Stop listening ONCE
      if (_speech.isListening) {
        await _speech.stop();
      }
      
      _isProcessing = true;
      notifyListeners();
      
      debugPrint('📤 Sending on timeout: $text');
      
      // Send to backend
      final response = await _apiClient.post('/voice/process-billing', {
        'transcript': text,
        'user_id': _userId,
        'inventory': _inventory,
      });

      if (response['success'] == true) {
        final billUpdates = response['bill_updates'] as List?;
        
        if (billUpdates != null && billUpdates.isNotEmpty) {
          if (onBillUpdate != null) {
            onBillUpdate!(billUpdates);
          }
        }
      }
      
    } catch (e) {
      debugPrint('❌ Timeout processing failed: $e');
    } finally {
      await stopListening();
    }
  }

  /// Speak response using TTS
  Future<void> _speakResponse(String text) async {
    _isSpeaking = true;
    notifyListeners();
    
    try {
      await _tts.speak(text);
      debugPrint('🔊 Speaking: $text');
    } catch (e) {
      debugPrint('❌ TTS failed: $e');
      _isSpeaking = false;
      notifyListeners();
    }
  }

  /// Stop listening - CLEAN STOP
  Future<void> stopListening() async {
    if (!_isActive) return;

    try {
      // Send any remaining text
      final text = _accumulatedText.trim();
      
      if (text.isNotEmpty && !_isProcessing) {
        _isProcessing = true;
        notifyListeners();
        
        debugPrint('📤 Sending final: $text');
        
        final response = await _apiClient.post('/voice/process-billing', {
          'transcript': text,
          'user_id': _userId,
          'inventory': _inventory,
        });

        if (response['success'] == true) {
          final billUpdates = response['bill_updates'] as List?;
          
          if (billUpdates != null && billUpdates.isNotEmpty) {
            if (onBillUpdate != null) {
              onBillUpdate!(billUpdates);
            }
          }
        }
      }

      // Stop ONCE
      if (_speech.isListening) {
        await _speech.stop();
      }
      
      // Cancel timers
      _silenceMonitor?.cancel();
      _audioLevelDecay?.cancel();
      
      // Reset state
      _isActive = false;
      _isProcessing = false;
      _accumulatedText = '';
      _liveTranscript = '';
      _audioLevel = 0.0;
      
      notifyListeners();
      debugPrint('🛑 CLEAN STOP - No restart');
      
    } catch (e) {
      debugPrint('❌ Stop failed: $e');
    }
  }

  @override
  void dispose() {
    _silenceMonitor?.cancel();
    _audioLevelDecay?.cancel();
    _speech.stop();
    _tts.stop();
    super.dispose();
  }
}
