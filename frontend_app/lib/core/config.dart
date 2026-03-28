import 'dart:io';
import 'package:flutter/foundation.dart';

class ApiConfig {
  // 🚀 PRODUCTION - Render Backend
  static const String _productionUrl = "https://parentcode-backend.onrender.com";

  // 🧪 LOCAL DEVELOPMENT URLs (for testing)
  static const String _emulatorUrl = "http://10.0.2.2:8000";
  static const String _realDeviceUrl = "http://10.186.218.207:8000";  // Updated with your laptop IP
  static const String _localUrl = "http://localhost:8000";

  static String get baseUrl {
    // 🧪 DEVELOPMENT MODE - Using local backend for testing
    if (kReleaseMode) {
      return _productionUrl;  // Use production in release mode
    }

    if (Platform.isAndroid) {
      return _realDeviceUrl;  // Real phone connected via USB
      // return _emulatorUrl;  // Emulator
    }

    return _localUrl;  // Web/Windows

    // ✅ PRODUCTION MODE - Uncomment this line to use production
    // return _productionUrl;
  }
}
