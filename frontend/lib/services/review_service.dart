import '../core/constants/api_config.dart';
import '../core/utils/dio_client.dart';

/// 社群心得相關 API，對應後端1新增的4支API
class ReviewService {
  static final _dio = DioClient.create(ApiConfig.dbBaseUrl);

  /// 建立一則心得（星評必填，文字可留空）
  /// is_anonymous、is_seed 由後端處理，前端完全不用傳
  static Future<void> createReview({
    required int productId,
    required int rating,
    String content = '',
  }) async {
    await _dio.post('/reviews', data: {
      'product_id': productId,
      'rating': rating,
      'content': content,
    });
  }

  /// 社群動態牆用：取得所有商品的心得列表（分頁）
  static Future<List<Map<String, dynamic>>> getReviews({
    int limit = 20,
    int offset = 0,
  }) async {
    final res = await _dio.get('/reviews', queryParameters: {
      'limit': limit,
      'offset': offset,
    });
    return List<Map<String, dynamic>>.from(res.data['reviews'] ?? []);
  }

  /// 商品詳情頁「查看全部心得」用
  static Future<List<Map<String, dynamic>>> getProductReviews(int productId) async {
    final res = await _dio.get('/products/$productId/reviews');
    return List<Map<String, dynamic>>.from(res.data['reviews'] ?? []);
  }

  /// 商品詳情頁社群評價卡片用
  static Future<Map<String, dynamic>?> getProductReviewSummary(int productId) async {
    try {
      final res = await _dio.get('/products/$productId/review_summary');
      return Map<String, dynamic>.from(res.data ?? {});
    } catch (e) {
      return null;  // 查詢失敗（例如商品還沒有任何心得）就回傳 null
    }
  }
}