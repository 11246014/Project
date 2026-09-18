/// 畫出「一則心得」的卡片：商品名稱（可點擊跳轉商品詳情頁）、
/// 滿意度文字、心得內容（過長可展開/收起）、匿名與留言時間。
/// 用於社群動態牆（community_screen.dart）

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../core/constants/app_colors.dart';
import '../../../core/constants/app_text_styles.dart';
import '../../../core/constants/app_routes.dart';
import '../../../core/constants/app_formatters.dart';   // 新增：縮圖要用 proxyImageUrl / imageHeaders

class ReviewCard extends StatefulWidget {
  final Map<String, dynamic> review;
  final Map<int, Map<String, dynamic>> productsById; // 新增：完整商品資料（id → 商品Map）
  const ReviewCard({
    super.key,
    required this.review,
    this.productsById = const {},
  });

  @override
  State<ReviewCard> createState() => _ReviewCardState();
}

class _ReviewCardState extends State<ReviewCard> {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    final content = widget.review['content']?.toString() ?? '';
    final rating = widget.review['rating'] ?? 0;
    final productName = widget.review['product_name']?.toString() ?? '未知商品';
    final productImage = widget.review['product_image']?.toString() ?? '';   

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppColors.cardBg(context),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.borderColor(context)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 商品資訊列：獨立的 GestureDetector，點擊才會離開社群頁
          GestureDetector(
            onTap: () {
              final productId = widget.review['product_id'];
              if (productId == null) return;
              context.push(AppRoutes.product, extra: {
                'id': productId,
                'name': productName,
                'image': productImage,
              });
            },
            child: Row(
              children: [
                ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: productImage.isNotEmpty
                      ? Image.network(
                          AppFormatters.proxyImageUrl(productImage),
                          headers: AppFormatters.imageHeaders,
                          width: 36,
                          height: 36,
                          fit: BoxFit.cover,
                          errorBuilder: (_, __, ___) => _thumbPlaceholder(),
                        )
                      : _thumbPlaceholder(),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(productName, style: AppTextStyles.bodyMedium
                      .copyWith(fontWeight: FontWeight.w600, color: AppColors.primary)),
                ),
              ],
            ),
          ),
          const SizedBox(height: 6),
          if (rating > 0 && rating <= 3)
            Row(
              children: [
                ...List.generate(3, (i) => Icon(
                  i < rating ? Icons.star_rounded : Icons.star_border_rounded,
                  size: 16,
                  color: i < rating ? Colors.amber : AppColors.textHint,
                )),
                const SizedBox(width: 6),
                Text(['', '不滿意', '普通', '滿意'][rating], style: AppTextStyles.caption),
              ],
            ),
          if (content.isNotEmpty) ...[
            const SizedBox(height: 6),
            Text(
              content,
              maxLines: _expanded ? null : 3,
              overflow: _expanded ? TextOverflow.visible : TextOverflow.ellipsis,
              style: AppTextStyles.bodyMedium.copyWith(color: AppColors.textSub(context)),
            ),
            if (content.length > 60)
              GestureDetector(
                onTap: () => setState(() => _expanded = !_expanded),
                child: Text(
                  _expanded ? '收起' : '顯示更多 ▾',
                  style: AppTextStyles.caption.copyWith(color: AppColors.primary),
                ),
              ),
          ],
          const SizedBox(height: 4),
          Text('匿名 · ${widget.review['created_at'] ?? ''}',
              style: AppTextStyles.caption.copyWith(color: AppColors.textHint)),
        ],
      ),
    );
  }
  Widget _thumbPlaceholder() => Container(
  width: 36,
  height: 36,
  decoration: BoxDecoration(
    color: AppColors.cardVariant(context),
    borderRadius: BorderRadius.circular(8),
  ),
  child: Icon(Icons.watch_outlined, size: 18, color: AppColors.textHint),
);
}