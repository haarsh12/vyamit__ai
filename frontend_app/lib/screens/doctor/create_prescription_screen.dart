import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;

import '../../core/theme.dart';
import '../../models/prescription_line.dart';
import '../../models/shop_details.dart';
import '../../providers/auth_provider.dart';
import '../../providers/doctor_prefs_provider.dart';
import '../../services/prescription_service.dart';
import '../../widgets/siri_wave_orb.dart';

/// Doctor Mode — Page 1: voice-first prescription with editable table.
class CreatePrescriptionScreen extends StatefulWidget {
  final String? doctorName;
  final String? specialization;
  final String? clinicName;

  const CreatePrescriptionScreen({
    super.key,
    this.doctorName,
    this.specialization,
    this.clinicName,
  });

  @override
  State<CreatePrescriptionScreen> createState() =>
      _CreatePrescriptionScreenState();
}

class _CreatePrescriptionScreenState extends State<CreatePrescriptionScreen> {
  static const platform = MethodChannel('com.snapbill/audio');

  final stt.SpeechToText _speech = stt.SpeechToText();
  final PrescriptionService _prescriptionService = PrescriptionService();

  bool _isListening = false;
  bool _isProcessing = false;
  String _statusText = 'Tap to Start';
  String _accumulatedText = '';
  String _currentChunk = '';
  double _audioLevel = 0.35;
  Timer? _audioLevelTimer;

  String? _voiceError;
  final List<PrescriptionLine> _lines = [];

  @override
  void dispose() {
    _speech.stop();
    _audioLevelTimer?.cancel();
    super.dispose();
  }

  Future<void> _muteSystemSounds() async {
    try {
      await platform.invokeMethod('muteSystemSounds');
    } catch (_) {}
  }

  Future<void> _unmuteSystemSounds() async {
    try {
      await platform.invokeMethod('unmuteSystemSounds');
    } catch (_) {}
  }

  void _startAudioLevelAnimation() {
    _audioLevelTimer?.cancel();
    _audioLevelTimer = Timer.periodic(const Duration(milliseconds: 120), (t) {
      if (!_isListening) {
        t.cancel();
        return;
      }
      setState(() {
        _audioLevel = _currentChunk.isNotEmpty ? 0.65 : 0.4;
      });
    });
  }

  Future<void> _toggleListening() async {
    if (_isProcessing) return;
    if (_isListening) {
      await _stopListeningAndProcess();
    } else {
      await _startListening();
    }
  }

  Future<void> _startListening() async {
    await _muteSystemSounds();
    _voiceError = null;

    final available = await _speech.initialize(
      onError: (e) {
        if (e.errorMsg.toLowerCase().contains('permission')) {
          setState(() {
            _isListening = false;
            _statusText = 'Microphone permission denied';
          });
          _unmuteSystemSounds();
        }
      },
      onStatus: (_) {},
    );

    if (!available) {
      setState(() => _statusText = 'Speech recognition not available');
      await _unmuteSystemSounds();
      return;
    }

    setState(() {
      _isListening = true;
      _statusText = 'Listening...';
      _accumulatedText = '';
      _currentChunk = '';
      _audioLevel = 0.45;
    });

    _startAudioLevelAnimation();

    try {
      await _speech.listen(
        onResult: (result) {
          if (!_isListening || !mounted) return;
          setState(() {
            _currentChunk = result.recognizedWords;
            if (result.finalResult && result.recognizedWords.isNotEmpty) {
              if (_accumulatedText.isEmpty) {
                _accumulatedText = result.recognizedWords;
              } else {
                _accumulatedText = '${_accumulatedText} ${result.recognizedWords}';
              }
              _currentChunk = '';
            }
          });
        },
        listenMode: stt.ListenMode.dictation,
        partialResults: true,
        localeId: 'en_IN',
        cancelOnError: false,
        listenFor: const Duration(minutes: 5),
        pauseFor: const Duration(seconds: 4),
      );
    } catch (e) {
      setState(() {
        _isListening = false;
        _statusText = 'Tap to Start';
      });
      await _unmuteSystemSounds();
    }
  }

