/// 路由名稱常數
/// 所有頁面路徑集中管理，禁止在其他地方直接寫路徑字串
class AppRoutes {
  AppRoutes._(); // 私有建構子，防止被實例化

  // ── 驗證相關 ────────────────────────────
  /// 登入頁
  static const String login    = '/login';

  /// 註冊頁
  static const String register = '/register';

  // ── 主要頁面 ────────────────────────────
  /// 首頁（商品列表）
  static const String home     = '/home';

  /// 情境篩選器
  static const String filter   = '/filter';

  /// AI 聊天導購
  static const String chat     = '/chat';

  /// 商品詳細頁
  static const String product  = '/product';

  // ── 個人相關 ────────────────────────────
  /// 個人偏好設定
  static const String profile  = '/profile';

  /// 購物車
  static const String cart     = '/cart';

  // ── 後台 ────────────────────────────────
  /// 商品管理後台
  static const String admin    = '/admin';
}