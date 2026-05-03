import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'core/constants/app_routes.dart';
import 'core/theme/app_theme.dart';
import 'features/auth/screens/login_screen.dart';
import 'features/auth/screens/register_screen.dart';
import 'features/home/screens/home_screen.dart';
import 'features/filter/screens/filter_screen.dart';
import 'features/chat/screens/chat_screen.dart';


/// GoRouter 路由設定
/// W2 以後新頁面直接在 routes 裡新增 GoRoute 即可
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
    // GoRoute(path: AppRoutes.filter, builder: ...),
    // GoRoute(path: AppRoutes.chat,   builder: ...),
  ],
);

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'WearAI Shop',
      debugShowCheckedModeBanner: false,
      // 套用深色主題
      theme: AppTheme.darkTheme,
      // 套用路由設定
      routerConfig: _router,
    );
  }
}