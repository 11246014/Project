import 'package:dio/dio.dart';
import '../core/constants/api_config.dart';
import '../core/utils/dio_client.dart';

class AuthService {
  static final _dio = DioClient.create(ApiConfig.dbBaseUrl);

  // 登入，回傳 Token
  static Future<String> login(String email, String password) async {
    final res = await _dio.post('/login', data: {
      'email': email,
      'password': password,
    });
    // 後端回傳 email，就用 email 當作本地識別 token
    return res.data['email'] as String;
  }

  // 註冊
  static Future<void> register(String name, String email, String password) async {
    await _dio.post('/register', data: {
      'username': name,
      'email': email,
      'password': password,
    });
  }

  /// 申請重設密碼驗證碼
  /// 後端不論 Email 是否存在，回應一律相同（避免被拿來探測帳號）
  static Future<void> requestResetCode(String email) async {
    await _dio.post('/forgot-password', data: {'email': email});
  }

  /// 用驗證碼重設密碼
  /// 失敗時後端回 {"detail": "..."}，由畫面解析顯示
  static Future<void> resetPassword(
      String email, String code, String newPassword) async {
    await _dio.post('/reset-password', data: {
      'email': email,
      'code': code,
      'new_password': newPassword,
    });
  }
}