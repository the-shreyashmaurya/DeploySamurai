import 'package:flutter/material.dart';

import '../../core/theme/app_colors.dart';
import '../pages/dashboard_page.dart';

class DeploySamuraiApp extends StatelessWidget {
  const DeploySamuraiApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'DeploySamurai',
      theme: ThemeData(
        useMaterial3: true,
        scaffoldBackgroundColor: AppColors.background,
        fontFamily: 'Arial',
        colorScheme: ColorScheme.fromSeed(
          seedColor: AppColors.teal,
          surface: AppColors.surface,
        ),
        textTheme: ThemeData.light().textTheme.apply(
          bodyColor: AppColors.text,
          displayColor: AppColors.text,
          fontFamily: 'Arial',
        ),
      ),
      home: const DashboardPage(),
    );
  }
}
