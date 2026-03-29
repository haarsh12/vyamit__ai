import 'package:uuid/uuid.dart';

/// One row in the prescription table (voice or manual).
class PrescriptionLine {
  final String id;
  String medicineName;
  String dosageFrequencyTiming;
  String days;

  PrescriptionLine({
    String? id,
    required this.medicineName,
    required this.dosageFrequencyTiming,
    required this.days,
  }) : id = id ?? const Uuid().v4();

  Map<String, dynamic> toJson() => {
        'medicine_name': medicineName,
        'dosage_frequency_timing': dosageFrequencyTiming,
        'days': days,
      };

  PrescriptionLine copyWith({
    String? medicineName,
    String? dosageFrequencyTiming,
    String? days,
  }) {
    return PrescriptionLine(
      id: id,
      medicineName: medicineName ?? this.medicineName,
      dosageFrequencyTiming:
          dosageFrequencyTiming ?? this.dosageFrequencyTiming,
      days: days ?? this.days,
    );
  }
}
