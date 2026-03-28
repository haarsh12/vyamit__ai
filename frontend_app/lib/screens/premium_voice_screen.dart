import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/premium_voice_service.dart';
import '../widgets/premium_voice_orb.dart';
import '../providers/inventory_provider.dart';
import '../core/theme.dart';

/// Premium Voice Screen - GPT-style voice interface
/// Features:
/// - Continuous listening (no interruptions)
/// - Smart silence detection (40s timeout)
/// - Auto-deactivate on queries
/// - Silent operation (no audio feedback)
/// - Smooth animations
class PremiumVoiceScreen extends StatefulWidget {
  const PremiumVoiceScreen({super.key});

  @override
  State<PremiumVoiceScreen> createState() => _PremiumVoiceScreenState();
}

class _PremiumVoiceScreenState extends State<PremiumVoiceScreen> {
  late PremiumVoiceService _voiceService;
  final List<BillItem> _billItems = [];
  String _lastResponse = '';

  @override
  void initState() {
    super.initState();
    _initializeVoiceService();
  }

  Future<void> _initializeVoiceService() async {
    _voiceService = PremiumVoiceService();
    await _voiceService.initialize();
    
    // Set callbacks
    _voiceService.onBillUpdate = _handleBillUpdate;
    _voiceService.onResponse = _handleResponse;
    
    // Set user context
    final inventoryProvider = Provider.of<InventoryProvider>(context, listen: false);
    final inventory = inventoryProvider.items.map((item) => {
      'id': item.id,
      'names': item.names,
      'price': item.price,
      'unit': item.unit,
      'category': item.category,
    }).toList();
    
    _voiceService.setContext(
      inventory: inventory,
      userId: 1, // TODO: Get from auth
    );
    
    _voiceService.addListener(_onVoiceServiceUpdate);
  }

  void _onVoiceServiceUpdate() {
    if (mounted) {
      setState(() {});
    }
  }

  void _handleBillUpdate(List<dynamic> updates) {
    setState(() {
      for (var update in updates) {
        _billItems.add(BillItem(
          name: update['name'] ?? '',
          quantity: update['quantity'] ?? 1.0,
          unit: update['unit'] ?? '',
          price: update['price'] ?? 0.0,
          total: update['total'] ?? 0.0,
        ));
      }
    });
    
    _showSnackBar('${updates.length} item(s) added to bill');
  }

  void _handleResponse(String response) {
    setState(() {
      _lastResponse = response;
    });
  }

