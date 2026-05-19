import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../core/constants/app_colors.dart';
import '../../../core/constants/app_routes.dart';
import '../../../core/constants/app_text_styles.dart';
import '../../../features/profile/screens/profile_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(child: _buildBody()),
      bottomNavigationBar: _buildBottomNav(),
    );
  }

  /// 根據底部導覽列切換顯示的頁面內容
  Widget _buildBody() {
    switch (_currentIndex) {
      case 0:
        return const _HomeTab();
      case 1:
        // 點篩選 Tab 時跳到篩選頁面
        WidgetsBinding.instance.addPostFrameCallback((_) {
          context.push(AppRoutes.filter);
          setState(() => _currentIndex = 0);
        });
        return const _HomeTab();
      case 2:
        WidgetsBinding.instance.addPostFrameCallback((_) {
          context.push(AppRoutes.chat);
          setState(() => _currentIndex = 0);
        });
        return const _HomeTab();
      case 3:
        return const ProfileScreen();
      default:
        return const SizedBox();
    }
  }

  /// 尚未開發的頁面佔位顯示
  Widget _buildPlaceholder(String title, String subtitle, IconData icon) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 48, color: AppColors.textHint),
          const SizedBox(height: 16),
          Text(title, style: AppTextStyles.displayMedium),
          const SizedBox(height: 8),
          Text(subtitle, style: AppTextStyles.bodyMedium),
        ],
      ),
    );
  }

  /// 底部導覽列
  Widget _buildBottomNav() {
    const items = [
      _NavItem(icon: Icons.home_outlined,   activeIcon: Icons.home_rounded,   label: '首頁'),
      _NavItem(icon: Icons.tune_outlined,   activeIcon: Icons.tune_rounded,   label: '篩選'),
      _NavItem(icon: Icons.chat_outlined,   activeIcon: Icons.chat_rounded,   label: 'AI 助理'),
      _NavItem(icon: Icons.person_outlined, activeIcon: Icons.person_rounded, label: '我的'),
    ];

    return Container(
      decoration: BoxDecoration(
        color: AppColors.surface,
        border: Border(
          top: BorderSide(color: AppColors.border),
        ),
      ),
      child: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (i) => setState(() => _currentIndex = i),
        backgroundColor: Colors.transparent,
        elevation: 0,
        type: BottomNavigationBarType.fixed,
        selectedItemColor: AppColors.primary,
        unselectedItemColor: AppColors.textHint,
        selectedLabelStyle: AppTextStyles.caption.copyWith(
          color: AppColors.primary,
          fontWeight: FontWeight.w600,
        ),
        unselectedLabelStyle: AppTextStyles.caption,
        items: items
            .map((item) => BottomNavigationBarItem(
                  icon: Icon(item.icon, size: 22),
                  activeIcon: Icon(item.activeIcon, size: 22),
                  label: item.label,
                ))
            .toList(),
      ),
    );
  }
}

/// 首頁 Tab 內容
class _HomeTab extends StatefulWidget {
  const _HomeTab();

  @override
  State<_HomeTab> createState() => _HomeTabState();
}

class _HomeTabState extends State<_HomeTab> {
  int _selectedTagIndex = 0;

  // 快速篩選標籤（W2 串接後從 API 取得）
  final List<String> _tags = ['全部', '手錶', '手環', '戒指'];

  // Mock 商品資料（W2 串接 API 後替換）
  final List<Map<String, dynamic>> _mockProducts = [
    {
      'name': 'Apple Watch Series 9',
      'price': 'NT\$ 12,900',
      'tags': ['#血氧', '#GPS', '#防水'],
      'rating': 4.8,
    },
    {
      'name': 'Garmin Fenix 7',
      'price': 'NT\$ 18,500',
      'tags': ['#GPS', '#續航14天', '#登山'],
      'rating': 4.7,
    },
    {
      'name': 'Samsung Galaxy Watch 6',
      'price': 'NT\$ 9,990',
      'tags': ['#血壓', '#睡眠', '#Android'],
      'rating': 4.5,
    },
  ];

