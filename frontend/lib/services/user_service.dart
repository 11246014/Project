import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../core/constants/api_config.dart';
import 'package:flutter/foundation.dart';

class UserService {
  static final _dio = Dio(BaseOptions(baseUrl: ApiConfig.dbBaseUrl));
  static const _storage = FlutterSecureStorage();

  /// 取得目前登入的使用者資訊
  /// 用存在 SecureStorage 裡的 token（目前是 email）去查詢
  static Future<Map<String, dynamic>> getMe() async {
    // 從安全儲存讀取 token（目前存的是 email）
    final token = await _storage.read(key: 'token');

    if (token == null) throw Exception('尚未登入');

    // 後端路由是 /me/{email}（路徑參數），不是查詢參數，兩者對不上會直接失敗
    final res = await _dio.get('/me/$token');

    return Map<String, dynamic>.from(res.data);
  }

  /// 更新使用者個人資訊（年齡層、職業、目前裝置）
  /// 對應後端1新增的 PUT /users/{email}/profile
  /// 用途：讓「我的」頁面填的個人資訊真的存進資料庫，
  /// 而不是只留在手機的暫時記憶體裡
  static Future<void> updateProfile({
    required String ageRange,
    required String occupation,
    required String currentDevice,
  }) async {
    // 先確認使用者有登入，沒有 token 就不用送了
    final token = await _storage.read(key: 'token');
    if (token == null) throw Exception('尚未登入');

    // 呼叫後端 API，把三個欄位送過去更新
    await _dio.put(
      '/users/$token/profile',
      data: {
        'age_range': ageRange,
        'occupation': occupation,
        'current_device': currentDevice,
      },
    );
  }
  /// 取得使用者的歷史紀錄（依時間新到舊，最多 20 筆）
  /// 對應後端1新增的 GET /history/{email}
  static Future<List<Map<String, dynamic>>> getHistory() async {
    final token = await _storage.read(key: 'token');
    if (token == null) throw Exception('尚未登入');

    final res = await _dio.get('/history/$token');
    return List<Map<String, dynamic>>.from(res.data);
  }

  /// 新增一筆歷史紀錄
  /// 對應後端1新增的 POST /history/{email}
  /// 用途：使用者看到 AI 推薦或篩選結果時呼叫，記錄「看過哪些商品」
  /// 失敗不影響主流程（不會讓推薦畫面因此壞掉），只記錄 log 方便除錯
  static Future<void> addHistory(Map<String, dynamic> product) async {
    final token = await _storage.read(key: 'token');
    if (token == null) return; // 未登入不記錄

    try {
      await _dio.post('/history/$token', data: {
        'name': product['name'] ?? '',
        'price': product['price'] ?? 0,
        'image': product['image'] ?? '',
        'tags': List<String>.from(
            product['tags'] ?? product['features'] ?? []),
        'rating': product['rating'] ?? 0,
        'platform': product['platform'] ?? '',
      });
    } catch (e) {
      debugPrint('新增歷史紀錄失敗：$e');
    }
  }
}
