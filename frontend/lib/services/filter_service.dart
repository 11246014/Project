import 'package:dio/dio.dart';
import '../core/constants/api_config.dart';

class FilterService {
  static final _dio = Dio(BaseOptions(
    baseUrl: ApiConfig.aiBaseUrl,
    // Ollama 比較慢，timeout 設長一點
    connectTimeout: const Duration(seconds: 30),
    receiveTimeout: const Duration(minutes: 5),
  ));

  // 把問卷答案送給 AI，取得推薦商品
  static Future<Map<String, dynamic>> recommend(String message) async {
    final res = await _dio.post('/ai/recommend', data: {
      'message': message,
    });
    return res.data;
  }
}