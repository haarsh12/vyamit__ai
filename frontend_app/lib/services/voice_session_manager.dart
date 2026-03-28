import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:flutter_tts/flutter_tts.dart';
import 'api_client.dart';

/// Voice session state machine
enum VoiceState {
  idle,
  listening,
  processing,
  speaking,
  timeout,
}

/// Voice session manager - Singleton pattern
/// Handles continuous voice listening with GPT-style behavior
class VoiceSessionManager extends ChangeNotifier {
  // Singleton instance
  static final VoiceSessionManager _instance = VoiceSessionManager._internal();
  factory VoiceSessionManager() => _instance;
  VoiceSessionManager._internal();

  // Core dependencies
  late stt.SpeechToText _speech;
  late FlutterTts _tts;
  final ApiClient _apiClient = ApiClient();

  // State management
  VoiceState _state = VoiceState.idle;
  VoiceState get state => _state;

  // Transcript accumulation
  String _accumulatedTranscript = '';
  String _currentChunk = '';
  String get currentTranscript => _accumulatedTranscript + _currentChunk;

  // Timing control
  DateTime _lastSpokenTime = DateTime.now();
  Timer? _silenceTimer;
  Timer? _chunkSyncTimer;
  
  // Configuration
  static const int silenceTimeoutSeconds = 40;
  static const int chunkSyncIntervalSeconds = 30;
  static const int silenceCheckIntervalMs = 1000;

  // Audio level for animation
  double _audioLevel = 0.0;
  double get audioLevel => _audioLevel;

  // Session control
  bool _isSessionActive = false;
  bool get isSessionActive => _isSessionActive;

  // User context
  List<Map<String, dynamic>> _userInventory = [];
  int? _userId;
  
  // Callback for bill updates
  Function(List<dynamic>)? onBillUpdates;

  /// Initialize the voice session manager
  Future<void> initialize() async {
    _speech = stt.SpeechToText();
    _tts = FlutterTts();
    
    await _configureTTS();
    
    debugPrint('✅ VoiceSessionManager initialized');
  }

  /// Configure TTS settings
  Future<void> _configureTTS() async {
    await _tts.setLanguage("hi-IN");
    await _tts.setPitch(1.0);
    await _tts.setSpeechRate(0.5);
    await _tts.awaitSpeakCompletion(true);
    
    _tts.setCompletionHandler(() {
      if (_state == VoiceState.speaking) {
        _setState(VoiceState.idle);
      }
    });
  }

  /// Set user context for AI processing
  void setUserContext({
    required List<Map<String, dynamic>> inventory,
    required int userId,
  }) {
    _userInventory = inventory;
    _userId = userId;
  }

  /// Start continuous listening session
  Future<void> startListening() async {
    if (_isSessionActive) {
      debugPrint('⚠️ Session already active');
      return;
    }

    try {
      // Initialize speech recognition
      bool available = await _speech.initialize(
        onError: _handleSpeechError,
        onStatus: _handleSpeechStatus,
      );

      if (!available) {
        debugPrint('❌ Speech recognition not available');
        return;
      }

      // Start listening
      await _startListeningInternal();
      
      // Start timers
      _startSilenceTimer();
      _startChunkSyncTimer();
      
      _isSessionActive = true;
      _setState(VoiceState.listening);
      
      debugPrint('🎙️ Voice session started');
      
    } catch (e) {
      debugPrint('❌ Failed to start listening: $e');
      _setState(VoiceState.idle);
    }
  }

  /// Internal speech recognition start
  Future<void> _startListeningInternal() async {
    await _speech.listen(
      onResult: _handleSpeechResult,
      listenMode: stt.ListenMode.dictation,
      partialResults: true,
      localeId: 'hi-IN',
      cancelOnError: false,
      listenFor: const Duration(seconds: 60), // Max duration per session
    );
  }

