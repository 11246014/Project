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

class ProfileScreen extends ConsumerStatefulWidget {
  const ProfileScreen({super.key});

  @override
  ConsumerState<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends ConsumerState<ProfileScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  // 串接後從 API 取得
Map<String, dynamic> _user = {
  'name': '載入中...',
  'email': '',
  'avatar': null,
};

  // 偏好標籤選取狀態
  final Map<String, bool> _preferTags = {
    'GPS 精準度': true,
    '電池續航': false,
    '耐用性': false,
    '感測器精準': true,
    'AI 功能': false,
    '生態整合': false,
    '易讀性': false,
    '售後服務': false,
    '外型設計': true,
    '價格': false,
    '睡眠追蹤': false,
  };

  // Mock 歷史紀錄（W3 串接後從 API 取得）
  final List<Map<String, dynamic>> _history = [
    {
      'name': 'Apple Watch Series 9',
      'price': 'NT\$ 12,900',
      'tags': ['#血氧', '#GPS', '#防水'],
      'rating': 4.8,
      'viewedAt': '今天 14:32',
    },
    {
      'name': 'Garmin Fenix 7',
      'price': 'NT\$ 18,500',
      'tags': ['#GPS', '#續航14天', '#登山'],
      'rating': 4.7,
      'viewedAt': '今天 13:15',
    },
    {
      'name': 'Samsung Galaxy Watch 6',
      'price': 'NT\$ 9,990',
      'tags': ['#血壓', '#睡眠', '#Android'],
      'rating': 4.5,
      'viewedAt': '昨天 20:04',
    },
  ];

