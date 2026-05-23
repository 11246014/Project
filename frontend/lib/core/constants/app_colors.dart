import 'package:flutter/material.dart';

/// 全域色彩常數
/// 主題：科技感深色系（深海藍 + 電光藍）
class AppColors {
  AppColors._(); // 私有建構子，防止被實例化

  // 背景層次（由深到淺）
  static const Color background     = Color(0xFF0A0E1A); // 頁面最底層背景
  static const Color surface        = Color(0xFF111827); // 卡片背景
  static const Color surfaceVariant = Color(0xFF1C2537); // 次要卡片、輸入框背景

  // 主色
  static const Color primary        = Color(0xFF3B82F6); // 電光藍，按鈕、連結
  static const Color primaryLight   = Color(0xFF60A5FA); // 較淺的藍，hover 狀態
  static const Color accent         = Color(0xFF06B6D4); // 青藍色，標籤 highlight

  // 文字
  static const Color textPrimary    = Color(0xFFF1F5F9); // 主要文字（近白）
  static const Color textSecondary  = Color(0xFF94A3B8); // 次要文字（灰藍）
  static const Color textHint       = Color(0xFF475569); // 提示文字、placeholder

  // 邊框
  static const Color border         = Color(0xFF1E293B); // 一般邊框
  static const Color borderFocus    = Color(0xFF3B82F6); // 輸入框聚焦邊框

  // 狀態色
  static const Color success        = Color(0xFF10B981); // 成功（綠）
  static const Color error          = Color(0xFFEF4444); // 錯誤（紅）
  static const Color warning        = Color(0xFFF59E0B); // 警告（黃）

  // 漸層：主要按鈕用
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [Color(0xFF3B82F6), Color(0xFF06B6D4)],
    begin: Alignment.centerLeft,
    end: Alignment.centerRight,
  );

  // 漸層：頁面背景用
  static const LinearGradient backgroundGradient = LinearGradient(
    colors: [Color(0xFF0A0E1A), Color(0xFF111827)],
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
  );

  // ── 淺色主題專用色彩 ────────────────────────────
  static const Color lightBackground     = Color(0xFFF8FAFC);
  static const Color lightSurface        = Color(0xFFFFFFFF);
  static const Color lightSurfaceVariant = Color(0xFFE8EDF2);
  static const Color lightTextPrimary    = Color(0xFF0A0A0A);
  static const Color lightTextSecondary  = Color(0xFF1E293B);
  static const Color lightTextHint       = Color(0xFF475569);
  static const Color lightBorder         = Color(0xFFE2E8F0);
  static const Color lightBorderFocus    = Color(0xFF3B82F6);

  static const LinearGradient lightBackgroundGradient = LinearGradient(
    colors: [Color(0xFFF8FAFC), Color(0xFFEFF6FF)],
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
  );

  /// 根據 BuildContext 取得當前主題對應的色彩
  /// 使用方式：AppColors.bg(context)
  static Color bg(BuildContext context) =>
      Theme.of(context).brightness == Brightness.dark
          ? background
          : lightBackground;

  static Color cardBg(BuildContext context) =>
      Theme.of(context).brightness == Brightness.dark
          ? surface
          : lightSurface;

  static Color cardVariant(BuildContext context) =>
      Theme.of(context).brightness == Brightness.dark
          ? surfaceVariant
          : lightSurfaceVariant;

  static Color textMain(BuildContext context) =>
      Theme.of(context).brightness == Brightness.dark
          ? textPrimary
          : lightTextPrimary;

  static Color textSub(BuildContext context) =>
      Theme.of(context).brightness == Brightness.dark
          ? textSecondary
          : lightTextSecondary;

  static Color textPlaceholder(BuildContext context) =>
      Theme.of(context).brightness == Brightness.dark
          ? textHint
          : lightTextHint;

  static Color borderColor(BuildContext context) =>
      Theme.of(context).brightness == Brightness.dark
          ? border
          : lightBorder;

  static LinearGradient bgGradient(BuildContext context) =>
      Theme.of(context).brightness == Brightness.dark
          ? backgroundGradient
          : lightBackgroundGradient;
}