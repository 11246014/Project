import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/constants/app_colors.dart';
import '../../../core/constants/app_text_styles.dart';
import '../../../core/constants/app_formatters.dart';
import '../../../core/providers/cart_provider.dart';
import '../../../core/utils/launch_helper.dart';
import '../../../shared/widgets/custom_button.dart';
import '../../../shared/widgets/sponsored_badge.dart';

import '../../../core/providers/review_provider.dart';
import '../../../core/constants/app_routes.dart';
import 'package:go_router/go_router.dart';
import '../../community/widgets/review_submit_sheet.dart';  

/// 商品詳情頁
///
/// 資料來源說明：
/// 接收上一頁（首頁 / 篩選推薦 / AI 聊天）傳入的完整商品 Map，
/// 不另外呼叫 API。因為 match（符合度分數）、reason（推薦理由）
/// 只在當次搜尋/推薦當下有效，商品也沒有穩定的資料庫 ID 可供重新查詢。
///
/// 欄位完整度差異：
/// - 首頁（MySQL）來源的商品：沒有 match 分數，tags 可能是空的
/// - 篩選 / 聊天推薦來源的商品：欄位較完整
/// 因此每個區塊都先判斷資料是否存在，不存在就不顯示，避免顯示 0 或空字串。
class ProductDetailScreen extends ConsumerWidget {
  final Map<String, dynamic> product;

  const ProductDetailScreen({super.key, required this.product});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final String name = product['name']?.toString() ?? '未知商品';
    final String image = product['image']?.toString() ?? '';

    // 相容兩種資料來源：AI 推薦商品用 'desc'，首頁 DB 商品用 'description'
    final String desc = (product['desc']?.toString().isNotEmpty ?? false)
        ? product['desc'].toString()
        : (product['description']?.toString() ?? '');

    final String platform = product['platform']?.toString() ?? '';
    final String link = product['link']?.toString() ?? '';
    final List<String> tags =
        List<String>.from(product['tags'] ?? product['features'] ?? []);

    // AI 推薦商品才有 reason；DB 商品沒有時，用標籤組一句概略描述，
    // 避免「推薦理由」整區塊空白
    String reason = product['reason']?.toString() ?? '';
    if (reason.isEmpty && tags.isNotEmpty) {
      reason = '此商品具備 ${tags.take(3).join('、')} 等功能規格。';
    }

    // match 只有推薦來源的商品才有；用 is int 判斷來決定「符合度」區塊要不要顯示
    final int? match = product['match'] is int ? product['match'] as int : null;