  /// Handle speech recognition results
  void _handleSpeechResult(result) {
    _currentChunk = result.recognizedWords;
    
    // Update last spoken time on any speech
    if (_currentChunk.isNotEmpty) {
      _lastSpokenTime = DateTime.now();
      
      // Simulate audio level for animation (0.0 to 1.0)
      _audioLevel = 0.5 + (0.5 * (result.finalResult ? 0.8 : 0.6));
      notifyListeners();
    }

    // If final result, accumulate and reset chunk
    if (result.finalResult && _currentChunk.isNotEmpty) {
      _accumulatedTranscript += _currentChunk + ' ';
      _currentChunk = '';
      
      debugPrint('📝 Accumulated: $_accumulatedTranscript');
    }
  }

  /// Handle speech recognition errors
  void _handleSpeechError(dynamic error) {
    debugPrint('⚠️ Speech error: $error');
    
    // Auto-restart on error if session is active
    if (_isSessionActive && _state == VoiceState.listening) {
      _restartListeningQuietly();
    }
  }

  /// Handle speech recognition status changes
  void _handleSpeechStatus(String status) {
    debugPrint('📊 Speech status: $status');
    
    // Auto-restart if stopped unexpectedly
    if (status == 'done' || status == 'notListening') {
      if (_isSessionActive && _state == VoiceState.listening) {
        _restartListeningQuietly();
      }
    }
  }

  /// Quietly restart listening without UI changes
  Future<void> _restartListeningQuietly() async {
    try {
      await Future.delayed(const Duration(milliseconds: 100));
      
      if (_isSessionActive && _state == VoiceState.listening) {
        await _startListeningInternal();
        debugPrint('🔄 Listening restarted quietly');
      }
    } catch (e) {
      debugPrint('❌ Failed to restart: $e');
    }
  }

  /// Start silence detection timer
  void _startSilenceTimer() {
    _silenceTimer?.cancel();
    _lastSpokenTime = DateTime.now();
    
    _silenceTimer = Timer.periodic(
      const Duration(milliseconds: silenceCheckIntervalMs),
      (timer) {
        final silenceDuration = DateTime.now().difference(_lastSpokenTime);
        
        // Reset audio level if no speech
        if (silenceDuration.inSeconds > 2) {
          _audioLevel = 0.2; // Idle breathing level
          notifyListeners();
        }
        
        // Timeout after 40 seconds of silence
        if (silenceDuration.inSeconds >= silenceTimeoutSeconds) {
          debugPrint('⏱️ Silence timeout reached');
          _handleSilenceTimeout();
        }
      },
    );
  }

  /// Start 30-second chunk sync timer
  void _startChunkSyncTimer() {
    _chunkSyncTimer?.cancel();
    
    _chunkSyncTimer = Timer.periodic(
      const Duration(seconds: chunkSyncIntervalSeconds),
      (timer) async {
        if (_isSessionActive && _state == VoiceState.listening) {
          await _sendChunkToBackend();
        }
      },
    );
  }

  /// Send accumulated transcript chunk to backend
  Future<void> _sendChunkToBackend() async {
    final transcript = _accumulatedTranscript.trim();
    
    if (transcript.isEmpty) {
      debugPrint('⏭️ No transcript to send');
      return;
    }

    try {
      debugPrint('📤 Sending chunk to backend: $transcript');
      
      // Detect intent first
      final isQuery = _detectQueryIntent(transcript);
      
      if (isQuery) {
        // Query mode - stop and process
        await _handleQueryMode(transcript);
        return;
      }

      // Billing mode - continue listening
      final response = await _apiClient.post('/voice/process-chunk', {
        'transcript': transcript,
        'user_id': _userId,
        'inventory': _userInventory,
        'mode': 'billing',
      });

      // Process response
      if (response['success'] == true) {
        final billUpdates = response['bill_updates'] as List?;
        
        if (billUpdates != null && billUpdates.isNotEmpty) {
          // Notify listeners about bill updates
          _notifyBillUpdates(billUpdates);
        }
        
        // Clear accumulated transcript after successful sync
        _accumulatedTranscript = '';
        
        debugPrint('✅ Chunk processed successfully');
      }
      
    } catch (e) {
      debugPrint('❌ Failed to send chunk: $e');
    }
  }

