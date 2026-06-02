import 'package:dio/dio.dart';
import '../core/constants/api_config.dart';

class AuthService {
  static final _dio = Dio(BaseOptions(baseUrl: ApiConfig.dbBaseUrl,));

  // 登入，回傳 Token
  static Future<String> login(String email, String password) async {
    final res = await _dio.post('/login', data: {
      'email': email,
      'password': password,
    });
    return res.data['access_token'];
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