    return Scaffold(
      backgroundColor: AppColors.bg(context),
      body: SafeArea(
        child: Column(
          children: [
            _buildHeader(context),
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildImage(context, image),
                    const SizedBox(height: 20),

                    // 商品名稱：詳情頁完整顯示，不像卡片會截斷
                    Text(
                      name,
                      style: AppTextStyles.displayMedium
                          .copyWith(color: AppColors.textMain(context)),
                    ),
                    const SizedBox(height: 8),

                    Text(
                      AppFormatters.formatPrice(product['price']),
                      style: AppTextStyles.displayMedium.copyWith(
                        color: AppColors.primary,
                        fontSize: 22,
                      ),
                    ),
                    const SizedBox(height: 12),

                    // 合作廠商推薦標籤：放在來源平台標籤之上，維持獨立一行
                    if (product['is_sponsored'] == true) ...[
                      const SponsoredBadge(),
                      const SizedBox(height: 8),
                    ],
                    if (platform.isNotEmpty) _buildSourceBadge(context, platform),
                    const SizedBox(height: 16),

                    if (tags.isNotEmpty) _buildTags(context, tags),

                    if (match != null) ...[
                      const SizedBox(height: 20),
                      _buildMatchScore(context, match),
                    ],

                    if (reason.isNotEmpty) ...[
                      const SizedBox(height: 20),
                      _buildReason(context, reason),
                    ],

                    if (desc.isNotEmpty) ...[
                      const SizedBox(height: 20),
                      _buildDescription(context, desc),
                    ],

                    if (product['id'] != null) ...[
                      const SizedBox(height: 20),
                      _buildCommunitySection(context, ref, product['id'] as int),
                    ],

                    const SizedBox(height: 28),

                    if (platform.isNotEmpty) _buildDisclaimer(context),
                    const SizedBox(height: 16),

                    // 前往購買：跳轉外部電商平台
                    CustomButton(
                      label: link.isEmpty ? '暫無購買連結' : '前往購買',
                      prefixIcon: Icons.open_in_new_rounded,
                      onTap: () => LaunchHelper.openProductLink(context, link),
                    ),
                    const SizedBox(height: 10),

                    // 加入購物車：寫入 CartProvider
                    CustomButton(
                      label: '加入購物車',
                      variant: ButtonVariant.outline,
                      onTap: () {
                        ref.read(cartProvider.notifier).addItem(product);
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: Text('已加入購物車：$name'),
                            backgroundColor: AppColors.success,
                            duration: const Duration(seconds: 1),
                          ),
                        );
                      },
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

  Widget _buildHeader(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(4, 8, 20, 12),
      decoration: BoxDecoration(
        color: AppColors.cardBg(context),
        border: Border(bottom: BorderSide(color: AppColors.borderColor(context))),
      ),
      child: Row(
        children: [
          IconButton(
            onPressed: () => Navigator.of(context).pop(),
            icon: Icon(Icons.arrow_back_ios_new,
                color: AppColors.textMain(context), size: 18),
          ),
          Text(
            '商品詳情',
            style: AppTextStyles.displayMedium
                .copyWith(fontSize: 16, color: AppColors.textMain(context)),
          ),
        ],
      ),
    );
  }

  /// 主圖，載入失敗時顯示備用圖示，避免整頁因為單一圖片壞掉
   /// 改為固定高度置中顯示，避免圖片過大佔滿整個螢幕
  Widget _buildImage(BuildContext context, String image) {
    return Center(
      child: Container(
        width: double.infinity,
        height: 240, // 固定高度，不再用 AspectRatio 撐滿寬度
        decoration: BoxDecoration(
          color: AppColors.cardVariant(context),
          borderRadius: BorderRadius.circular(16),
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(16),
          child: image.isNotEmpty
              ? Image.network(
                  AppFormatters.proxyImageUrl(image),
                  headers: AppFormatters.imageHeaders,
                  fit: BoxFit.contain, // 改用 contain，圖片不裁切、置中顯示
                  errorBuilder: (context, error, stackTrace) => Icon(
                    Icons.watch_rounded,
                    color: AppColors.primary,
                    size: 64,
                  ),
                )
              : Icon(Icons.watch_rounded, color: AppColors.primary, size: 64),
        ),
      ),
    );
  }

  Widget _buildSourceBadge(BuildContext context, String platform) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: AppColors.cardVariant(context),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: AppColors.borderColor(context)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.storefront_outlined, size: 14, color: AppColors.textSub(context)),
          const SizedBox(width: 6),
          Text(
            '資料來源：${AppFormatters.formatPlatform(platform)}',
            style: AppTextStyles.caption.copyWith(color: AppColors.textSub(context)),
          ),
        ],
      ),
    );
  }

  Widget _buildTags(BuildContext context, List<String> tags) {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: tags
          .map((tag) => Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                decoration: BoxDecoration(
                  color: AppColors.accent.withOpacity(0.12),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  tag,
                  style: AppTextStyles.caption.copyWith(color: AppColors.accent),
                ),
              ))
          .toList(),
    );
  }

  Widget _buildMatchScore(BuildContext context, int match) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppColors.cardVariant(context),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('與您需求的符合度',
                  style: AppTextStyles.bodyMedium.copyWith(color: AppColors.textSub(context))),
              Text('$match%',
                  style: AppTextStyles.bodyMedium
                      .copyWith(color: AppColors.success, fontWeight: FontWeight.w600)),
            ],
          ),
          const SizedBox(height: 8),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: match / 100,
              backgroundColor: AppColors.borderColor(context),
              valueColor: const AlwaysStoppedAnimation<Color>(AppColors.primary),
              minHeight: 6,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildReason(BuildContext context, String reason) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppColors.primary.withOpacity(0.06),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.primary.withOpacity(0.2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.smart_toy_outlined, color: AppColors.primary, size: 16),
              const SizedBox(width: 6),
              Text('推薦理由',
                  style: AppTextStyles.bodyMedium
                      .copyWith(color: AppColors.primary, fontWeight: FontWeight.w600)),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            reason,
            style: AppTextStyles.bodyMedium.copyWith(color: AppColors.textMain(context), height: 1.6),
          ),
        ],
      ),
    );
  }

  Widget _buildDescription(BuildContext context, String desc) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('商品描述',
            style: AppTextStyles.bodyMedium
                .copyWith(color: AppColors.textSub(context), fontWeight: FontWeight.w600)),
        const SizedBox(height: 8),
        Text(
          desc,
          // 後端尚未清洗此欄位（可能含促銷字眼），先限制行數避免顯示過多雜訊
          maxLines: 4,
          overflow: TextOverflow.ellipsis,
          style: AppTextStyles.bodyMedium.copyWith(color: AppColors.textSub(context), height: 1.6),
        ),
      ],
    );
  }

  Widget _buildDisclaimer(BuildContext context) {
    return Text(
      '商品資訊來自第三方電商平台，實際售價與庫存請以外部頁面為準',
      style: AppTextStyles.caption.copyWith(color: AppColors.textHint),
    );
  }

  Widget _buildCommunitySection(BuildContext context, WidgetRef ref, int productId) {
    final summaryAsync = ref.watch(reviewSummaryProvider(productId));

    return summaryAsync.when(
      loading: () => const Padding(
        padding: EdgeInsets.symmetric(vertical: 12),
        child: Center(child: CircularProgressIndicator(strokeWidth: 2)),
      ),
      error: (e, _) => const SizedBox(),  // 查詢失敗就整塊不顯示
      data: (summary) {
        final reviewCount = summary?['review_count'] ?? 0;

        if (summary == null || reviewCount == 0) {
          return _buildEmptyCommunityCard(context, ref, productId);
        }

        final positiveRatio = (summary['positive_ratio'] ?? 0.0) as num;
        final summaryText = summary['summary_text']?.toString();
        final topPros = (summary['top_pros']?.toString() ?? '')
            .split(',').where((s) => s.trim().isNotEmpty).toList();
        final topCons = (summary['top_cons']?.toString() ?? '')
            .split(',').where((s) => s.trim().isNotEmpty).toList();

        return Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: AppColors.cardVariant(context),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Text('社群評價', style: AppTextStyles.bodyMedium.copyWith(
                      fontWeight: FontWeight.w600, color: AppColors.textMain(context))),
                  const Spacer(),
                  Text('$reviewCount 則心得', style: AppTextStyles.caption
                      .copyWith(color: AppColors.textHint)),
                ],
              ),
              const SizedBox(height: 8),
              Text('好評率 ${(positiveRatio * 100).toStringAsFixed(0)}%',
                  style: AppTextStyles.bodyLarge.copyWith(
                      color: AppColors.primary, fontWeight: FontWeight.w700)),
              if (summaryText != null && summaryText.isNotEmpty) ...[
                const SizedBox(height: 8),
                Text(summaryText, style: AppTextStyles.bodyMedium
                    .copyWith(color: AppColors.textSub(context))),
              ],
              if (topPros.isNotEmpty) ...[
                const SizedBox(height: 8),
                Text('優點：${topPros.join(' ')}', style: AppTextStyles.caption),
              ],
              if (topCons.isNotEmpty) ...[
                const SizedBox(height: 4),
                Text('缺點：${topCons.join(' ')}', style: AppTextStyles.caption),
              ],
              const SizedBox(height: 12),
              Row(
                children: [
                  TextButton(
                    onPressed: () => _openReviewSubmitSheet(context, ref, productId: productId),
                    child: const Text('我要留言心得'),
                  ),
                  TextButton(
                    onPressed: () => context.push(
                      AppRoutes.productReviews,
                      extra: {
                        'productId': productId,
                        'productName': product['name']?.toString() ?? '',
                      },
                    ),
                    child: const Text('查看全部心得'),
                  ),
                ],
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildEmptyCommunityCard(BuildContext context, WidgetRef ref, int productId) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.cardVariant(context),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          Text('目前尚無社群心得，成為第一個分享的人吧',
              style: AppTextStyles.bodyMedium.copyWith(color: AppColors.textSub(context))),
          const SizedBox(height: 8),
          TextButton(
            onPressed: () => _openReviewSubmitSheet(context, ref, productId: productId),
            child: const Text('我要留言心得'),
          ),
        ],
      ),
    );
  }

  void _openReviewSubmitSheet(
    BuildContext context,
    WidgetRef ref, {
    required int productId,
  }) async {
    final success = await openReviewSubmitSheet(
      context,
      productId: productId,
      productName: product['name']?.toString(),
    );
    // 送出成功才重新查詢，避免使用者只是關掉表單也白打一次 API
    if (success == true) {
      ref.invalidate(reviewSummaryProvider(productId));
    }
  }
}