import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../core/constants/api_config.dart';

class UserService {
  static final _dio = Dio(BaseOptions(baseUrl: ApiConfig.dbBaseUrl));
  static const _storage = FlutterSecureStorage();

  /// 取得目前登入的使用者資訊
  /// 用存在 SecureStorage 裡的 token（目前是 email）去查詢
  static Future<Map<String, dynamic>> getMe() async {
    // 從安全儲存讀取 token（目前存的是 email）
    final token = await _storage.read(key: 'token');

    if (token == null) throw Exception('尚未登入');

    final res = await _dio.get(
      '/me',
      queryParameters: {'email': token},
    );

    return Map<String, dynamic>.from(res.data);
  }
}