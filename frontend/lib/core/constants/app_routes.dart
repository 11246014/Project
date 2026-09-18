/// 路由名稱常數
/// 所有頁面路徑集中管理，禁止在其他地方直接寫路徑字串
class AppRoutes {
  AppRoutes._(); // 私有建構子，防止被實例化

  // ── 驗證相關 ────────────────────────────
  /// 登入頁
  static const String login    = '/login';

  /// 註冊頁
  static const String register = '/register';

  ///忘記密碼頁
  static const String forgotPassword = '/forgot-password';
  
  // ── 主要頁面 ────────────────────────────
  /// 首頁（商品列表）
  static const String home     = '/home';

  /// 情境篩選器
  static const String filter   = '/filter';

  /// 情境篩選頁
  static const String recommendation = '/recommendation';

  /// 單一商品的完整心得列表（「查看全部心得」用）
  static const String productReviews = '/product/reviews';

  /// 社群心得動態牆
  static const String community = '/community';

  /// AI 聊天導購
  static const String chat     = '/chat';

  /// 商品詳細頁
  static const String product  = '/product';

  // ── 個人相關 ────────────────────────────
  /// 個人偏好設定
  static const String profile  = '/profile';

  /// 購物車
  static const String cart     = '/cart';

  
 
}