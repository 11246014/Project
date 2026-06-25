import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import 'core/constants/app_routes.dart';
import 'core/theme/app_theme.dart';
import 'core/theme/theme_provider.dart';
import 'core/constants/app_colors.dart';
import 'features/auth/screens/login_screen.dart';
import 'features/auth/screens/register_screen.dart';
import 'features/auth/screens/forgot_password_screen.dart';
import 'features/home/screens/home_screen.dart';
import 'features/filter/screens/filter_screen.dart';
import 'features/filter/screens/recommendation_screen.dart';
import 'features/chat/screens/chat_screen.dart';
import 'features/profile/screens/profile_screen.dart';
import 'package:flutter/gestures.dart';
import 'package:google_fonts/google_fonts.dart';

// ════════════════════════════════════════════════════
// 自訂 ScrollBehavior
// 讓滾輪條永遠顯示在瀏覽器最右側，不侷限在 App 內容區域內
// ════════════════════════════════════════════════════
class WebScrollBehavior extends ScrollBehavior {
  const WebScrollBehavior();

  @override
  Widget buildScrollbar(
    BuildContext context,
    Widget child,
    ScrollableDetails details,
  ) {
    // 回傳原始 child，不在內容區域內建立 scrollbar
    // 讓瀏覽器原生的滾輪條接管（位置在最右側）
    return child;
  }

  @override
  Set<PointerDeviceKind> get dragDevices => {
        PointerDeviceKind.touch,
        PointerDeviceKind.mouse, // 讓滑鼠也能拖曳滾動
        PointerDeviceKind.trackpad,
      };
}

// ════════════════════════════════════════════════════
// 頂部固定 NavBar
// ════════════════════════════════════════════════════
class WebNavBar extends StatelessWidget implements PreferredSizeWidget {
  const WebNavBar({super.key});

  static const double navBarHeight = 56;

  @override
  Size get preferredSize => const Size.fromHeight(navBarHeight);

  @override
  Widget build(BuildContext context) {
    return Container(
      height: navBarHeight,
      decoration: const BoxDecoration(
        gradient: AppColors.primaryGradient,
        boxShadow: [
          BoxShadow(
            color: Color(0x663B82F6),
            blurRadius: 12,
            offset: Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          const SizedBox(width: 24),
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 32,
                height: 32,
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: Image.asset(
                    'assets/images/LOGO.png',
                    fit: BoxFit.contain,
                  ),
                ),
              ),
              const SizedBox(width: 10),
              Text(
                'WearWise',
                style: GoogleFonts.sora(
                  fontSize: 18,
                  fontWeight: FontWeight.w700,
                  color: Colors.white,
                  letterSpacing: 0.5,
                ),
              ),
            ],
          ),
          const Spacer(),
          Text(
            '智慧穿戴裝置推薦',
            style: GoogleFonts.dmSans(
              fontSize: 13,
              color: Colors.white.withValues(alpha: 0.85),
              fontWeight: FontWeight.w400,
            ),
          ),
          const SizedBox(width: 24),
        ],
      ),
    );
  }
}

// ════════════════════════════════════════════════════
// Web 版主要佈局
// ════════════════════════════════════════════════════
class WebLayout extends StatelessWidget {
  final Widget child;

  const WebLayout({super.key, required this.child});

  static const double contentWidth = 430;
  static const Color bgColor = Color(0xFF1E2A3A);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const WebNavBar(),
      backgroundColor: bgColor,
      body: Row(
        children: [
          const Spacer(),
          SizedBox(
            width: contentWidth,
            child: Material(
              elevation: 16,
              shadowColor: Colors.black.withValues(alpha: 0.8),
              shape: RoundedRectangleBorder(
                side: BorderSide(
                  color: AppColors.primary.withValues(alpha: 0.15),
                  width: 1,
                ),
              ),
              child: child,
            ),
          ),
          const Spacer(),
        ],
      ),
    );
  }
}

// ════════════════════════════════════════════════════
// GoRouter 路由設定
// ════════════════════════════════════════════════════
final _router = GoRouter(
  initialLocation: AppRoutes.login,
  redirect: (context, state) async {
    final token = await const FlutterSecureStorage().read(key: 'token');
    final isLoggedIn = token != null && token.isNotEmpty;

    // 不需要登入就能進入的頁面
    final isOnPublicPage =
        state.matchedLocation == AppRoutes.login ||
        state.matchedLocation == AppRoutes.register ||
        state.matchedLocation == AppRoutes.forgotPassword;

    // 沒有 Token 且不在公開頁 → 強制去登入頁
    if (!isLoggedIn && !isOnPublicPage) return AppRoutes.login;

    // 有 Token 且在登入／註冊頁 → 直接進首頁
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
      pageBuilder: (context, state) => const NoTransitionPage(
        child: WebLayout(child: LoginScreen()),
      ),
    ),
    GoRoute(
      path: AppRoutes.register,
      pageBuilder: (context, state) => const NoTransitionPage(
        child: WebLayout(child: RegisterScreen()),
      ),
    ),
    GoRoute(
      path: AppRoutes.forgotPassword,
      pageBuilder: (context, state) => const NoTransitionPage(
        child: WebLayout(child: ForgotPasswordScreen()),
      ),
    ),
    GoRoute(
      path: AppRoutes.home,
      pageBuilder: (context, state) => const NoTransitionPage(
        child: WebLayout(child: HomeScreen()),
      ),
    ),
    GoRoute(
      path: AppRoutes.filter,
      pageBuilder: (context, state) => const NoTransitionPage(
        child: WebLayout(child: FilterScreen()),
      ),
    ),
    GoRoute(
      path: AppRoutes.chat,
      pageBuilder: (context, state) => const NoTransitionPage(
        child: WebLayout(child: ChatScreen()),
      ),
    ),
    GoRoute(
      path: AppRoutes.recommendation,
      pageBuilder: (context, state) {
        final result = state.extra as Map<String, dynamic>? ?? {};
        return NoTransitionPage(
          child: WebLayout(
            child: RecommendationScreen(result: result),
          ),
        );
      },
    ),
  ],
);

void main() {
  runApp(const ProviderScope(child: MyApp()));
}

class MyApp extends ConsumerWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final themeMode = ref.watch(themeProvider);

    return MaterialApp.router(
      title: 'WearWise',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: themeMode,
      routerConfig: _router,
      // 套用自訂 ScrollBehavior，讓滾輪在瀏覽器最右側
      scrollBehavior: const WebScrollBehavior(),
    );
  }
}