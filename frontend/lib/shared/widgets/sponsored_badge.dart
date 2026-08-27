//
// 合作廠商推薦標籤
//
// 顯示條件：後端2 的 score_engine.py 在計算 final_score 時，
// 若商品品牌落在 sponsored_brands 合作名單中，
// 會在回傳的商品 JSON 多加一個欄位 is_sponsored = true。
//
// 重要：這個標籤只影響「顯示」，不影響：
// - 商品排序（後端已經照 final_score 排好，前端不用重排）
// - 商品客觀資訊（規格、價格、來源平台皆維持原樣）
//
// 使用方式：
//   if (product['is_sponsored'] == true) const SponsoredBadge(),

import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_text_styles.dart';

class SponsoredBadge extends StatelessWidget {
  const SponsoredBadge({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      // 讓標籤只佔文字本身的寬度，不會撐滿整行
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        gradient: AppColors.primaryGradient, // 沿用專案既有的電光藍漸層
        borderRadius: BorderRadius.circular(6),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(Icons.bolt_rounded, size: 12, color: Colors.white),
          const SizedBox(width: 2),
          Text(
            '推薦',
            style: AppTextStyles.caption.copyWith(
              color: Colors.white,
              fontWeight: FontWeight.w600,
              fontSize: 10,
            ),
          ),
        ],
      ),
    );
  }
}