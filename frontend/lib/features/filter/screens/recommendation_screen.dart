import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../core/constants/app_colors.dart';
import '../../../core/constants/app_routes.dart';
import '../../../core/constants/app_text_styles.dart';
import '../../../shared/widgets/custom_button.dart';
import '../../../core/constants/app_formatters.dart';
import '../../../services/filter_service.dart';

//  StatefulWidget，讓頁面自己打 API
class RecommendationScreen extends StatefulWidget {
  final Map<String, dynamic> result;

  const RecommendationScreen({super.key, required this.result});

  @override
  State<RecommendationScreen> createState() => _RecommendationScreenState();
}

class _RecommendationScreenState extends State<RecommendationScreen> {
  // 是否正在等待 AI 回應
  bool _isLoading = false;

  // AI 推薦摘要
  String _summary = '';

  // 推薦商品列表
  List<Map<String, dynamic>> _products = [];

  @override
  void initState() {
    super.initState();

    // 判斷是從篩選器跳過來（需要打 API）還是直接有結果
    if (widget.result['loading'] == true) {
      // 從篩選器跳過來，自己打 API
      _fetchRecommendation(widget.result['message'] as String);
    } else {
      // 直接有結果的情況（保留舊的進入方式相容性）
      _summary = widget.result['summary'] as String? ?? '';
      _products = List<Map<String, dynamic>>.from(
          widget.result['products'] ?? []);
    }
  }

  /// 打 API 取得推薦結果
  Future<void> _fetchRecommendation(String message) async {
    setState(() => _isLoading = true);

    try {
      final response = await FilterService.recommend(message);

      if (mounted) {
        setState(() {
          _summary = response['summary'] as String? ?? '';
          _products = List<Map<String, dynamic>>.from(
              response['products'] ?? []);
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isLoading = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: const Text('推薦失敗，請稍後再試'),
            backgroundColor: AppColors.error,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bg(context),
      body: SafeArea(
        child: Column(
          children: [
            // 頂部標題列
            _buildHeader(context),

            // 內容區域
            Expanded(
              child: _isLoading
                  // 等待時顯示 loading 畫面
                  ? Center(
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const CircularProgressIndicator(
                            color: AppColors.primary,
                          ),
                          const SizedBox(height: 16),
                          Text(
                            'AI 正在為你分析推薦中...',
                            style: AppTextStyles.bodyMedium.copyWith(
                              color: AppColors.textSub(context),
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            '需要一點時間，請稍候',
                            style: AppTextStyles.caption.copyWith(
                              color: AppColors.textSub(context),
                            ),
                          ),
                        ],
                      ),
                    )
                  // 有結果時顯示內容
                  : SingleChildScrollView(
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
                                  '${_products.take(3).length} 款',
                                  style: AppTextStyles.caption.copyWith(
                                    color: Colors.white,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 12),

                          // 商品卡片列表（最多3個）
                          ..._products
                              .take(3)
                              .map((product) =>
                                  _buildProductCard(context, product)),

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
        border:
            Border(bottom: BorderSide(color: AppColors.borderColor(context))),
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
                  // summary 是空的時顯示預設文字
                  _summary.isEmpty ? '已為你找到以下推薦商品' : _summary,
                  style: AppTextStyles.bodyMedium.copyWith(
                    color: AppColors.textMain(context),
                    height: 1.6,
                  ),
                  maxLines: 5,
                  overflow: TextOverflow.ellipsis,
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
    final isTop = product['isTop'] as bool? ?? false;
    final match = product['match'] as int? ?? 0;

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
              // 商品圖片
              Container(
                width: 52,
                height: 52,
                decoration: BoxDecoration(
                  color: AppColors.cardVariant(context),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(10),
                  child: (product['image'] != null &&
                          product['image'].toString().isNotEmpty)
                      ? Image.network(
                          product['image'].toString(),
                          fit: BoxFit.cover,
                          errorBuilder: (context, error, stackTrace) => Icon(
                            Icons.watch_rounded,
                            color: AppColors.primary,
                            size: 26,
                          ),
                        )
                      : Icon(
                          Icons.watch_rounded,
                          color: AppColors.primary,
                          size: 26,
                        ),
                ),
              ),
              const SizedBox(width: 12),

              // 商品名稱、標籤、價格
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      product['name'].toString(),
                      style: AppTextStyles.bodyLarge.copyWith(
                        fontWeight: FontWeight.w600,
                        fontSize: 14,
                        color: AppColors.textMain(context),
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      ((product['tags'] as List<dynamic>?) ?? [])
                          .take(3)
                          .map((e) => e.toString())
                          .join(' '),
                      style: AppTextStyles.caption
                          .copyWith(color: AppColors.accent),
                    ),
                    const SizedBox(height: 4),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          AppFormatters.formatPrice(product['price']),
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
              product['reason'].toString(),
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