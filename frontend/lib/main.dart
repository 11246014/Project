import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'core/constants/app_routes.dart';
import 'core/theme/app_theme.dart';
import 'features/auth/screens/login_screen.dart';
import 'features/auth/screens/register_screen.dart';
import 'features/home/screens/home_screen.dart';
import 'features/filter/screens/filter_screen.dart';
import 'features/chat/screens/chat_screen.dart';
import 'features/profile/screens/profile_screen.dart';
import 'features/auth/screens/forgot_password_screen.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'core/theme/theme_provider.dart';


/// GoRouter 路由設定
/// 新頁面直接在 routes 裡新增 GoRoute 即可
final _router = GoRouter(
  // App 啟動時第一個顯示的頁面
  initialLocation: AppRoutes.login,
  routes: [
    GoRoute(
      path: AppRoutes.login,
      builder: (context, state) => const LoginScreen(),
    ),
    GoRoute(
      path: AppRoutes.register,
      builder: (context, state) => const RegisterScreen(),
    ),
    GoRoute(
      path: AppRoutes.home,
      builder: (context, state) => const HomeScreen(),
    ),
    // W2 以後在這裡繼續新增：
    GoRoute(
      path: AppRoutes.filter,
      builder: (context, state) => const FilterScreen(),
    ),
    GoRoute(
      path: AppRoutes.chat,
      builder: (context, state) => const ChatScreen(),
    ),
    GoRoute(
      path: AppRoutes.forgotPassword,
      builder: (context, state) => const ForgotPasswordScreen(),
    ),
    // GoRoute(path: AppRoutes.filter, builder: ...),
    // GoRoute(path: AppRoutes.chat,   builder: ...),
  ],
);

void main() {
  runApp(
    const ProviderScope(child: MyApp()),
  );
}

class MyApp extends ConsumerWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // 監聽主題狀態
    final themeMode = ref.watch(themeProvider);

    return MaterialApp.router(
      title: 'WearWise',
      debugShowCheckedModeBanner: false,
      // 同時提供深色和淺色主題
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: themeMode,
      routerConfig: _router,
    );
  }
}