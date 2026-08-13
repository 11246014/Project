import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../core/constants/api_config.dart';
import '../core/utils/dio_client.dart';
import 'package:flutter/foundation.dart';

class UserService {
  static final _dio = DioClient.create(ApiConfig.dbBaseUrl);
  static const _storage = FlutterSecureStorage();

  /// 取得目前登入的使用者資訊
  /// 用存在 SecureStorage 裡的 token（目前是 email）去查詢
  static Future<Map<String, dynamic>> getMe() async {
    final token = await _storage.read(key: 'token');

    if (token == null) throw Exception('尚未登入');

    final res = await _dio.get('/me/$token');

    return Map<String, dynamic>.from(res.data);
  }

  /// 更新使用者個人資訊（年齡層、職業、目前裝置）
  static Future<void> updateProfile({
    required String ageRange,
    required String occupation,
    required String currentDevice,
  }) async {
    final token = await _storage.read(key: 'token');
    if (token == null) throw Exception('尚未登入');

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
  static Future<List<Map<String, dynamic>>> getHistory() async {
    final token = await _storage.read(key: 'token');
    if (token == null) throw Exception('尚未登入');

    final res = await _dio.get('/history/$token');
    return List<Map<String, dynamic>>.from(res.data);
  }

  /// 新增一筆歷史紀錄
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