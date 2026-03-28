import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:flutter_tts/flutter_tts.dart';
import 'package:provider/provider.dart';

import '../core/theme.dart';
import '../models/shop_details.dart';
import '../services/api_client.dart';
import '../providers/bill_provider.dart';
import 'bill_share_modal.dart';
import '../widgets/siri_wave_orb.dart';

class VoiceAssistantScreen extends StatefulWidget {
  final ShopDetails shopDetails;
  final Function(Map<String, dynamic>) onBillFinalized;
  final bool isPrinterConnected;
  final VoidCallback togglePrinter;

  const VoiceAssistantScreen({
    super.key,
    required this.shopDetails,
    required this.onBillFinalized,
    required this.isPrinterConnected,
    required this.togglePrinter,
  });

  @override
  State<VoiceAssistantScreen> createState() => _VoiceAssistantScreenState();
}

class _VoiceAssistantScreenState extends State<VoiceAssistantScreen> {
  late stt.SpeechToText _speech;
  late FlutterTts _flutterTts;
  
  // Native audio control
  static const platform = MethodChannel('com.snapbill/audio');

  bool _isListening = false;
  String _accumulatedText = ""; // Accumulated text during session
  String _currentSpeechChunk = ""; // Live chunk
  String _aiResponseText = "Tap to Start";
  double _audioLevel = 0.0; // For animation
  Timer? _audioLevelTimer;
  final ApiClient _apiClient = ApiClient();
  
  // Edit Mode State
  bool _isEditMode = false;

  @override
  void initState() {
    super.initState();
    _speech = stt.SpeechToText();
    _flutterTts = FlutterTts();
    _initTts();
  }

  @override
  void dispose() {
    _speech.stop();
    _flutterTts.stop();
    _audioLevelTimer?.cancel();
    _unmuteSystemSounds();
    super.dispose();
  }

  /// Mute system sounds (beeps)
  Future<void> _muteSystemSounds() async {
    try {
      await platform.invokeMethod('muteSystemSounds');
      debugPrint('🔇 System sounds muted');
    } catch (e) {
      debugPrint('❌ Failed to mute: $e');
    }
  }

  /// Unmute system sounds
  Future<void> _unmuteSystemSounds() async {
    try {
      await platform.invokeMethod('unmuteSystemSounds');
      debugPrint('🔊 System sounds unmuted');
    } catch (e) {
      debugPrint('❌ Failed to unmute: $e');
    }
  }

  void _initTts() async {
    await _flutterTts.setLanguage("hi-IN");
    await _flutterTts.setPitch(1.0);
    await _flutterTts.setSpeechRate(0.5);
    await _flutterTts.awaitSpeakCompletion(true);
  }

  /// Reset entire voice page
  void _resetVoicePage() {
    // Stop listening if active
    if (_isListening) {
      _speech.stop();
      _audioLevelTimer?.cancel();
      _unmuteSystemSounds();
    }
    
    // Get bill provider
    final billProvider = Provider.of<BillProvider>(context, listen: false);
    
    // Clear everything
    billProvider.clearBill();
    
    setState(() {
      _isListening = false;
      _accumulatedText = '';
      _currentSpeechChunk = '';
      _aiResponseText = 'Tap to Start';
      _audioLevel = 0.0;
      if (_isEditMode) {
        _isEditMode = false;
      }
    });
    
    debugPrint('🔄 Voice page reset');
  }

  /// Get last 2 lines of text for display (scrolling effect)
  String _getDisplayText() {
    final fullText = (_accumulatedText + ' ' + _currentSpeechChunk).trim();
    
    if (fullText.isEmpty) {
      return _isListening ? "Listening..." : "Tap to Start";
    }
    
    // Split by spaces and take last ~15 words (approximately 2 lines)
    final words = fullText.split(' ');
    if (words.length <= 15) {
      return fullText;
    }
    
    // Take last 15 words (scrolling effect - old text disappears)
    final lastWords = words.sublist(words.length - 15);
    return lastWords.join(' ');
  }

  /// Manual tap to start/stop listening
  void _toggleListening() async {
    if (_isListening) {
      // Stop and process
      await _stopListeningAndProcess();
    } else {
      // Start listening
      await _startListening();
    }
  }