  void _showSnackBar(String message) {
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(message),
          behavior: SnackBarBehavior.floating,
          duration: const Duration(seconds: 2),
        ),
      );
    }
  }

  void _toggleVoice() {
    if (_voiceService.isActive) {
      _voiceService.stopListening();
    } else {
      _voiceService.startListening();
    }
  }

  void _clearBill() {
    setState(() {
      _billItems.clear();
      _lastResponse = '';
    });
  }

  double get _totalAmount {
    return _billItems.fold(0.0, (sum, item) => sum + item.total);
  }

  @override
  void dispose() {
    _voiceService.removeListener(_onVoiceServiceUpdate);
    _voiceService.stopListening();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: const Text('Voice Billing'),
        backgroundColor: AppColors.primaryGreen,
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          if (_billItems.isNotEmpty)
            IconButton(
              icon: const Icon(Icons.delete_outline),
              onPressed: _clearBill,
              tooltip: 'Clear bill',
            ),
        ],
      ),
      body: Column(
        children: [
          // Voice Orb Section
          Expanded(
            flex: 2,
            child: Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    AppColors.primaryGreen.withOpacity(0.05),
                    Colors.white,
                  ],
                ),
              ),
              child: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    // Premium Voice Orb
                    PremiumVoiceOrb(
                      isActive: _voiceService.isActive,
                      isProcessing: _voiceService.isProcessing,
                      audioLevel: _voiceService.audioLevel,
                      onTap: _toggleVoice,
                      size: 140,
                    ),
                    
                    const SizedBox(height: 24),
                    
                    // Status Text
                    AnimatedSwitcher(
                      duration: const Duration(milliseconds: 300),
                      child: Text(
                        _getStatusText(),
                        key: ValueKey(_getStatusText()),
                        style: TextStyle(
                          fontSize: 16,
                          color: Colors.grey[700],
                          fontWeight: FontWeight.w500,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ),
                    
                    const SizedBox(height: 12),
                    
                    // Live Transcript
                    if (_voiceService.isActive && _voiceService.fullTranscript.isNotEmpty)
                      Container(
                        margin: const EdgeInsets.symmetric(horizontal: 32),
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: Colors.grey[100],
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Text(
                          _voiceService.fullTranscript,
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.grey[800],
                          ),
                          textAlign: TextAlign.center,
                          maxLines: 3,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    
                    // Last Response
                    if (_lastResponse.isNotEmpty && !_voiceService.isActive)
                      Container(
                        margin: const EdgeInsets.symmetric(horizontal: 32),
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: AppColors.primaryGreen.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                            color: AppColors.primaryGreen.withOpacity(0.3),
                          ),
                        ),
                        child: Row(
                          children: [
                            Icon(
                              Icons.chat_bubble_outline,
                              color: AppColors.primaryGreen,
                              size: 20,
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Text(
                                _lastResponse,
                                style: TextStyle(
                                  fontSize: 14,
                                  color: Colors.grey[800],
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                  ],
                ),
              ),
            ),
          ),
          
          // Bill Items Section
          if (_billItems.isNotEmpty)
            Expanded(
              flex: 3,
              child: Container(
                decoration: BoxDecoration(
                  color: Colors.grey[50],
                  borderRadius: const BorderRadius.only(
                    topLeft: Radius.circular(24),
                    topRight: Radius.circular(24),
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.05),
                      blurRadius: 10,
                      offset: const Offset(0, -5),
                    ),
                  ],
                ),
                child: Column(
                  children: [
                    // Header
                    Padding(
                      padding: const EdgeInsets.all(20),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            'Bill Items',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: Colors.grey[800],
                            ),
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 12,
                              vertical: 6,
                            ),
                            decoration: BoxDecoration(
                              color: AppColors.primaryGreen.withOpacity(0.1),
                              borderRadius: BorderRadius.circular(20),
                            ),
                            child: Text(
                              '${_billItems.length} items',
                              style: const TextStyle(
                                fontSize: 14,
                                color: AppColors.primaryGreen,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                    
                    // Items List
                    Expanded(
                      child: ListView.builder(
                        padding: const EdgeInsets.symmetric(horizontal: 20),
                        itemCount: _billItems.length,
                        itemBuilder: (context, index) {
                          return _buildBillItem(_billItems[index], index);
                        },
                      ),
                    ),
                    
                    // Total
                    Container(
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.05),
                            blurRadius: 10,
                            offset: const Offset(0, -5),
                          ),
                        ],
                      ),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text(
                            'Total Amount',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          Text(
                            '₹${_totalAmount.toStringAsFixed(2)}',
                            style: const TextStyle(
                              fontSize: 24,
                              fontWeight: FontWeight.bold,
                              color: AppColors.primaryGreen,
                            ),
                          ),
                        ],
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

  String _getStatusText() {
    if (_voiceService.isSpeaking) {
      return 'Speaking...';
    } else if (_voiceService.isProcessing) {
      return 'Processing...';
    } else if (_voiceService.isActive) {
      return 'Listening... (Tap to stop)';
    } else {
      return 'Tap to start voice billing';
    }
  }

  Widget _buildBillItem(BillItem item, int index) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 5,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          // Index
          Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              color: AppColors.primaryGreen.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: Center(
              child: Text(
                '${index + 1}',
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  color: AppColors.primaryGreen,
                ),
              ),
            ),
          ),
          
          const SizedBox(width: 12),
          
          // Item Details
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  item.name,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  '${item.quantity} ${item.unit} × ₹${item.price.toStringAsFixed(2)}',
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
          ),
          
          // Total
          Text(
            '₹${item.total.toStringAsFixed(2)}',
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: AppColors.primaryGreen,
            ),
          ),
        ],
      ),
    );
  }
}

// Bill Item Model
class BillItem {
  final String name;
  final double quantity;
  final String unit;
  final double price;
  final double total;

  BillItem({
    required this.name,
    required this.quantity,
    required this.unit,
    required this.price,
    required this.total,
  });
}
