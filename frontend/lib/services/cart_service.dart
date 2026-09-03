import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../core/constants/api_config.dart';
import '../core/utils/dio_client.dart';

/// 購物車雲端同步服務
///
/// 設計重點：
/// - 只收/送 Map<String, dynamic>，不直接依賴 CartItem 類別，
///   避免 cart_service.dart <-> cart_provider.dart 互相 import 造成循環依賴。
/// - 每個方法都自己去 SecureStorage 讀 token（比照 UserService 的寫法）。
///   雖然系統沒有訪客模式，理論上呼叫這裡時 token 一定存在，
///   但還是保留 null 檢查當作防呆（例如登入流程還沒完全跑完就被呼叫到）。
class CartService {
  static final _dio = DioClient.create(ApiConfig.dbBaseUrl);
  static const _storage = FlutterSecureStorage();

  /// 取得伺服器上的購物車清單
  static Future<List<Map<String, dynamic>>> getCart() async {
    final token = await _storage.read(key: 'token');
    if (token == null) return [];

    try {
      final res = await _dio.get('/cart/$token');
      return List<Map<String, dynamic>>.from(res.data);
    } catch (e) {
      debugPrint('取得購物車失敗：$e');
      return [];
    }
  }

  /// 新增／累加一項商品到雲端購物車
  static Future<void> addItem({
    required String name,
    required dynamic price,
    required String image,
    required List<String> tags,
    required String link,
    required String platform,
    int qty = 1,
  }) async {
    final token = await _storage.read(key: 'token');
    if (token == null) return;

    try {
      await _dio.post('/cart/$token', data: {
        'name': name,
        'price': price,
        'image': image,
        'tags': tags,
        'link': link,
        'platform': platform,
        'qty': qty,
      });
    } catch (e) {
      // 同步失敗不影響本地購物車操作，只記錄 log
      // （例如 ngrok 網址過期、暫時斷線等情況）
      debugPrint('購物車新增失敗：$e');
    }
  }

  /// 更新某商品的絕對數量；qty <= 0 由後端負責刪除該列
  static Future<void> updateQty({
    required String platform,
    required String name,
    required int qty,
  }) async {
    final token = await _storage.read(key: 'token');
    if (token == null) return;

    try {
      await _dio.put('/cart/$token/item', data: {
        'platform': platform,
        'name': name,
        'qty': qty,
      });
    } catch (e) {
      debugPrint('購物車更新數量失敗：$e');
    }
  }

  /// 刪除單一商品
  static Future<void> removeItem({
    required String platform,
    required String name,
  }) async {
    final token = await _storage.read(key: 'token');
    if (token == null) return;

    try {
      await _dio.delete(
        '/cart/$token/item',
        queryParameters: {'platform': platform, 'name': name},
      );
    } catch (e) {
      debugPrint('購物車刪除項目失敗：$e');
    }
  }

  /// 清空雲端購物車
  static Future<void> clearCart() async {
    final token = await _storage.read(key: 'token');
    if (token == null) return;

    try {
      await _dio.delete('/cart/$token');
    } catch (e) {
      debugPrint('購物車清空失敗：$e');
    }
  }
}