  // Mock 購物車（W3 串接後從 API 取得）
  final List<Map<String, dynamic>> _cartItems = [
    {
      'name': 'Apple Watch Series 9',
      'price': 12900,
      'tags': ['#血氧', '#GPS'],
      'qty': 1,
    },
    {
      'name': 'Garmin Fenix 7',
      'price': 18500,
      'tags': ['#GPS', '#續航14天'],
      'qty': 1,
    },
  ];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _loadUserInfo();
  }

  Future<void> _loadUserInfo() async {
  try {
    final user = await UserService.getMe();
    if (mounted) {
      setState(() {
        _user = {
          'name': user['username'] ?? '使用者',
          'email': user['email'] ?? '',
          'avatar': null,
        };
      });
    }
  } catch (e) {
    // 載入失敗就保留預設值，不影響畫面
    debugPrint('載入使用者資訊失敗：$e');
  }
}

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  /// 購物車總金額
  int get _cartTotal => _cartItems.fold(
        0,
        (sum, item) => sum + (item['price'] as int) * (item['qty'] as int),
      );

  /// 更新購物車數量
  void _updateQty(int index, int delta) {
    setState(() {
      final newQty = (_cartItems[index]['qty'] as int) + delta;
      if (newQty <= 0) {
        _cartItems.removeAt(index);
      } else {
        _cartItems[index]['qty'] = newQty;
      }
    });
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
          // 偏好標籤
          Text('我的偏好標籤', style: AppTextStyles.displayMedium.copyWith(
            fontSize: 16,
            color: AppColors.textMain(context))),
          const SizedBox(height: 6),
          Text('點選標籤調整你的推薦偏好', style: AppTextStyles.bodyMedium.copyWith(color: AppColors.textSub(context))),
          const SizedBox(height: 16),

          // 標籤選取區
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: _preferTags.entries.map((entry) {
              final isSelected = entry.value;
              return GestureDetector(
                onTap: () => setState(
                  () => _preferTags[entry.key] = !isSelected,
                ),
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 150),
                  padding: const EdgeInsets.symmetric(
                      horizontal: 14, vertical: 8),
                  decoration: BoxDecoration(
                    gradient: isSelected ? AppColors.primaryGradient : null,
                    color: isSelected ? null : AppColors.cardVariant(context),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(
                      color: isSelected
                          ? AppColors.primary
                          : AppColors.borderColor(context),
                    ),
                  ),
                  child: Text(
                    entry.key,
                    style: AppTextStyles.caption.copyWith(
                      color: isSelected
                          ? Colors.white
                          : AppColors.textMain(context),
                      fontWeight: isSelected
                          ? FontWeight.w600
                          : FontWeight.w400,
                    ),
                  ),
                ),
              );
            }).toList(),
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

    return ListView.builder(
      padding: const EdgeInsets.all(20),
      itemCount: _history.length,
      itemBuilder: (context, index) {
        final item = _history[index];
        return Container(
          margin: const EdgeInsets.only(bottom: 12),
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: AppColors.cardBg(context),
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: AppColors.borderColor(context)),
          ),
          child: Row(
            children: [
              // 商品圖示
              Container(
                width: 52,
                height: 52,
                decoration: BoxDecoration(
                  color: AppColors.cardVariant(context),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Icon(Icons.watch_rounded,
                    color: AppColors.primary, size: 26),
              ),
              const SizedBox(width: 12),

              // 商品資訊
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(item['name'],
                        style: AppTextStyles.bodyLarge.copyWith(
                          fontWeight: FontWeight.w600,
                          color: AppColors.textMain(context), fontSize: 15)),
                    const SizedBox(height: 4),
                    Text(
                      (item['tags'] as List<String>).join(' '),
                      style: AppTextStyles.caption
                          .copyWith(color: AppColors.accent),
                    ),
                    const SizedBox(height: 4),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(item['price'],
                            style: AppTextStyles.caption.copyWith(
                                color: AppColors.primary,
                                fontWeight: FontWeight.w600)),
                        Text(item['viewedAt'],
                            style: AppTextStyles.caption),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  // ── Tab 3：購物車 ──────────────────────────────────────
  Widget _buildCartTab() {
    if (_cartItems.isEmpty) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.shopping_cart_outlined,
                size: 48, color: AppColors.textHint),
            const SizedBox(height: 12),
            Text('購物車是空的', style: AppTextStyles.bodyMedium.copyWith(color: AppColors.textSub(context))),
          ],
        ),
      );
    }

    return Column(
      children: [
        // 商品列表
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.fromLTRB(20, 20, 20, 0),
            itemCount: _cartItems.length,
            itemBuilder: (context, index) {
              final item = _cartItems[index];
              return Container(
                margin: const EdgeInsets.only(bottom: 12),
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: AppColors.cardBg(context),
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: AppColors.borderColor(context)),
                ),
                child: Row(
                  children: [
                    // 商品圖示
                    Container(
                      width: 52,
                      height: 52,
                      decoration: BoxDecoration(
                        color: AppColors.cardVariant(context),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: const Icon(Icons.watch_rounded,
                          color: AppColors.primary, size: 26),
                    ),
                    const SizedBox(width: 12),

                    // 商品資訊
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(item['name'],
                              style: AppTextStyles.bodyLarge.copyWith(
                                  fontWeight: FontWeight.w600,
                                  color: AppColors.textMain(context), fontSize: 15)),
                          const SizedBox(height: 4),
                          Text(
                            (item['tags'] as List<String>).join(' '),
                            style: AppTextStyles.caption
                                .copyWith(color: AppColors.accent),
                          ),
                          const SizedBox(height: 6),
                          Text(
                            'NT\$ ${item['price']}',
                            style: AppTextStyles.caption.copyWith(
                                color: AppColors.primary,
                                fontWeight: FontWeight.w600),
                          ),
                        ],
                      ),
                    ),

                    // 數量控制
                    Row(
                      children: [
                        _QtyButton(
                          icon: Icons.remove,
                          onTap: () => _updateQty(index, -1),
                        ),
                        Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 10),
                          child: Text(
                            '${item['qty']}',
                            style: AppTextStyles.labelLarge.copyWith(
                              color: AppColors.textMain(context),
                            ),
                          ),
                        ),
                        _QtyButton(
                          icon: Icons.add,
                          onTap: () => _updateQty(index, 1),
                        ),
                      ],
                    ),
                  ],
                ),
              );
            },
          ),
        ),

        // 底部總價 + 結帳
        Container(
          padding: const EdgeInsets.fromLTRB(20, 14, 20, 24),
          decoration: BoxDecoration(
            color: AppColors.cardBg(context),
            border: Border(top: BorderSide(color: AppColors.borderColor(context))),
          ),
          child: Column(
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('總計', style: AppTextStyles.bodyLarge
                      .copyWith(fontWeight: FontWeight.w600,color: AppColors.textMain(context))),
                  Text(
                    'NT\$ $_cartTotal',
                    style: AppTextStyles.displayMedium
                        .copyWith(color: AppColors.primary, fontSize: 20),
                  ),
                ],
              ),
              const SizedBox(height: 14),
              CustomButton(
                label: '前往結帳',
                onTap: () {
                  // TODO：串接結帳流程
                },
              ),
            ],
          ),
        ),
      ],
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