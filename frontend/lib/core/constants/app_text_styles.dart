import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'app_colors.dart';

/// 全域字體樣式
/// 標題：Sora
/// 內文：DM Sans
class AppTextStyles {
  AppTextStyles._(); // 私有建構子，防止被實例化

  // ── 大標題 ──────────────────────────────
  /// 頁面主標題，例如「歡迎回來」
  static TextStyle displayLarge = GoogleFonts.sora(
    fontSize: 34,
    fontWeight: FontWeight.w700,
    color: AppColors.textPrimary,
    letterSpacing: -0.5,
  );

  /// 區塊標題，例如「為你推薦」
  static TextStyle displayMedium = GoogleFonts.sora(
    fontSize: 26,
    fontWeight: FontWeight.w600,
    color: AppColors.textPrimary,
    letterSpacing: -0.3,
  );

  // ── 內文 ────────────────────────────────
  /// 主要說明文字
  static TextStyle bodyLarge = GoogleFonts.dmSans(
    fontSize: 18,
    fontWeight: FontWeight.w400,
    color: AppColors.textPrimary,
    height: 1.6,
  );

  /// 次要說明文字，例如副標、描述
  static TextStyle bodyMedium = GoogleFonts.dmSans(
    fontSize: 16,
    fontWeight: FontWeight.w400,
    color: AppColors.textSecondary,
    height: 1.5,
  );

  // ── 標籤 / 按鈕 ─────────────────────────
  /// 按鈕文字、重要標籤
  static TextStyle labelLarge = GoogleFonts.sora(
    fontSize: 18,
    fontWeight: FontWeight.w600,
    color: AppColors.textPrimary,
    letterSpacing: 0.3,
  );

  /// 小字提示，例如版權、時間戳記
  static TextStyle caption = GoogleFonts.dmSans(
    fontSize: 15,
    fontWeight: FontWeight.w400,
    color: AppColors.textHint,
  );
}