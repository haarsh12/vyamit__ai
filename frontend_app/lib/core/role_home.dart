import 'package:flutter/material.dart';

import '../screens/home_screen.dart';
import '../screens/doctor/doctor_home_screen.dart';

/// Same app shell: retail [HomeScreen] vs [DoctorHomeScreen] by category.
Widget buildHomeForShopCategory(String? shopCategory) {
  if (shopCategory == 'Doctor') {
    return const DoctorHomeScreen();
  }
  return const HomeScreen();
}