  /// Start listening session - TRUE CONTINUOUS MODE
  Future<void> _startListening() async {
    // Mute system beeps FIRST
    await _muteSystemSounds();
    
    // Initialize speech if not already done
    bool available = await _speech.initialize(
      onError: (val) {
        debugPrint('🎤 STT Error: $val');
        // Only restart if still in listening mode and not a permission error
        if (_isListening && !val.errorMsg.toLowerCase().contains('permission')) {
          debugPrint('🔄 Auto-restarting after error...');
          Future.delayed(const Duration(milliseconds: 800), () {
            if (_isListening && mounted) _startSpeechRecognition();
          });
        } else if (val.errorMsg.toLowerCase().contains('permission')) {
          debugPrint('❌ Permission denied - stopping');
          setState(() {
            _isListening = false;
            _aiResponseText = "Microphone permission denied";
            _audioLevel = 0.0;
          });
          _unmuteSystemSounds();
        }
      },
      onStatus: (status) {
        debugPrint('🎤 Status: $status');
        // CRITICAL: Auto-restart when done to keep continuous listening
        // Use longer delay to avoid cutting off speech after pauses
        if (_isListening && (status == 'done' || status == 'notListening')) {
          debugPrint('🔄 Auto-restarting to continue listening (after pause)...');
          Future.delayed(const Duration(milliseconds: 800), () {
            if (_isListening && mounted) _startSpeechRecognition();
          });
        }
      },
    );

    if (available) {
      setState(() {
        _isListening = true;
        _accumulatedText = "";
        _currentSpeechChunk = "";
        _aiResponseText = "Listening...";
        _audioLevel = 0.3;
      });

      await _startSpeechRecognition();
      _startAudioLevelAnimation();
      debugPrint('🎙️ TRUE CONTINUOUS Listening started - Will auto-restart after pauses');
    } else {
      debugPrint('❌ Speech recognition not available');
      setState(() {
        _aiResponseText = "Speech recognition not available";
      });
      await _unmuteSystemSounds();
    }
  }

  /// Internal speech recognition start - TRUE CONTINUOUS MODE
  Future<void> _startSpeechRecognition() async {
    if (!_isListening || !mounted) return; // Safety check
    
    try {
      // Check if speech is available before starting
      if (!_speech.isAvailable) {
        debugPrint('❌ Speech not available, reinitializing...');
        await _startListening();
        return;
      }
      
      await _speech.listen(
        onResult: _handleSpeechResult,
        listenMode: stt.ListenMode.confirmation, // CHANGED: confirmation mode for better pause handling
        partialResults: true,
        localeId: 'en_IN',
        cancelOnError: false,
        // Very long durations - but system will still pause detection
        listenFor: const Duration(minutes: 30), // 30 minutes session
        pauseFor: const Duration(seconds: 3),   // 3 seconds pause detection (realistic)
      );
      
      debugPrint('✅ Speech recognition started (will auto-restart after 3s pause)');
    } catch (e) {
      debugPrint('❌ Listen error: $e');
      // Retry if still in listening mode with longer delay
      if (_isListening && mounted) {
        Future.delayed(const Duration(milliseconds: 800), () {
          if (_isListening && mounted) _startSpeechRecognition();
        });
      }
    }
  }

  /// Audio level animation for orb
  void _startAudioLevelAnimation() {
    _audioLevelTimer?.cancel();
    
    _audioLevelTimer = Timer.periodic(
      const Duration(milliseconds: 100),
      (timer) {
        if (!_isListening) {
          timer.cancel();
          return;
        }
        
        setState(() {
          // Simulate audio level based on speech activity
          if (_currentSpeechChunk.isNotEmpty) {
            _audioLevel = 0.6 + (0.4 * (timer.tick % 10) / 10);
          } else {
            _audioLevel = 0.3 + (0.2 * (timer.tick % 10) / 10);
          }
        });
      },
    );
  }

  /// Handle speech results - ACCUMULATE on final result
  void _handleSpeechResult(result) {
    if (!_isListening || !mounted) return;

    final recognizedWords = result.recognizedWords;
    
    setState(() {
      _currentSpeechChunk = recognizedWords;
      _audioLevel = 0.7; // Show activity
    });

    // CRITICAL: Accumulate on final result to preserve all text
    if (result.finalResult && recognizedWords.isNotEmpty) {
      setState(() {
        // Add space only if accumulated text exists
        if (_accumulatedText.isNotEmpty) {
          _accumulatedText += ' ' + recognizedWords;
        } else {
          _accumulatedText = recognizedWords;
        }
        _currentSpeechChunk = '';
      });
      debugPrint('📝 Accumulated (${_accumulatedText.split(' ').length} words): $_accumulatedText');
    } else if (!result.finalResult) {
      debugPrint('📝 Current chunk: $recognizedWords (partial)');
    }
  }

