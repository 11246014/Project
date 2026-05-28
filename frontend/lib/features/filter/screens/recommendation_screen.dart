import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../core/constants/app_colors.dart';
import '../../../core/constants/app_routes.dart';
import '../../../core/constants/app_text_styles.dart';
import '../../../shared/widgets/custom_button.dart';

class RecommendationScreen extends StatelessWidget {
  // 從篩選器傳來的 AI 推薦結果
  final Map<String, dynamic> result;

  const RecommendationScreen({super.key, required this.result});

  // Mock 推薦商品（串接後從 result 取得）
  List<Map<String, dynamic>> get _products => [
    {
      'name': 'Garmin Fenix 7',
      'price': 'NT\$ 14,900',
      'tags': ['#GPS', '#續航14天', '#登山'],
      'rating': 4.7,
      'match': 94,
      'reason': '續航達 14 天，GPS 精準度業界頂尖，且在你的預算內。網路評測普遍好評耐用性。',
      'isTop': true,
    },
    {
      'name': 'Apple Watch Series 9',
      'price': 'NT\$ 12,900',
      'tags': ['#GPS', '#血氧', '#防水'],
      'rating': 4.8,
      'match': 78,
      'reason': '生態系完整，健康監測功能豐富，適合 iOS 用戶。',
      'isTop': false,
    },
    {
      'name': 'Samsung Galaxy Watch 6',
      'price': 'NT\$ 9,990',
      'tags': ['#血壓', '#睡眠', '#Android'],
      'rating': 4.5,
      'match': 65,
      'reason': '價格親民，Android 生態系整合佳，睡眠追蹤表現優異。',
      'isTop': false,
    },
  ];