  @override
  Widget build(BuildContext context) {
    return CustomScrollView(
      slivers: [
        // 頂部問候區塊
        SliverToBoxAdapter(child: _buildGreeting()),

        // 橫向標籤列
        SliverToBoxAdapter(child: _buildTagsRow()),

        // 商品列表標題
        SliverToBoxAdapter(
          child: Padding(
            padding: const EdgeInsets.fromLTRB(20, 24, 20, 12),
            child: Text('為你推薦', style: AppTextStyles.displayMedium),
          ),
        ),

        // 商品卡片列表
        SliverList(
          delegate: SliverChildBuilderDelegate(
            (context, index) =>
                _ProductCard(product: _mockProducts[index]),
            childCount: _mockProducts.length,
          ),
        ),

        const SliverToBoxAdapter(child: SizedBox(height: 20)),
      ],
    );
  }

  Widget _buildGreeting() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 20, 20, 16),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('您好，使用者 👋', style: AppTextStyles.bodyMedium),
              const SizedBox(height: 4),
              Text('找到你的理想穿戴裝置',
                  style: AppTextStyles.displayMedium),
            ],
          ),
          // 通知鈴鐺
          Container(
            width: 42,
            height: 42,
            decoration: BoxDecoration(
              color: AppColors.surfaceVariant,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppColors.border),
            ),
            child: const Icon(
              Icons.notifications_outlined,
              color: AppColors.textSecondary,
              size: 20,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTagsRow() {
    return SizedBox(
      height: 40,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 20),
        itemCount: _tags.length,
        separatorBuilder: (_, __) => const SizedBox(width: 8),
        itemBuilder: (context, index) => GestureDetector(
          onTap: () => setState(() => _selectedTagIndex = index),
          child: _QuickTag(
            label: _tags[index],
            isSelected: _selectedTagIndex == index,
          ),
        ),
      ),
    );
  }
}

/// 快速篩選標籤元件
class _QuickTag extends StatelessWidget {
  final String label;
  final bool isSelected;

  const _QuickTag({required this.label, this.isSelected = false});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
      decoration: BoxDecoration(
        gradient: isSelected ? AppColors.primaryGradient : null,
        color: isSelected ? null : AppColors.surfaceVariant,
        borderRadius: BorderRadius.circular(20),
        border: isSelected ? null : Border.all(color: AppColors.border),
      ),
      child: Text(
        label,
        style: AppTextStyles.caption.copyWith(
          color: isSelected ? Colors.white : AppColors.textSecondary,
          fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
        ),
      ),
    );
  }
}

/// 商品卡片元件
class _ProductCard extends StatelessWidget {
  final Map<String, dynamic> product;

  const _ProductCard({required this.product});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.fromLTRB(20, 0, 20, 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.border),
      ),
      child: Row(
        children: [
          // 商品圖示佔位（W2 替換為真實圖片 Image.network）
          Container(
            width: 72,
            height: 72,
            decoration: BoxDecoration(
              color: AppColors.surfaceVariant,
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Icon(
              Icons.watch_rounded,
              color: AppColors.primary,
              size: 32,
            ),
          ),
          const SizedBox(width: 16),

          // 商品資訊
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // 商品名稱
                Text(
                  product['name'],
                  style: AppTextStyles.bodyLarge
                      .copyWith(fontWeight: FontWeight.w600),
                ),
                const SizedBox(height: 6),

                // 規格標籤
                Wrap(
                  spacing: 6,
                  children: (product['tags'] as List<String>)
                      .map((tag) => Text(
                            tag,
                            style: AppTextStyles.caption
                                .copyWith(color: AppColors.accent),
                          ))
                      .toList(),
                ),
                const SizedBox(height: 8),

                // 價格 + 評分
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      product['price'],
                      style: AppTextStyles.labelLarge
                          .copyWith(color: AppColors.primary),
                    ),
                    Row(
                      children: [
                        const Icon(Icons.star_rounded,
                            color: AppColors.warning, size: 14),
                        const SizedBox(width: 2),
                        Text(
                          '${product['rating']}',
                          style: AppTextStyles.caption,
                        ),
                      ],
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

/// 底部導覽列資料模型
class _NavItem {
  final IconData icon;
  final IconData activeIcon;
  final String label;

  const _NavItem({
    required this.icon,
    required this.activeIcon,
    required this.label,
  });
}