  /// Stop listening and process accumulated text
  Future<void> _stopListeningAndProcess() async {
    if (!_isListening) return;

    await _speech.stop();
    _audioLevelTimer?.cancel();
    
    // Unmute system sounds
    await _unmuteSystemSounds();

    // Get ALL text (accumulated + current chunk)
    final finalText = (_accumulatedText + ' ' + _currentSpeechChunk).trim();

    setState(() {
      _isListening = false;
      _accumulatedText = '';
      _currentSpeechChunk = '';
      _audioLevel = 0.0;
    });

    debugPrint('🛑 Stopped. Final text: $finalText');

    // Process only if we have text
    if (finalText.isNotEmpty) {
      await _processAiRequest(finalText);
    } else {
      setState(() {
        _aiResponseText = "No speech detected";
      });
    }
  }

  Future<void> _processAiRequest(String text) async {
    try {
      setState(() => _aiResponseText = "Processing...");

      // 1. Call API
      final data = await _apiClient.post('/voice/process', {"text": text});

      // 2. Extract customer name (if provided by AI)
      String customerName = data['customer_name'] ?? "Walk-in";
      final billProvider = Provider.of<BillProvider>(context, listen: false);
      
      // Update customer name in bill provider
      if (customerName != "Walk-in") {
        billProvider.setCustomerName(customerName);
        debugPrint("👤 Customer name set: $customerName");
      }

      // 3. Handle Text Response (Voice)
      String? msg = data['msg'];
      if (msg != null && msg.isNotEmpty) {
        setState(() => _aiResponseText = msg);

        // CRITICAL FIX: await ensures the UI doesn't refresh/interrupt while speaking
        await _flutterTts.speak(msg);
      }

      // 4. Update Bill (Only AFTER voice finishes)
      if (data['type'] == 'BILL') {
        List<dynamic> newItems = data['items'] ?? [];
        
        debugPrint("🎤 VOICE API returned ${newItems.length} items");
        
        for (var item in newItems) {
          debugPrint("🎤 RAW API ITEM: $item");
          
          // Extract quantity and unit properly
          String qtyDisplay = item['qty_display']?.toString() ?? '1kg';
          String qty = item['qty']?.toString() ?? '1';
          String unit = item['unit']?.toString() ?? 'kg';
          
          // If qty_display is missing or default, construct it from qty and unit
          if (qtyDisplay == '1kg' && (qty != '1' || unit != 'kg')) {
            qtyDisplay = '$qty$unit';
          }
          
          // Normalize the item structure to match what printer expects
          final normalizedItem = {
            'name': item['name'] ?? item['en'] ?? item['item_name'] ?? 'Unknown',
            'en': item['en'] ?? item['name'] ?? item['item_name'] ?? 'Unknown',
            'hi': item['hi'] ?? item['name'] ?? item['item_name'] ?? 'Unknown',
            'qty': qty,
            'qty_display': qtyDisplay,
            'rate': (item['rate'] ?? item['price'] ?? item['unit_price'] ?? 0).toDouble(),
            'total': (item['total'] ?? item['line_total'] ?? 0).toDouble(),
            'unit': unit,
          };
          
          debugPrint("🎤 NORMALIZED ITEM: $normalizedItem");
          debugPrint("   ├─ qty_display: ${normalizedItem['qty_display']}");
          debugPrint("   ├─ qty: ${normalizedItem['qty']}");
          debugPrint("   ├─ unit: ${normalizedItem['unit']}");
          debugPrint("   ├─ rate: ${normalizedItem['rate']}");
          debugPrint("   └─ total: ${normalizedItem['total']}");
          
          billProvider.addBillItem(normalizedItem);
        }
      }

      // 5. Resume Listening (Optional - makes it conversational)
      // Uncomment the line below if you want it to auto-listen after speaking
      // _toggleListening();
    } catch (e) {
      debugPrint("Error: $e");
      setState(() => _aiResponseText = "Server Error");
    }
  }