  Future<void> _stopListeningAndProcess() async {
    await _speech.stop();
    _audioLevelTimer?.cancel();
    await _unmuteSystemSounds();

    final spoken = ('$_accumulatedText $_currentChunk').trim();

    setState(() {
      _isListening = false;
      _accumulatedText = '';
      _currentChunk = '';
      _audioLevel = 0.35;
    });

    if (spoken.isEmpty) {
      setState(() {
        _statusText = 'Tap to Start';
        _voiceError = 'No speech detected. Try again or add medicines manually.';
      });
      return;
    }

    setState(() {
      _isProcessing = true;
      _statusText = 'Processing...';
      _voiceError = null;
    });

    try {
      final parsed = await _prescriptionService.parseFromVoiceText(spoken);
      if (!mounted) return;
      if (parsed.isEmpty) {
        setState(() {
          _isProcessing = false;
          _statusText = 'Tap to Start';
          _voiceError =
              'Could not understand medicines. Edit the table or try again.';
        });
        return;
      }
      setState(() {
        _lines.clear();
        _lines.addAll(parsed);
        _isProcessing = false;
        _statusText = 'Tap to Start';
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _isProcessing = false;
        _statusText = 'Tap to Start';
        _voiceError = 'Could not process speech. Try again.';
      });
    }
  }

  void _addRow() {
    setState(() {
      _lines.add(PrescriptionLine(
        medicineName: '',
        dosageFrequencyTiming: '',
        days: '1',
      ));
    });
  }

  void _removeRow(int index) {
    setState(() {
      _lines.removeAt(index);
    });
  }

  Future<void> _save() async {
    final err = _validate();
    if (err != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(err), backgroundColor: Colors.red[700]),
      );
      return;
    }

    setState(() => _isProcessing = true);
    try {
      await _prescriptionService.savePrescription(lines: _lines);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Prescription saved'),
          backgroundColor: AppColors.primaryGreen,
        ),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            'Save failed (add POST /doctor/prescriptions on server): $e',
          ),
          backgroundColor: Colors.orange[800],
          duration: const Duration(seconds: 4),
        ),
      );
    } finally {
      if (mounted) setState(() => _isProcessing = false);
    }
  }

  String? _validate() {
    if (_lines.isEmpty) {
      return 'Add at least one medicine.';
    }
    for (final line in _lines) {
      if (line.medicineName.trim().isEmpty) {
        return 'Each row needs a medicine name.';
      }
      final d = int.tryParse(line.days.trim());
      if (d == null || d < 1) {
        return 'Enter a valid number of days for "${line.medicineName}".';
      }
    }
    return null;
  }

  @override
  Widget build(BuildContext context) {
    final bottomInset = MediaQuery.of(context).viewInsets.bottom;

    // Resolve names: use passed params or fallback to providers
    final shop = Provider.of<AuthProvider>(context).shopDetails;
    final docPrefs = Provider.of<DoctorPrefsProvider>(context);

    final finalDoctorName = widget.doctorName ?? shop?.ownerName ?? 'Doctor';
    final finalClinicName = widget.clinicName ?? shop?.shopName ?? 'Clinic';

    String finalSpec = widget.specialization ?? docPrefs.specialization;
    if (finalSpec.trim().isEmpty) finalSpec = 'Specialization not set';

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(finalDoctorName, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            Text(finalSpec, style: const TextStyle(fontSize: 13, color: AppColors.textGrey, fontWeight: FontWeight.normal)),
          ],
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: EdgeInsets.fromLTRB(16, 12, 16, 16 + bottomInset),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Text(
                'Create Prescription',
                style: TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                  color: AppColors.textBlack,
                ),
              ),
              const SizedBox(height: 20),
            Center(
              child: Column(
                children: [
                  IgnorePointer(
                    ignoring: _isProcessing,
                    child: Opacity(
                      opacity: _isProcessing ? 0.5 : 1,
                      child: SiriWaveOrb(
                        isActive: _isListening,
                        audioLevel: _audioLevel,
                        onTap: _toggleListening,
                        size: 168,
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),
                  if (_isProcessing)
                    const Padding(
                      padding: EdgeInsets.only(top: 8),
                      child: SizedBox(
                        width: 28,
                        height: 28,
                        child: CircularProgressIndicator(
                          strokeWidth: 2.5,
                          color: AppColors.primaryGreen,
                        ),
                      ),
                    )
                  else
                    Text(
                      _statusText,
                      style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w600,
                        color: _isListening
                            ? AppColors.primaryGreen
                            : AppColors.textGrey,
                      ),
                    ),
                ],
              ),
            ),
            if (_voiceError != null) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.orange.shade50,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.orange.shade200),
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(Icons.info_outline, color: Colors.orange[800]),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        _voiceError!,
                        style: const TextStyle(
                          fontSize: 13,
                          color: AppColors.textBlack,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
            const SizedBox(height: 24),
            Text(
              'Medicines',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: AppColors.textBlack,
                  ),
            ),
            const SizedBox(height: 8),
            if (_lines.isEmpty)
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 24),
                child: Text(
                  'Use the voice button above or tap "Add Medicine".',
                  textAlign: TextAlign.center,
                  style: TextStyle(color: Colors.grey[600], fontSize: 14),
                ),
              )
            else
              ...List.generate(_lines.length, (index) {
                final line = _lines[index];
                return _PrescriptionRowCard(
                  key: ValueKey(line.id),
                  line: line,
                  onChanged: () => setState(() {}),
                  onDelete: () => _removeRow(index),
                );
              }),
            const SizedBox(height: 12),
            OutlinedButton.icon(
              onPressed: _isProcessing ? null : _addRow,
              icon: const Icon(Icons.add_circle_outline),
              label: const Text('Add Medicine'),
              style: OutlinedButton.styleFrom(
                foregroundColor: AppColors.primaryGreen,
                side: const BorderSide(color: AppColors.primaryGreen),
                padding: const EdgeInsets.symmetric(vertical: 14),
              ),
            ),
            const SizedBox(height: 16),
            SizedBox(
              height: 52,
              child: ElevatedButton(
                onPressed: _isProcessing ? null : _save,
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.primaryGreen,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: const Text(
                  'Save Prescription',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                ),
              ),
            ),
          ],
        ),
      ),
      ),
    );
  }
}

