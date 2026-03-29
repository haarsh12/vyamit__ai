import '../models/prescription_line.dart';
import 'api_client.dart';

/// Voice → structured rows, and save to backend when `/doctor/prescriptions` exists.
class PrescriptionService {
  final ApiClient _api = ApiClient();

  /// Prefer backend parsing; falls back to local heuristics.
  Future<List<PrescriptionLine>> parseFromVoiceText(String rawText) async {
    final text = rawText.trim();
    if (text.isEmpty) return [];

    try {
      final data = await _api.post('/doctor/prescriptions/parse-voice', {
        'text': text,
      });
      final items = data['items'] as List<dynamic>?;
      if (items != null && items.isNotEmpty) {
        return items.map((e) {
          final m = e as Map<String, dynamic>;
          return PrescriptionLine(
            medicineName: (m['medicine_name'] ?? m['name'] ?? '').toString(),
            dosageFrequencyTiming:
                (m['dosage_frequency_timing'] ?? m['instructions'] ?? '')
                    .toString(),
            days: (m['days'] ?? m['duration_days'] ?? '1').toString(),
          );
        }).toList();
      }
    } catch (_) {
      // Endpoint not deployed or error — use local parser
    }

    return parsePrescriptionLocally(text);
  }

  /// Saves prescription; throws on HTTP error.
  Future<Map<String, dynamic>> savePrescription({
    required List<PrescriptionLine> lines,
    String? patientNotes,
  }) async {
    return await _api.post('/doctor/prescriptions', {
      'items': lines.map((e) => e.toJson()).toList(),
      if (patientNotes != null && patientNotes.isNotEmpty)
        'notes': patientNotes,
    });
  }

  /// Heuristic parser for common phrases like:
  /// "Paracetamol 500 mg twice daily after food for 5 days"
  static List<PrescriptionLine> parsePrescriptionLocally(String raw) {
    final text = raw.trim();
    if (text.isEmpty) return [];

    final segments = <String>[];
    for (final part in text.split(RegExp(r'\s*(?:;|\.)\s*'))) {
      final p = part.trim();
      if (p.isEmpty) continue;
      final andParts = p.split(RegExp(r'\s+and\s+', caseSensitive: false));
      if (andParts.length > 1) {
        for (final a in andParts) {
          final t = a.trim();
          if (t.isNotEmpty) segments.add(t);
        }
      } else {
        segments.add(p);
      }
    }

    if (segments.isEmpty) return [_parseSingleMedicine(text)];

    return segments.map(_parseSingleMedicine).toList();
  }

  static PrescriptionLine _parseSingleMedicine(String t) {
    var work = t.trim();
    int days = 1;

    var m = RegExp(r'\s+for\s+(\d+)\s*days?', caseSensitive: false)
        .firstMatch(work);
    if (m != null) {
      days = int.tryParse(m.group(1)!) ?? 1;
      work = work.substring(0, m.start).trim();
    } else {
      m = RegExp(r'\s+(\d+)\s*days?\s*$', caseSensitive: false)
          .firstMatch(work);
      if (m != null) {
        days = int.tryParse(m.group(1)!) ?? 1;
        work = work.substring(0, m.start).trim();
      }
    }

    final structured = RegExp(
      r'^(.+?\s+\d+\s*mg)\s+(.+)$',
      caseSensitive: false,
    ).firstMatch(work);

    if (structured != null) {
      return PrescriptionLine(
        medicineName: structured.group(1)!.trim(),
        dosageFrequencyTiming: structured.group(2)!.trim(),
        days: '$days',
      );
    }

    final words = work.split(RegExp(r'\s+'));
    if (words.length >= 3) {
      return PrescriptionLine(
        medicineName: words.take(2).join(' '),
        dosageFrequencyTiming: words.skip(2).join(' '),
        days: '$days',
      );
    }

    return PrescriptionLine(
      medicineName: work.isEmpty ? '—' : work,
      dosageFrequencyTiming: '',
      days: '$days',
    );
  }
}