  // AI 推薦摘要（串接後從 result['summary'] 取得）
  String get _summary =>
      result['summary'] as String? ??
      '根據你的需求，我從商城中找到 3 款最符合的手錶，並參考了最新的網路評測。';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bg(context),
      body: SafeArea(
        child: Column(
          children: [
            // 頂部標題列
            _buildHeader(context),
            // 內容
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // AI 推薦摘要
                    _buildAiSummary(context),
                    const SizedBox(height: 16),

                    // 推薦商品標題
                    Row(
                      children: [
                        Text(
                          '推薦商品',
                          style: AppTextStyles.bodyMedium.copyWith(
                            color: AppColors.textSub(context),
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        const SizedBox(width: 8),
                        // 商品數量 badge
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 8, vertical: 2),
                          decoration: BoxDecoration(
                            color: AppColors.primary,
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: Text(
                            '${_products.length} 款',
                            style: AppTextStyles.caption.copyWith(
                              color: Colors.white,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),

                    // 商品卡片列表
                    ..._products.map(
                      (product) => _buildProductCard(context, product),
                    ),

                    // 重新篩選按鈕
                    const SizedBox(height: 8),
                    CustomButton(
                      label: '重新篩選',
                      onTap: () => context.go(AppRoutes.filter),
                      variant: ButtonVariant.outline,
                    ),
                    const SizedBox(height: 8),
                    CustomButton(
                      label: '回到首頁',
                      onTap: () => context.go(AppRoutes.home),
                      variant: ButtonVariant.ghost,
                    ),
                    const SizedBox(height: 20),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// 頂部標題列
  Widget _buildHeader(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 12, 20, 12),
      decoration: BoxDecoration(
        color: AppColors.cardBg(context),
        border: Border(bottom: BorderSide(color: AppColors.borderColor(context))),
      ),
      child: Row(
        children: [
          // 返回按鈕
          IconButton(
            onPressed: () => context.go(AppRoutes.home),
            icon: Icon(
              Icons.arrow_back_ios_new,
              color: AppColors.textSub(context),
              size: 18,
            ),
          ),
          const SizedBox(width: 4),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                '為你推薦',
                style: AppTextStyles.displayMedium.copyWith(
                  fontSize: 16,
                  color: AppColors.textMain(context),
                ),
              ),
              Text(
                '根據您的需求篩選',
                style: AppTextStyles.caption.copyWith(
                  color: AppColors.textSub(context),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  /// AI 推薦摘要區塊
  Widget _buildAiSummary(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppColors.cardVariant(context),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.borderColor(context)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // AI 頭像
          Container(
            width: 28,
            height: 28,
            decoration: BoxDecoration(
              gradient: AppColors.primaryGradient,
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Icon(
              Icons.smart_toy_outlined,
              color: Colors.white,
              size: 14,
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'WearWise AI 分析',
                  style: AppTextStyles.caption.copyWith(
                    color: AppColors.textSub(context),
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  _summary,
                  style: AppTextStyles.bodyMedium.copyWith(
                    color: AppColors.textMain(context),
                    height: 1.6,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// 商品推薦卡片
  Widget _buildProductCard(
      BuildContext context, Map<String, dynamic> product) {
    final isTop = product['isTop'] as bool;
    final match = product['match'] as int;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: isTop
            ? AppColors.primary.withOpacity(0.06)
            : AppColors.cardBg(context),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: isTop ? AppColors.primary : AppColors.borderColor(context),
          width: isTop ? 1.5 : 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 最推薦 badge
          if (isTop) ...[
            Container(
              padding:
                  const EdgeInsets.symmetric(horizontal: 10, vertical: 3),
              decoration: BoxDecoration(
                gradient: AppColors.primaryGradient,
                borderRadius: BorderRadius.circular(10),
              ),
              child: Text(
                '最推薦',
                style: AppTextStyles.caption.copyWith(
                  color: Colors.white,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
            const SizedBox(height: 10),
          ],

          // 商品資訊列
          Row(
            children: [
              // 商品圖示
              Container(
                width: 52,
                height: 52,
                decoration: BoxDecoration(
                  color: AppColors.cardVariant(context),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Icon(
                  Icons.watch_rounded,
                  color: AppColors.primary,
                  size: 26,
                ),
              ),
              const SizedBox(width: 12),

              // 商品名稱、標籤、價格
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      product['name'],
                      style: AppTextStyles.bodyLarge.copyWith(
                        fontWeight: FontWeight.w600,
                        fontSize: 14,
                        color: AppColors.textMain(context),
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      (product['tags'] as List<String>).join(' '),
                      style: AppTextStyles.caption
                          .copyWith(color: AppColors.accent),
                    ),
                    const SizedBox(height: 4),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          product['price'],
                          style: AppTextStyles.labelLarge.copyWith(
                            color: AppColors.primary,
                            fontSize: 13,
                          ),
                        ),
                        Row(
                          children: [
                            const Icon(Icons.star_rounded,
                                color: AppColors.warning, size: 13),
                            const SizedBox(width: 2),
                            Text('${product['rating']}',
                                style: AppTextStyles.caption),
                          ],
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),

          // 符合度進度條
          Row(
            children: [
              Text(
                '符合度',
                style: AppTextStyles.caption
                    .copyWith(color: AppColors.textSub(context)),
              ),
              const Spacer(),
              Text(
                '$match%',
                style: AppTextStyles.caption.copyWith(
                  color: AppColors.success,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: match / 100,
              backgroundColor: AppColors.cardVariant(context),
              valueColor:
                  const AlwaysStoppedAnimation<Color>(AppColors.primary),
              minHeight: 6,
            ),
          ),
          const SizedBox(height: 10),

          // AI 推薦理由
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: AppColors.cardVariant(context),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              product['reason'],
              style: AppTextStyles.caption.copyWith(
                color: AppColors.textSub(context),
                height: 1.5,
              ),
            ),
          ),
          const SizedBox(height: 10),

          // 加入購物車按鈕
          CustomButton(
            label: '加入購物車',
            onTap: () {
              // TODO：加入購物車邏輯
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text('已加入購物車：${product['name']}'),
                  backgroundColor: AppColors.success,
                  duration: const Duration(seconds: 1),
                ),
              );
            },
            variant: isTop ? ButtonVariant.primary : ButtonVariant.outline,
          ),
        ],
      ),
    );
  }
}