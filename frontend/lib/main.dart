import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import 'core/constants/app_routes.dart';
import 'core/theme/app_theme.dart';
import 'core/theme/theme_provider.dart';
import 'features/auth/screens/login_screen.dart';
import 'features/auth/screens/register_screen.dart';
import 'features/auth/screens/forgot_password_screen.dart';
import 'features/home/screens/home_screen.dart';
import 'features/filter/screens/filter_screen.dart';
import 'features/filter/screens/recommendation_screen.dart';
import 'features/chat/screens/chat_screen.dart';
import 'features/profile/screens/profile_screen.dart';

/// GoRouter 路由設定
/// 新頁面直接在 routes 裡新增 GoRoute 即可
final _router = GoRouter(
  initialLocation: AppRoutes.login,
  redirect: (context, state) async {
    final token = await const FlutterSecureStorage().read(key: 'token');
    final isLoggedIn = token != null && token.isNotEmpty;

    // 不需要登入就能進入的頁面
    final isOnPublicPage =
        state.matchedLocation == AppRoutes.login ||
        state.matchedLocation == AppRoutes.register ||
        state.matchedLocation == AppRoutes.forgotPassword; // ← 正確用 || 串接

    // 沒有 Token 且不在公開頁 → 強制去登入頁
    if (!isLoggedIn && !isOnPublicPage) return AppRoutes.login;

    // 有 Token 且在登入／註冊頁 → 直接進首頁
    // 注意：忘記密碼頁即使已登入也可以進，所以不擋
    if (isLoggedIn &&
        (state.matchedLocation == AppRoutes.login ||
         state.matchedLocation == AppRoutes.register)) {
      return AppRoutes.home;
    }

    // 其他情況不做跳轉
    return null;
  },
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
      path: AppRoutes.forgotPassword,
      builder: (context, state) => const ForgotPasswordScreen(),
    ),
    GoRoute(
      path: AppRoutes.home,
      builder: (context, state) => const HomeScreen(),
    ),
    GoRoute(
      path: AppRoutes.filter,
      builder: (context, state) => const FilterScreen(),
    ),
    GoRoute(
      path: AppRoutes.chat,
      builder: (context, state) => const ChatScreen(),
    ),
    GoRoute(
      path: AppRoutes.recommendation,
      builder: (context, state) {
        final result = state.extra as Map<String, dynamic>? ?? {};
        return RecommendationScreen(result: result);
      },
    ),
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
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: themeMode,
      routerConfig: _router,
    );
  }
}