class _PrescriptionRowCard extends StatefulWidget {
  final PrescriptionLine line;
  final VoidCallback onChanged;
  final VoidCallback onDelete;

  const _PrescriptionRowCard({
    super.key,
    required this.line,
    required this.onChanged,
    required this.onDelete,
  });

  @override
  State<_PrescriptionRowCard> createState() => _PrescriptionRowCardState();
}

class _PrescriptionRowCardState extends State<_PrescriptionRowCard> {
  late TextEditingController _name;
  late TextEditingController _dose;
  late TextEditingController _days;

  @override
  void initState() {
    super.initState();
    _bindControllers();
  }

  void _bindControllers() {
    _name = TextEditingController(text: widget.line.medicineName);
    _dose = TextEditingController(text: widget.line.dosageFrequencyTiming);
    _days = TextEditingController(text: widget.line.days);
  }

  @override
  void didUpdateWidget(covariant _PrescriptionRowCard oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.line.id != widget.line.id) {
      _name.dispose();
      _dose.dispose();
      _days.dispose();
      _bindControllers();
    }
  }

  @override
  void dispose() {
    _name.dispose();
    _dose.dispose();
    _days.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final line = widget.line;
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    'Medicine',
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w600,
                      color: Colors.grey[700],
                    ),
                  ),
                ),
                IconButton(
                  onPressed: widget.onDelete,
                  icon:
                      const Icon(Icons.delete_outline, color: Colors.redAccent),
                  tooltip: 'Remove row',
                ),
              ],
            ),
            TextField(
              controller: _name,
              onChanged: (v) {
                line.medicineName = v;
                widget.onChanged();
              },
              decoration: const InputDecoration(
                hintText: 'e.g. Paracetamol 500 mg',
                isDense: true,
              ),
            ),
            const SizedBox(height: 10),
            Text(
              'Dosage · frequency · timing',
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w600,
                color: Colors.grey[700],
              ),
            ),
            TextField(
              controller: _dose,
              onChanged: (v) {
                line.dosageFrequencyTiming = v;
                widget.onChanged();
              },
              maxLines: 2,
              decoration: const InputDecoration(
                hintText: 'e.g. 2 times daily — after food',
                isDense: true,
              ),
            ),
            const SizedBox(height: 10),
            Text(
              'Days',
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w600,
                color: Colors.grey[700],
              ),
            ),
            TextField(
              controller: _days,
              keyboardType: TextInputType.number,
              onChanged: (v) {
                line.days = v;
                widget.onChanged();
              },
              decoration: const InputDecoration(
                hintText: '5',
                isDense: true,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
