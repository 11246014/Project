import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../core/constants/app_colors.dart';
import '../../../core/constants/app_text_styles.dart';
import '../../../core/constants/app_routes.dart';

class ReviewCard extends StatefulWidget {
  final Map<String, dynamic> review;
  const ReviewCard({super.key, required this.review});

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
                'image': widget.review['product_image'] ?? '',
              });
            },
            child: Text(productName, style: AppTextStyles.bodyMedium
                .copyWith(fontWeight: FontWeight.w600, color: AppColors.primary)),
          ),
          const SizedBox(height: 6),
          Text(rating > 0 && rating <= 3
              ? ['', '不滿意', '普通', '滿意'][rating] : '',
              style: AppTextStyles.caption),
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
}