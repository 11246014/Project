import 'package:flutter/material.dart';
import '../../../core/constants/app_colors.dart';
import '../../../core/constants/app_text_styles.dart';
import '../../../shared/widgets/custom_button.dart';
import 'package:go_router/go_router.dart';
import '../../../core/constants/app_routes.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/theme/theme_provider.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../../../services/user_service.dart';
import '../../../core/providers/user_profile_provider.dart';
import '../../../core/providers/cart_provider.dart';
import '../../../core/utils/launch_helper.dart';
import '../../../core/constants/app_formatters.dart';

class ProfileScreen extends ConsumerStatefulWidget {
  const ProfileScreen({super.key});

  @override
  ConsumerState<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends ConsumerState<ProfileScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  late final TextEditingController _occupationController;
  late final TextEditingController _currentDeviceController;

  // 串接後從 API 取得
Map<String, dynamic> _user = {
  'name': '載入中...',
  'email': '',
  'avatar': null,
};


  // 歷史紀錄改為向後端拉取真實資料，不再使用 mock
  List<Map<String, dynamic>> _history = [];
  bool _isHistoryLoading = true;
  bool _hasHistoryError = false;


  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _loadUserInfo();

    _occupationController =
    TextEditingController(text: ref.read(userProfileProvider).occupation);
    _currentDeviceController =
    TextEditingController(text: ref.read(userProfileProvider).currentDevice);
  }

  Future<void> _loadUserInfo() async {
  try {
    final user = await UserService.getMe();
    if (mounted) {
      setState(() {
        // 後端 /me 會回傳 username（註冊時填的暱稱）
        // 若是舊帳號沒有暱稱資料，退回顯示 email 帳號名稱，不顯示「載入中」
        final rawUsername = user['username']?.toString() ?? '';
        final email = user['email']?.toString() ?? '';
        _user = {
          'name': rawUsername.isNotEmpty
              ? rawUsername
              : (email.contains('@') ? email.split('@').first : '使用者'),
          'email': email,
          'avatar': null,
        };
      });

      // 將後端已存的個人資訊寫入 Provider
        // 讓使用者不用每次登入都重填年齡層、職業、目前裝置
        ref.read(userProfileProvider.notifier).hydrate(user);

        // Dropdown 靠 ref.watch 會自動刷新，但文字輸入框要手動同步 controller
        _occupationController.text = ref.read(userProfileProvider).occupation;
        _currentDeviceController.text =
            ref.read(userProfileProvider).currentDevice;
            
    }
  } catch (e) {
    // 失敗時也要更新畫面，不然名稱會永遠卡在初始值「載入中...」
    debugPrint('載入使用者資訊失敗：$e');
    if (mounted) {
      setState(() {
        _user = {'name': '使用者', 'email': '', 'avatar': null};
      });
    }
  }

  // 個人資訊處理完（無論成功失敗）後，接著載入歷史紀錄
  _loadHistory();
}

