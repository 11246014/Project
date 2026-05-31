import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter/material.dart';

/// 主題模式 Provider
/// 控制全 App 的深色/淺色切換
final themeProvider = StateNotifierProvider<ThemeNotifier, ThemeMode>((ref) {
  return ThemeNotifier();
});

class ThemeNotifier extends StateNotifier<ThemeMode> {
  // 預設深色模式
  ThemeNotifier() : super(ThemeMode.dark);

  /// 切換主題
  void toggle() {
    state = state == ThemeMode.dark ? ThemeMode.light : ThemeMode.dark;
  }

  /// 是否為深色模式
  bool get isDark => state == ThemeMode.dark;
}