import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../services/review_service.dart';

/// 依 productId 查詢該商品的社群評價彙整摘要
final reviewSummaryProvider =
    FutureProvider.family<Map<String, dynamic>?, int>((ref, productId) async {
  return ReviewService.getProductReviewSummary(productId);
});