/// 向後端取得歷史紀錄，並更新載入 / 錯誤狀態
Future<void> _loadHistory() async {
  setState(() {
    _isHistoryLoading = true;
    _hasHistoryError = false;
  });
  try {
    final history = await UserService.getHistory();
    if (mounted) {
      setState(() {
        _history = history;
        _isHistoryLoading = false;
      });
    }
  } catch (e) {
    debugPrint('載入歷史紀錄失敗：$e');
    if (mounted) {
      setState(() {
        _hasHistoryError = true;
        _isHistoryLoading = false;
      });
    }
  }
}

  @override
  void dispose() {
    _tabController.dispose();
    _occupationController.dispose();
    _currentDeviceController.dispose();
    super.dispose();
  }


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bg(context),
      body: SafeArea(
        child: Column(
          children: [
            // 頂部使用者資訊
            _buildUserHeader(),

            // Tab 列
            _buildTabBar(),

            // Tab 內容
            Expanded(
              child: TabBarView(
                controller: _tabController,
                children: [
                  _buildPreferenceTab(),
                  _buildHistoryTab(),
                  _buildCartTab(),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// 頂部使用者資訊區
  Widget _buildUserHeader() {
    return Container(
      padding: const EdgeInsets.fromLTRB(20, 20, 20, 16),
      decoration: BoxDecoration(
        color: AppColors.cardBg(context),
        border: Border(bottom: BorderSide(color: AppColors.borderColor(context))),
      ),
      child: Row(
        children: [
          // 頭像
          Container(
            width: 56,
            height: 56,
            decoration: BoxDecoration(
              gradient: AppColors.primaryGradient,
              borderRadius: BorderRadius.circular(16),
            ),
            child: const Icon(
              Icons.person_rounded,
              color: Colors.white,
              size: 28,
            ),
          ),
          const SizedBox(width: 14),

          // 名稱 + Email
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  _user['name'],
                  style: AppTextStyles.displayMedium.copyWith(
                    fontSize: 18,
                    color: AppColors.textMain(context)),
                ),
                const SizedBox(height: 4),
                Text(
                  _user['email'],
                  style: AppTextStyles.bodyLarge.copyWith(
                  color: AppColors.textMain(context),
                ),
                ),
              ],
            ),
          ),

          // 編輯按鈕
          IconButton(
            onPressed: () {
              // TODO：編輯個人資料
            },
            icon: Icon(
              Icons.edit_outlined,
              color: AppColors.textMain(context),
              size: 20,
            ),
          ),
        ],
      ),
    );
  }

  /// Tab 列
  Widget _buildTabBar() {
    return Container(
      color: AppColors.cardBg(context),
      child: TabBar(
        controller: _tabController,
        labelColor: AppColors.primary,
        unselectedLabelColor: AppColors.textHint,
        labelStyle: AppTextStyles.caption.copyWith(fontWeight: FontWeight.w600),
        unselectedLabelStyle: AppTextStyles.caption,
        indicatorColor: AppColors.primary,
        indicatorWeight: 2,
        tabs: const [
          Tab(text: '偏好設定'),
          Tab(text: '歷史紀錄'),
          Tab(text: '購物車'),
        ],
      ),
    );
  }

  // ── Tab 1：偏好設定 ────────────────────────────────────
  Widget _buildPreferenceTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 個人資訊（皆為選填，會自動套用到 Filter 問卷與 AI 聊天推薦）
          Text('個人資訊', style: AppTextStyles.displayMedium.copyWith(
              fontSize: 16, color: AppColors.textMain(context))),
          const SizedBox(height: 6),
          Text('填寫後，AI 推薦時會自動參考這些資訊',
              style: AppTextStyles.bodyMedium.copyWith(color: AppColors.textSub(context))),
          const SizedBox(height: 16),

          _buildProfileDropdown(
            label: '年齡層',
            // 如果舊資料不在新選項清單裡，就當作沒填，讓使用者重選
            value: const [
              '18 歲以下', '19–25 歲', '26–35 歲', '36–45 歲', '46–55 歲', '56 歲以上',
            ].contains(ref.watch(userProfileProvider).ageRange)
                ? ref.watch(userProfileProvider).ageRange
                : '',
            options: const [
              '18 歲以下', '19–25 歲', '26–35 歲', '36–45 歲', '46–55 歲', '56 歲以上',
            ],
            onChanged: ref.read(userProfileProvider.notifier).updateAgeRange,
          ),
          const SizedBox(height: 12),

          _buildProfileTextField(
            controller: _occupationController,
            label: '職業',
            hint: '例如：學生、工程師、教師、運動員',
            onChanged: ref.read(userProfileProvider.notifier).updateOccupation,
          ),
          const SizedBox(height: 12),

          _buildProfileTextField(
            controller: _currentDeviceController,
            label: '目前已經在使用的商品',
            hint: '例如：手機型號、Apple Watch SE、小米手環 7、無',
            onChanged: ref.read(userProfileProvider.notifier).updateCurrentDevice,
          ),
          const SizedBox(height: 28),

          // 系統設定
          Text('系統設定', style: AppTextStyles.displayMedium.copyWith(
            fontSize: 16,
            color: AppColors.textMain(context))),
          const SizedBox(height: 12),

          

          _buildSettingItem(
            icon: Icons.notifications_outlined,
            label: '推播通知',
            trailing: Switch(
              value: true,
              onChanged: (_) {},
              activeColor: AppColors.primary,
            ),
          ),
          _buildSettingItem(
            icon: Icons.dark_mode_outlined,
            label: '深色模式',
            trailing: Switch(
              // 從 Provider 讀取當前主題狀態
              value: ref.watch(themeProvider) == ThemeMode.dark,
              onChanged: (_) => ref.read(themeProvider.notifier).toggle(),
              activeColor: AppColors.primary,
            ),
          ),
          _buildSettingItem(
            icon: Icons.language_outlined,
            label: '語言設定',
            trailing: Text('繁體中文',
                style: AppTextStyles.caption
                    .copyWith(color: AppColors.textMain(context))),
          ),
          const SizedBox(height: 28),

          // 登出按鈕
          CustomButton(
            label: '登出',
            onTap: () {
              showDialog(
                context: context,
                builder: (context) => AlertDialog(
                  backgroundColor: AppColors.cardBg(context),
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16)),
                  title: Text('登出',
                      style: AppTextStyles.displayMedium.copyWith(fontSize: 16,color: AppColors.textMain(context))),
                      
                  content: Text(
                    '確定要登出嗎？',
                    style: AppTextStyles.bodyMedium.copyWith(
                        color: AppColors.textMain(context)
),
                  ),
                  actions: [
                    TextButton(
                      onPressed: () => Navigator.pop(context),
                      child: Text('取消',
                          style: AppTextStyles.bodyMedium
                              .copyWith(color: AppColors.textMain(context))),
                    ),
                    TextButton(
                      onPressed: () async {
                        Navigator.pop(context);
                        await const FlutterSecureStorage().deleteAll();
                        ref.read(userProfileProvider.notifier).reset();
                        if (mounted) context.go(AppRoutes.login);
                      },
                      child: Text('登出',
                          style: AppTextStyles.bodyMedium
                              .copyWith(color: AppColors.error)),
                    ),
                  ],
                ),
              );
            },
            variant: ButtonVariant.outline,
          ),
        ],
      ),
    );
  }

  /// 個人資訊下拉選單（用於選項固定的欄位，例如年齡層）
  Widget _buildProfileDropdown({
    required String label,
    required String value,
    required List<String> options,
    required ValueChanged<String> onChanged,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      decoration: BoxDecoration(
        color: AppColors.cardBg(context),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.borderColor(context)),
      ),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<String>(
          isExpanded: true,
          value: value.isEmpty ? null : value,
          hint: Text(label,
              style: AppTextStyles.bodyMedium.copyWith(color: AppColors.textSub(context))),
          dropdownColor: AppColors.cardBg(context),
          style: AppTextStyles.bodyMedium.copyWith(color: AppColors.textMain(context)),
          items: options.map((o) => DropdownMenuItem(value: o, child: Text(o))).toList(),
          onChanged: (v) {
            if (v != null) onChanged(v);
          },
        ),
      ),
    );
  }

  /// 個人資訊文字輸入（用於職業、目前裝置等自由輸入欄位）
  Widget _buildProfileTextField({
    required TextEditingController controller,
    required String label,
    required String hint,
    required ValueChanged<String> onChanged,
  }) {
    return TextFormField(
      controller: controller,
      onChanged: onChanged,
      style: AppTextStyles.bodyMedium.copyWith(color: AppColors.textMain(context)),
      decoration: InputDecoration(
        labelText: label,
        hintText: hint,
        filled: true,
        fillColor: AppColors.cardBg(context),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: AppColors.borderColor(context)),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: AppColors.borderColor(context)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: AppColors.borderFocus, width: 1.5),
        ),
      ),
    );
  }

  /// 設定列表項目
  Widget _buildSettingItem({
    required IconData icon,
    required String label,
    required Widget trailing,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: AppColors.cardBg(context),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.borderColor(context)),
      ),
      child: Row(
        children: [
          Icon(icon, color: AppColors.textMain(context), size: 20),
          const SizedBox(width: 12),
          Expanded(
            child: Text(label, style: AppTextStyles.bodyMedium
                .copyWith(color: AppColors.textMain(context))),
          ),
          trailing,
        ],
      ),
    );
  }

  // ── Tab 2：歷史紀錄 ────────────────────────────────────
  Widget _buildHistoryTab() {
    // 狀態一：載入中
    if (_isHistoryLoading) {
      return const Center(
        child: CircularProgressIndicator(color: AppColors.primary),
      );
    }

    // 狀態二：載入失敗
    if (_hasHistoryError) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.wifi_off_rounded, size: 48, color: AppColors.textHint),
            const SizedBox(height: 12),
            Text('載入歷史紀錄失敗',
                style: AppTextStyles.bodyMedium
                    .copyWith(color: AppColors.textSub(context))),
            const SizedBox(height: 12),
            TextButton(
              onPressed: _loadHistory,
              child: const Text('重新載入'),
            ),
          ],
        ),
      );
    }

    // 狀態三：沒有紀錄
    if (_history.isEmpty) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.history, size: 48, color: AppColors.textHint),
            const SizedBox(height: 12),
            Text('還沒有瀏覽紀錄', style: AppTextStyles.bodyMedium.copyWith(color: AppColors.textSub(context))),
          ],
        ),
      );
    }

    // 狀態四：正常顯示（資料來自後端 /history/{email}）
    return ListView.builder(
      padding: const EdgeInsets.all(20),
      itemCount: _history.length,
      itemBuilder: (context, index) {
        final item = _history[index];
        final tags = List<String>.from(item['tags'] ?? []);

        // 點擊卡片可進入商品詳情頁
        // 注意：歷史紀錄目前沒有存 link（外部購買連結），
        // 詳情頁會顯示「暫無購買連結」，其餘資訊（名稱、價格、圖片、標籤）正常顯示
        return GestureDetector(
          onTap: () => context.push(
            AppRoutes.product,
            extra: {
              'name': item['name'],
              'price': item['price'],
              'image': item['image'],
              'tags': tags,
              'platform': item['platform'],
              'link': '', // 歷史紀錄未儲存連結，先給空字串避免 key 不存在
            },
          ),
          child: Container(
          margin: const EdgeInsets.only(bottom: 12),
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: AppColors.cardBg(context),
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: AppColors.borderColor(context)),
          ),
          child: Row(
            children: [
              // 商品圖片：有圖顯示圖片，沒有或載入失敗顯示備用圖示
              Container(
                width: 52,
                height: 52,
                decoration: BoxDecoration(
                  color: AppColors.cardVariant(context),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(10),
                  child: (item['image'] != null &&
                          item['image'].toString().isNotEmpty)
                      ? Image.network(
                          AppFormatters.proxyImageUrl(item['image'].toString()),
                          headers: AppFormatters.imageHeaders,
                          fit: BoxFit.cover,
                          errorBuilder: (context, error, stackTrace) =>
                              const Icon(Icons.watch_rounded,
                                  color: AppColors.primary, size: 26),
                        )
                      : const Icon(Icons.watch_rounded,
                          color: AppColors.primary, size: 26),
                ),
              ),
              const SizedBox(width: 12),

              // 商品資訊
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(item['name']?.toString() ?? '',
                        style: AppTextStyles.bodyLarge.copyWith(
                          fontWeight: FontWeight.w600,
                          color: AppColors.textMain(context), fontSize: 15)),
                    const SizedBox(height: 4),
                    if (tags.isNotEmpty)
                      Text(
                        tags.take(3).join(' '),
                        style: AppTextStyles.caption
                            .copyWith(color: AppColors.accent),
                      ),
                    const SizedBox(height: 4),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        // price 是後端回傳的 int，統一用 AppFormatters 格式化
                        Text(AppFormatters.formatPrice(item['price']),
                            style: AppTextStyles.caption.copyWith(
                                color: AppColors.primary,
                                fontWeight: FontWeight.w600)),
                        Text(item['viewedAt']?.toString() ?? '',
                            style: AppTextStyles.caption),
                      ],
                    ),
                  ],
                ),
              ),
            ],
            ),
          ),
        );
      },
    );
  }

  // ── Tab 3：購物車 ──────────────────────────────────────
  // 已改用 CartProvider 讀取真實資料，不再使用 mock array。
  // 不提供結帳流程：每個商品改為「前往購買」跳轉外部電商平台，
  // 底部總金額也改成「預估總金額」純參考文字。
  Widget _buildCartTab() {
    final cartItems = ref.watch(cartProvider);

    if (cartItems.isEmpty) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.shopping_cart_outlined,
                size: 48, color: AppColors.textHint),
            const SizedBox(height: 12),
            Text('購物車是空的',
                style: AppTextStyles.bodyMedium
                    .copyWith(color: AppColors.textSub(context))),
          ],
        ),
      );
    }

    // 預估總金額（僅供參考，不是真正的結帳金額）
    final int estimatedTotal = cartItems.fold(0, (sum, item) {
      final price = item.price;
      final intPrice =
          price is int ? price : (price is double ? price.toInt() : 0);
      return sum + intPrice * item.qty;
    });

    return Column(
      children: [
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.fromLTRB(20, 20, 20, 0),
            itemCount: cartItems.length,
            itemBuilder: (context, index) {
              return _buildCartItemCard(cartItems[index]);
            },
          ),
        ),
        _buildCartFooter(estimatedTotal),
      ],
    );
  }

  /// 單一購物車商品卡片
  /// 點擊卡片可進入商品詳情頁（前往購買、數量按鈕不受影響，
  /// Flutter 手勢判定會優先由內層按鈕接收點擊事件）
  Widget _buildCartItemCard(CartItem item) {
    return GestureDetector(
      onTap: () => context.push(
        AppRoutes.product,
        extra: {
          'name': item.name,
          'price': item.price,
          'image': item.image,
          'tags': item.tags,
          'link': item.link,
          'platform': item.platform,
        },
      ),
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: AppColors.cardBg(context),
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: AppColors.borderColor(context)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                _buildCartItemImage(item),
                const SizedBox(width: 12),
                Expanded(child: _buildCartItemInfo(item)),
                _buildCartItemQtyControls(item),
              ],
            ),
            const SizedBox(height: 10),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: () =>
                    LaunchHelper.openProductLink(context, item.link),
                icon: const Icon(Icons.open_in_new_rounded, size: 16),
                label: const Text('前往購買'),
                style: OutlinedButton.styleFrom(
                  foregroundColor: AppColors.primary,
                  side: const BorderSide(color: AppColors.primary),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// 商品圖示
  Widget _buildCartItemImage(CartItem item) {
    return Container(
      width: 52,
      height: 52,
      decoration: BoxDecoration(
        color: AppColors.cardVariant(context),
        borderRadius: BorderRadius.circular(10),
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(10),
        child: item.image.isNotEmpty
            ? Image.network(
                AppFormatters.proxyImageUrl(item.image),
                fit: BoxFit.cover,
                errorBuilder: (context, error, stackTrace) => const Icon(
                    Icons.watch_rounded,
                    color: AppColors.primary,
                    size: 26),
              )
            : const Icon(Icons.watch_rounded,
                color: AppColors.primary, size: 26),
      ),
    );
  }

  /// 商品名稱、標籤、價格與來源平台
  Widget _buildCartItemInfo(CartItem item) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          item.name,
          style: AppTextStyles.bodyLarge.copyWith(
            fontWeight: FontWeight.w600,
            color: AppColors.textMain(context),
            fontSize: 15,
          ),
          maxLines: 2,
          overflow: TextOverflow.ellipsis,
        ),
        const SizedBox(height: 4),
        if (item.tags.isNotEmpty)
          Text(
            item.tags.take(3).join(' '),
            style: AppTextStyles.caption.copyWith(color: AppColors.accent),
          ),
        const SizedBox(height: 6),
        Row(
          children: [
            Text(
              AppFormatters.formatPrice(item.price),
              style: AppTextStyles.caption.copyWith(
                color: AppColors.primary,
                fontWeight: FontWeight.w600,
              ),
            ),
            if (item.platform.isNotEmpty)
              Text(
                ' · ${AppFormatters.formatPlatform(item.platform)}',
                style:
                    AppTextStyles.caption.copyWith(color: AppColors.textHint),
              ),
          ],
        ),
      ],
    );
  }

  /// 數量加減控制
  Widget _buildCartItemQtyControls(CartItem item) {
    return Row(
      children: [
        _QtyButton(
          icon: Icons.remove,
          onTap: () =>
              ref.read(cartProvider.notifier).updateQty(item.key, -1),
        ),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 10),
          child: Text(
            '${item.qty}',
            style: AppTextStyles.labelLarge.copyWith(
              color: AppColors.textMain(context),
            ),
          ),
        ),
        _QtyButton(
          icon: Icons.add,
          onTap: () => ref.read(cartProvider.notifier).updateQty(item.key, 1),
        ),
      ],
    );
  }

  /// 底部：預估總金額（僅供參考，不提供結帳）
  Widget _buildCartFooter(int estimatedTotal) {
    return Container(
      padding: const EdgeInsets.fromLTRB(20, 14, 20, 24),
      decoration: BoxDecoration(
        color: AppColors.cardBg(context),
        border:
            Border(top: BorderSide(color: AppColors.borderColor(context))),
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                '預估總金額（僅供參考）',
                style: AppTextStyles.bodyMedium
                    .copyWith(color: AppColors.textSub(context)),
              ),
              Text(
                AppFormatters.formatPrice(estimatedTotal),
                style: AppTextStyles.displayMedium
                    .copyWith(color: AppColors.primary, fontSize: 20),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            '實際金額請以各平台結帳頁面為準',
            style: AppTextStyles.caption.copyWith(color: AppColors.textHint),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}

/// 購物車數量加減按鈕
class _QtyButton extends StatelessWidget {
  final IconData icon;
  final VoidCallback onTap;

  const _QtyButton({required this.icon, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 28,
        height: 28,
        decoration: BoxDecoration(
          color: AppColors.cardVariant(context),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: AppColors.borderColor(context)),
        ),
        child: Icon(icon, size: 14, color: AppColors.textMain(context)),
      ),
    );
  }
}