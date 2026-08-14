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
}