  void _finalizeBill() async {
    final billProvider = Provider.of<BillProvider>(context, listen: false);
    
    // DEBUG: Check if bill has items
    if (!billProvider.hasBillItems) {
      debugPrint("❌ VOICE BILL: Bill is empty - cannot print");
      return;
    }

    debugPrint("✅ VOICE BILL: Has ${billProvider.currentBillItems.length} items");
    debugPrint("👤 Customer: ${billProvider.customerName}");
    
    // DEBUG: Print each item structure
    for (var item in billProvider.currentBillItems) {
      debugPrint("VOICE ITEM: $item");
    }

    if (!widget.isPrinterConnected) {
      _flutterTts.speak("Printer connected nahi hai"); // Speak warning
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text("⚠️ Connect Printer First!"),
          backgroundColor: Colors.red,
          duration: Duration(seconds: 2),
        ),
      );
      widget.togglePrinter();
      return;
    }

    // Speak confirmation
    _flutterTts.speak("Bill print ho raha hai");

    // Get next bill number
    final billNumber = await billProvider.getNextBillNumber();

    // CRITICAL: Create a COPY of items before clearing
    final itemsCopy = List<Map<String, dynamic>>.from(billProvider.currentBillItems);

    final billData = {
      'id': billNumber,
      'date':
          "${DateTime.now().day}-${DateTime.now().month}-${DateTime.now().year}",
      'time': "${DateTime.now().hour}:${DateTime.now().minute}",
      'total': billProvider.billTotal,
      'customerName': billProvider.customerName, // Add customer name
      'shopName': widget.shopDetails.shopName,
      'shopAddress': widget.shopDetails.address,
      'shopPhone': widget.shopDetails.phone1,
      'items': itemsCopy,  // Use the copy, not the reference
    };

    debugPrint("✅ VOICE BILL DATA: $billData");
    final itemsList = billData['items'] as List;
    debugPrint("✅ VOICE BILL ITEMS COUNT: ${itemsList.length}");

    widget.onBillFinalized(billData);

    // Clear bill after printing
    billProvider.clearBill();
    setState(() {
      _aiResponseText = "Bill Printed!";
    });
  }

  void _openShareModal(BillProvider billProvider) {
    if (!billProvider.hasBillItems) return;

    // Get current bill items
    final billItems = List<Map<String, dynamic>>.from(billProvider.currentBillItems);
    final totalAmount = billProvider.billTotal;

    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => BillShareModal(
          billItems: billItems,
          totalAmount: totalAmount,
          shopDetails: widget.shopDetails,
          customerName: billProvider.customerName,
        ),
        fullscreenDialog: true,
      ),
    );
  }

  // Helper: Format number without .0 for whole numbers
  String _formatNumber(double value) {
    if (value == value.toInt()) {
      return value.toInt().toString();
    }
    return value.toString();
  }
  
  // Helper: Extract numeric quantity from qtyDisplay (e.g., "2kg" -> "2")
  String _extractQuantityNumber(String qtyDisplay) {
    final numericPart = qtyDisplay.replaceAll(RegExp(r'[^0-9.]'), '');
    return numericPart.isEmpty ? '1' : numericPart;
  }
  
  // Helper: Extract unit from qtyDisplay (e.g., "2kg" -> "kg")
  String _extractUnit(String qtyDisplay) {
    final unitPart = qtyDisplay.replaceAll(RegExp(r'[0-9.]'), '').trim();
    return unitPart.isEmpty ? 'kg' : unitPart;
  }
  
  // Helper: Format rate with unit (e.g., rate=30, qtyDisplay="2plt" -> "₹30/plt")
  String _formatRateWithUnit(double rate, String qtyDisplay) {
    final unit = _extractUnit(qtyDisplay);
    return '₹${_formatNumber(rate)}/$unit';
  }

  // Helper: Format quantity display with smart kg/gm conversion
  String _formatQuantityDisplay(String qtyDisplay) {
    // First apply short unit names
    String result = qtyDisplay;
    result = result.replaceAll('dozen', 'doz');
    result = result.replaceAll('plate', 'plt');
    result = result.replaceAll('pieces', 'pic');
    result = result.replaceAll('pics', 'pic');
    result = result.replaceAll('litre', 'lit');
    result = result.replaceAll('liter', 'lit');
    
    // Smart kg/gm conversion
    // Extract number and unit from string like "0.4kg" or "1.2 kg"
    final RegExp kgPattern = RegExp(r'(\d+\.?\d*)\s*kg', caseSensitive: false);
    final match = kgPattern.firstMatch(result);
    
    if (match != null) {
      double kgValue = double.tryParse(match.group(1) ?? '0') ?? 0;
      
      // If < 1kg, convert to grams
      if (kgValue > 0 && kgValue < 1) {
        int grams = (kgValue * 1000).round();
        result = result.replaceFirst(kgPattern, '${grams}gm');
      }
      // If > 1kg but has decimal, convert fully to grams
      else if (kgValue > 1 && kgValue != kgValue.toInt()) {
        int grams = (kgValue * 1000).round();
        result = result.replaceFirst(kgPattern, '${grams}gm');
      }
      // If whole kg, keep as is
    }
    
    // Convert large grams to kg (e.g., 2000gm -> 2kg)
    final RegExp gmPattern = RegExp(r'(\d+)\s*gm', caseSensitive: false);
    final gmMatch = gmPattern.firstMatch(result);
    
    if (gmMatch != null) {
      int gmValue = int.tryParse(gmMatch.group(1) ?? '0') ?? 0;
      if (gmValue >= 1000 && gmValue % 1000 == 0) {
        int kgValue = gmValue ~/ 1000;
        result = result.replaceFirst(gmPattern, '${kgValue}kg');
      }
    }
    
    return result;
  }

  void _toggleEditMode() {
    setState(() {
      _isEditMode = !_isEditMode;
    });
    if (!_isEditMode) {
      // Close keyboard when exiting edit mode
      FocusScope.of(context).unfocus();
    }
  }

  void _addManualItem(BillProvider billProvider) {
    // Add empty item and enter edit mode
    final newItem = {
      'name': 'New Item',
      'en': 'New Item',
      'hi': 'New Item',
      'qty': '1',
      'qty_display': '1kg',
      'rate': 0.0,
      'total': 0.0,
      'unit': 'kg',
    };
    
    billProvider.addBillItem(newItem);
    
    if (!_isEditMode) {
      setState(() {
        _isEditMode = true;
      });
    }
  }

  void _updateBillItem(int index, String field, String value, BillProvider billProvider) {
    final items = List<Map<String, dynamic>>.from(billProvider.currentBillItems);
    final item = Map<String, dynamic>.from(items[index]);
    
    if (field == 'name') {
      item['name'] = value;
      item['en'] = value;
      item['hi'] = value;
    } else if (field == 'qty_display') {
      item['qty_display'] = value;
      // Extract numeric part for qty field
      final numericQty = value.replaceAll(RegExp(r'[^0-9.]'), '');
      item['qty'] = numericQty;
      // Recalculate total
      final rate = (item['rate'] as num).toDouble();
      final qty = double.tryParse(numericQty) ?? 1.0;
      item['total'] = rate * qty;
    } else if (field == 'rate') {
      final rate = double.tryParse(value) ?? 0.0;
      item['rate'] = rate;
      // Recalculate total
      final qtyStr = item['qty_display'].toString().replaceAll(RegExp(r'[^0-9.]'), '');
      final qty = double.tryParse(qtyStr) ?? 1.0;
      item['total'] = rate * qty;
    }
    
    items[index] = item;
    billProvider.updateBillItems(items);
  }
  
  // Computed total - always derived from items
  double _computeTotal(List<Map<String, dynamic>> items) {
    return items.fold<double>(
      0,
      (sum, item) => sum + ((item['total'] as num?)?.toDouble() ?? 0),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<BillProvider>(
      builder: (context, billProvider, child) {
        final currentBill = billProvider.currentBillItems;
        final grandTotal = _computeTotal(currentBill);
        
        return Scaffold(
      resizeToAvoidBottomInset: true,
      body: SafeArea(
        child: Column(
          children: [
            // 1. Header - Fixed overflow
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              child: Row(
                  children: [
                    const SizedBox(width: 48),
                    Expanded(
                      child: Text(widget.shopDetails.shopName,
                          textAlign: TextAlign.center,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: const TextStyle(
                              fontSize: 20, fontWeight: FontWeight.bold)),
                    ),
                    IconButton(
                        icon: Icon(Icons.print,
                            color: widget.isPrinterConnected
                                ? AppColors.printerConnected
                                : AppColors.printerDisconnected),
                        onPressed: widget.togglePrinter),
                  ]),
            ),

            // 2. Voice Circle - Simple green pulsing with better feedback
            if (!_isEditMode)
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 20),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    // Green Pulsing Circle with ripple effect
                    Stack(
                      alignment: Alignment.center,
                      children: [
                        // Outer ripple when listening
                        if (_isListening)
                          AnimatedContainer(
                            duration: const Duration(milliseconds: 1000),
                            height: 160,
                            width: 160,
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              border: Border.all(
                                color: AppColors.primaryGreen.withOpacity(0.3),
                                width: 2,
                              ),
                            ),
                          ),
                        
                        // Main circle
                        AnimatedScale(
                          scale: _isListening ? 1.0 + (_audioLevel * 0.15) : 1.0,
                          duration: const Duration(milliseconds: 100),
                          child: GestureDetector(
                            onTap: _toggleListening,
                            child: Container(
                              height: 120,
                              width: 120,
                              decoration: BoxDecoration(
                                color: _isListening ? AppColors.primaryGreen : Colors.white,
                                shape: BoxShape.circle,
                                border: Border.all(
                                  color: _isListening ? Colors.transparent : Colors.grey.shade300,
                                  width: 2,
                                ),
                                boxShadow: [
                                  if (_isListening)
                                    BoxShadow(
                                      color: AppColors.primaryGreen.withOpacity(0.6),
                                      blurRadius: 40,
                                      spreadRadius: 10,
                                    )
                                  else
                                    const BoxShadow(
                                      color: Colors.black12,
                                      blurRadius: 10,
                                      spreadRadius: 2,
                                    ),
                                ],
                              ),
                              child: Icon(
                                _isListening ? Icons.graphic_eq : Icons.mic,
                                size: 50,
                                color: _isListening ? Colors.white : Colors.black,
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                    
                    const SizedBox(height: 15),
                    
                    // Status indicator
                    if (_isListening)
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                        decoration: BoxDecoration(
                          color: AppColors.primaryGreen.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Container(
                              width: 8,
                              height: 8,
                              decoration: const BoxDecoration(
                                color: AppColors.primaryGreen,
                                shape: BoxShape.circle,
                              ),
                            ),
                            const SizedBox(width: 6),
                            const Text(
                              'Listening...',
                              style: TextStyle(
                                color: AppColors.primaryGreen,
                                fontWeight: FontWeight.bold,
                                fontSize: 12,
                              ),
                            ),
                          ],
                        ),
                      ),
                    
                    const SizedBox(height: 10),
                    
                    // Speech Text - SINGLE LINE with fixed height
                    SizedBox(
                      height: 20,
                      child: Text(
                        _getDisplayText(),
                        textAlign: TextAlign.center,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                          fontSize: 14,
                          color: Colors.grey,
                        ),
                      ),
                    ),
                    
                    const SizedBox(height: 8),

                    // Response Text - SINGLE LINE with fixed height
                    SizedBox(
                      height: 24,
                      child: Text(
                        _aiResponseText,
                        textAlign: TextAlign.center,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ),
              ),

            // 3. Live Bill Container (Takes remaining space)
            Expanded(
              child: Container(
                margin: const EdgeInsets.fromLTRB(16, 20, 16, 16),
                decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(25),
                    boxShadow: [
                      const BoxShadow(
                          color: Colors.black12,
                          blurRadius: 20,
                          offset: Offset(0, -5))
                    ]),
                child: Column(
                  children: [
                    // Bill Header - Flexible to prevent overflow
                    Padding(
                        padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
                        child: Row(
                            children: [
                              const Text("Live Bill",
                                  style: TextStyle(
                                      fontWeight: FontWeight.bold,
                                      fontSize: 16)),
                              const Spacer(),
                              Flexible(
                                child: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    Flexible(
                                      child: TextButton.icon(
                                          onPressed: _resetVoicePage,
                                          icon: const Icon(Icons.refresh,
                                              size: 16, color: Colors.red),
                                          label: const Text("Cancel",
                                              overflow: TextOverflow.ellipsis,
                                              style: TextStyle(
                                                  color: Colors.red,
                                                  fontSize: 12,
                                                  fontWeight: FontWeight.bold)),
                                          style: TextButton.styleFrom(
                                            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 4),
                                            minimumSize: Size.zero,
                                            tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                                          )),
                                    ),
                                    const SizedBox(width: 4),
                                    IconButton(
                                      onPressed: () {
                                        if (currentBill.isEmpty) {
                                          _addManualItem(billProvider);
                                        } else {
                                          _toggleEditMode();
                                        }
                                      },
                                      icon: Icon(
                                        currentBill.isEmpty 
                                          ? Icons.add 
                                          : (_isEditMode ? Icons.close : Icons.edit),
                                        size: 18,
                                        color: AppColors.primaryGreen,
                                      ),
                                      style: IconButton.styleFrom(
                                        backgroundColor: AppColors.primaryGreen.withOpacity(0.1),
                                        padding: const EdgeInsets.all(6),
                                        minimumSize: Size.zero,
                                        tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ])),

                    // Column Headers
                    const Padding(
                        padding:
                            EdgeInsets.symmetric(horizontal: 20, vertical: 5),
                        child: Row(children: [
                          Expanded(
                              flex: 4,
                              child: Text("Item",
                                  style: TextStyle(
                                      fontWeight: FontWeight.bold,
                                      fontSize: 12,
                                      color: Colors.grey))),
                          Expanded(
                              flex: 1,
                              child: Text("Qty",
                                  textAlign: TextAlign.center,
                                  style: TextStyle(
                                      fontWeight: FontWeight.bold,
                                      fontSize: 12,
                                      color: Colors.grey))),
                          Expanded(
                              flex: 3,
                              child: Text("Rate",
                                  textAlign: TextAlign.right,
                                  style: TextStyle(
                                      fontWeight: FontWeight.bold,
                                      fontSize: 12,
                                      color: Colors.grey))),
                          Expanded(
                              flex: 2,
                              child: Text("Total",
                                  textAlign: TextAlign.right,
                                  style: TextStyle(
                                      fontWeight: FontWeight.bold,
                                      fontSize: 12,
                                      color: Colors.grey))),
                        ])),
                    const Divider(height: 1),

                    // List Items
                    Expanded(
                        child: currentBill.isEmpty
                            ? const Center(
                                child: Text("Tap + to add items manually\nor say 'Chawal 1kg'",
                                    textAlign: TextAlign.center,
                                    style: TextStyle(color: Colors.grey)))
                            : ListView.separated(
                                padding: const EdgeInsets.symmetric(
                                    horizontal: 20, vertical: 10),
                                itemCount: currentBill.length + (_isEditMode ? 1 : 0),
                                separatorBuilder: (_, __) =>
                                    const Divider(height: 16),
                                itemBuilder: (context, index) {
                                  // Add Item Button at the end in Edit Mode
                                  if (_isEditMode && index == currentBill.length) {
                                    return GestureDetector(
                                      onTap: () => _addManualItem(billProvider),
                                      child: Container(
                                        padding: const EdgeInsets.symmetric(vertical: 12),
                                        decoration: BoxDecoration(
                                          color: AppColors.primaryGreen.withOpacity(0.1),
                                          borderRadius: BorderRadius.circular(8),
                                          border: Border.all(
                                            color: AppColors.primaryGreen.withOpacity(0.3),
                                            style: BorderStyle.solid,
                                          ),
                                        ),
                                        child: const Row(
                                          mainAxisAlignment: MainAxisAlignment.center,
                                          children: [
                                            Icon(Icons.add, color: AppColors.primaryGreen, size: 20),
                                            SizedBox(width: 8),
                                            Text(
                                              "Add Item",
                                              style: TextStyle(
                                                color: AppColors.primaryGreen,
                                                fontWeight: FontWeight.bold,
                                                fontSize: 14,
                                              ),
                                            ),
                                          ],
                                        ),
                                      ),
                                    );
                                  }
                                  
                                  final item = currentBill[index];
                                  
                                  if (_isEditMode) {
                                    // Editable Mode
                                    return Row(children: [
                                      GestureDetector(
                                          onTap: () => billProvider.removeBillItem(index),
                                          child: Container(
                                              margin:
                                                  const EdgeInsets.only(right: 8),
                                              padding: const EdgeInsets.all(2),
                                              decoration: BoxDecoration(
                                                  color: Colors.red[50],
                                                  shape: BoxShape.circle),
                                              child: const Icon(Icons.remove,
                                                  size: 16, color: Colors.red))),
                                      Expanded(
                                          flex: 4,
                                          child: TextField(
                                            controller: TextEditingController(text: item['name'])
                                              ..selection = TextSelection.collapsed(offset: item['name'].length),
                                            style: const TextStyle(
                                                fontWeight: FontWeight.w600,
                                                fontSize: 14),
                                            decoration: const InputDecoration(
                                              isDense: true,
                                              contentPadding: EdgeInsets.symmetric(vertical: 8, horizontal: 4),
                                              border: OutlineInputBorder(),
                                            ),
                                            onChanged: (value) => _updateBillItem(index, 'name', value, billProvider),
                                          )),
                                      const SizedBox(width: 4),
                                      Expanded(
                                          flex: 1,
                                          child: TextFormField(
                                            initialValue: _extractQuantityNumber(item['qty_display']),
                                            textAlign: TextAlign.center,
                                            keyboardType: TextInputType.number,
                                            style: const TextStyle(fontSize: 13),
                                            decoration: const InputDecoration(
                                              isDense: true,
                                              contentPadding: EdgeInsets.symmetric(vertical: 8, horizontal: 2),
                                              border: OutlineInputBorder(),
                                            ),
                                            onChanged: (value) {
                                              // Update quantity keeping the unit
                                              final unit = _extractUnit(item['qty_display']);
                                              final newQtyDisplay = '$value$unit';
                                              _updateBillItem(index, 'qty_display', newQtyDisplay, billProvider);
                                            },
                                          )),
                                      const SizedBox(width: 4),
                                      Expanded(
                                          flex: 3,
                                          child: TextFormField(
                                            initialValue: _formatNumber((item['rate'] as num).toDouble()),
                                            textAlign: TextAlign.right,
                                            keyboardType: TextInputType.number,
                                            style: const TextStyle(fontSize: 11),
                                            decoration: InputDecoration(
                                              isDense: true,
                                              contentPadding: const EdgeInsets.symmetric(vertical: 8, horizontal: 4),
                                              border: const OutlineInputBorder(),
                                              prefixText: '₹',
                                              suffixText: '/${_extractUnit(item['qty_display'])}',
                                            ),
                                            onChanged: (value) => _updateBillItem(index, 'rate', value, billProvider),
                                          )),
                                      const SizedBox(width: 4),
                                      Expanded(
                                          flex: 2,
                                          child: Text("₹${_formatNumber((item['total'] as num).toDouble())}",
                                              textAlign: TextAlign.right,
                                              style: const TextStyle(
                                                  fontWeight: FontWeight.bold,
                                                  fontSize: 14))),
                                    ]);
                                  } else {
                                    // Display Mode
                                    return Padding(
                                      padding: const EdgeInsets.only(bottom: 12),
                                      child: Row(children: [
                                        GestureDetector(
                                            onTap: () => billProvider.removeBillItem(index),
                                            child: Container(
                                                margin:
                                                    const EdgeInsets.only(right: 8),
                                                padding: const EdgeInsets.all(2),
                                                decoration: BoxDecoration(
                                                    color: Colors.red[50],
                                                    shape: BoxShape.circle),
                                                child: const Icon(Icons.remove,
                                                    size: 16, color: Colors.red))),
                                        Expanded(
                                            flex: 4,
                                            child: Text(item['name'],
                                                style: const TextStyle(
                                                    fontWeight: FontWeight.w600,
                                                    fontSize: 14))),
                                        Expanded(
                                            flex: 1,
                                            child: Text(_formatQuantityDisplay(item['qty_display'] ?? '1kg'),
                                                textAlign: TextAlign.center,
                                                style:
                                                    const TextStyle(fontSize: 13))),
                                        Expanded(
                                            flex: 3,
                                            child: Text(_formatRateWithUnit((item['rate'] as num).toDouble(), item['qty_display'] ?? '1kg'),
                                                textAlign: TextAlign.right,
                                                style:
                                                    const TextStyle(fontSize: 11))),
                                        Expanded(
                                            flex: 2,
                                            child: Text("₹${_formatNumber((item['total'] as num).toDouble())}",
                                                textAlign: TextAlign.right,
                                                style: const TextStyle(
                                                    fontWeight: FontWeight.bold,
                                                    fontSize: 14))),
                                      ]),
                                    );
                                  }
                                })),

                    // Footer Total - Fixed overflow with tighter spacing
                    Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 14),
                        decoration: BoxDecoration(
                            color: Colors.grey[50],
                            borderRadius: const BorderRadius.vertical(
                                bottom: Radius.circular(25))),
                        child: Row(
                            children: [
                              // Print Button - Smaller fixed width
                              SizedBox(
                                width: 110,
                                height: 44,
                                child: ElevatedButton.icon(
                                    onPressed: _finalizeBill,
                                    icon: const Icon(Icons.print,
                                        color: Colors.white, size: 16),
                                    label: const Text("PRINT",
                                        style: TextStyle(
                                            color: Colors.white,
                                            fontSize: 12,
                                            fontWeight: FontWeight.bold)),
                                    style: ElevatedButton.styleFrom(
                                        backgroundColor: Colors.black,
                                        padding: const EdgeInsets.symmetric(horizontal: 8))),
                              ),
                              
                              const SizedBox(width: 6),
                              
                              // Share Icon - Smaller
                              Transform.rotate(
                                angle: -0.5,
                                child: IconButton(
                                  onPressed: currentBill.isEmpty ? null : () => _openShareModal(billProvider),
                                  icon: Icon(
                                    Icons.send,
                                    color: currentBill.isEmpty ? Colors.grey : AppColors.primaryGreen,
                                    size: 22,
                                  ),
                                  style: IconButton.styleFrom(
                                    backgroundColor: currentBill.isEmpty 
                                        ? Colors.grey[200] 
                                        : AppColors.primaryGreen.withOpacity(0.1),
                                    padding: const EdgeInsets.all(8),
                                  ),
                                ),
                              ),
                              
                              const SizedBox(width: 4),
                              
                              // Total - Flexible with constraints
                              Expanded(
                                child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.end,
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      const Text("TOTAL",
                                          style: TextStyle(
                                              fontSize: 10,
                                              color: Colors.grey,
                                              fontWeight: FontWeight.w600)),
                                      FittedBox(
                                        fit: BoxFit.scaleDown,
                                        child: Text(
                                            "₹${_formatNumber(billProvider.billTotal)}",
                                            style: const TextStyle(
                                                fontSize: 22,
                                                fontWeight: FontWeight.bold,
                                                color: AppColors.textBlack)),
                                      ),
                                    ]),
                              ),
                            ])),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
      },
    );
  }
}
