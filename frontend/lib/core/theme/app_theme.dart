import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../constants/app_colors.dart';
import '../constants/app_text_styles.dart';

/// 全域主題設定
/// 將 AppColors 與 AppTextStyles 統一套用到所有元件
class AppTheme {
  AppTheme._(); // 私有建構子，防止被實例化

  static ThemeData get darkTheme => ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    scaffoldBackgroundColor: AppColors.background,

    // 色彩系統
    colorScheme: const ColorScheme.dark(
      primary: AppColors.primary,
      secondary: AppColors.accent,
      surface: AppColors.surface,
      error: AppColors.error,
    ),

    // AppBar 預設樣式
    appBarTheme: AppBarTheme(
      backgroundColor: AppColors.background,
      elevation: 0,
      centerTitle: true,
      titleTextStyle: AppTextStyles.displayMedium,
      // 讓手機頂部狀態列文字變白色
      systemOverlayStyle: SystemUiOverlayStyle.light,
      iconTheme: const IconThemeData(color: AppColors.textPrimary),
    ),

    // 所有 TextFormField / TextField 預設樣式
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: AppColors.surfaceVariant,
      contentPadding:
          const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      hintStyle: AppTextStyles.bodyMedium,
      // 預設邊框
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: AppColors.border),
      ),
      // 未聚焦邊框
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: AppColors.border),
      ),
      // 聚焦時邊框變藍
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide:
            const BorderSide(color: AppColors.borderFocus, width: 1.5),
      ),
      // 驗證錯誤邊框
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: AppColors.error),
      ),
      focusedErrorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: AppColors.error, width: 1.5),
      ),
    ),

    // 所有 ElevatedButton 預設樣式
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: AppColors.primary,
        foregroundColor: Colors.white,
        minimumSize: const Size(double.infinity, 52),
        shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12)),
        textStyle: AppTextStyles.labelLarge,
        elevation: 0,
      ),
    ),

    // 底部導覽列預設樣式
    bottomNavigationBarTheme: BottomNavigationBarThemeData(
      backgroundColor: AppColors.surface,
      selectedItemColor: AppColors.primary,
      unselectedItemColor: AppColors.textHint,
      elevation: 0,
      type: BottomNavigationBarType.fixed,
    ),
  );
}