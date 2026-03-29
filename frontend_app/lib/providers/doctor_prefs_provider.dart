import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Local prefs for Doctor Mode (e.g. specialization shown on Create Prescription).
class DoctorPrefsProvider extends ChangeNotifier {
  static const _key = 'doctor_specialization';

  String specialization = '';

  Future<void> load() async {
    final p = await SharedPreferences.getInstance();
    specialization = p.getString(_key) ?? '';
    notifyListeners();
  }

  Future<void> setSpecialization(String value) async {
    specialization = value.trim();
    final p = await SharedPreferences.getInstance();
    await p.setString(_key, specialization);
    notifyListeners();
  }
}