  /// Detect if transcript is a query
  bool _detectQueryIntent(String transcript) {
    final lowerTranscript = transcript.toLowerCase();
    
    // Query patterns
    final queryPatterns = [
      'kitna',
      'kya hai',
      'batao',
      'bata do',
      'price',
      'rate',
      'cost',
      '?',
    ];

    return queryPatterns.any((pattern) => lowerTranscript.contains(pattern));
  }

  /// Handle query mode
  Future<void> _handleQueryMode(String transcript) async {
    try {
      // Stop listening
      await _stopListeningInternal();
      _setState(VoiceState.processing);
      
      debugPrint('❓ Query detected: $transcript');
      
      // Send to backend
      final response = await _apiClient.post('/voice/process-query', {
        'transcript': transcript,
        'user_id': _userId,
        'inventory': _userInventory,
        'mode': 'query',
      });

      if (response['success'] == true) {
        final answer = response['answer'] as String?;
        final mode = response['mode'] as String?;
        
        if (answer != null && answer.isNotEmpty) {
          // Speak answer
          await _speakAnswer(answer);
        }
        
        // Check mode
        if (mode == 'billing') {
          // Resume listening
          await startListening();
        } else {
          // Deactivate
          await stopListening();
        }
      } else {
        await stopListening();
      }
      
    } catch (e) {
      debugPrint('❌ Query processing failed: $e');
      await stopListening();
    }
  }

  /// Speak answer using TTS
  Future<void> _speakAnswer(String answer) async {
    _setState(VoiceState.speaking);
    
    try {
      await _tts.speak(answer);
      debugPrint('🔊 Speaking: $answer');
    } catch (e) {
      debugPrint('❌ TTS failed: $e');
      _setState(VoiceState.idle);
    }
  }

  /// Handle silence timeout
  Future<void> _handleSilenceTimeout() async {
    _setState(VoiceState.timeout);
    
    // Send final transcript
    await _sendChunkToBackend();
    
    // Stop session
    await stopListening();
    
    debugPrint('⏱️ Session ended due to silence timeout');
  }

  /// Stop listening session
  Future<void> stopListening() async {
    if (!_isSessionActive) return;

    try {
      // Send any remaining transcript
      if (_accumulatedTranscript.trim().isNotEmpty) {
        await _sendChunkToBackend();
      }

      await _stopListeningInternal();
      
      // Cancel timers
      _silenceTimer?.cancel();
      _chunkSyncTimer?.cancel();
      
      // Reset state
      _isSessionActive = false;
      _accumulatedTranscript = '';
      _currentChunk = '';
      _audioLevel = 0.0;
      _setState(VoiceState.idle);
      
      debugPrint('🛑 Voice session stopped');
      
    } catch (e) {
      debugPrint('❌ Failed to stop listening: $e');
    }
  }

  /// Internal stop listening
  Future<void> _stopListeningInternal() async {
    if (_speech.isListening) {
      await _speech.stop();
    }
  }

  /// Set state and notify listeners
  void _setState(VoiceState newState) {
    if (_state != newState) {
      _state = newState;
      notifyListeners();
    }
  }

  /// Notify about bill updates (to be handled by UI)
  void _notifyBillUpdates(List<dynamic> updates) {
    debugPrint('📊 Bill updates: ${updates.length} items');
    
    // Call callback if set
    if (onBillUpdates != null) {
      onBillUpdates!(updates);
    }
  }

  /// Dispose resources
  @override
  void dispose() {
    _silenceTimer?.cancel();
    _chunkSyncTimer?.cancel();
    _speech.stop();
    _tts.stop();
    super.dispose();
  }
}
