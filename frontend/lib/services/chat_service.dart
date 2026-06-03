import 'package:dio/dio.dart';
import '../core/constants/api_config.dart';

class ChatService {
  static final _dio = Dio(BaseOptions(
    baseUrl: ApiConfig.aiBaseUrl,
    connectTimeout: const Duration(seconds: 30),
    receiveTimeout: const Duration(minutes: 5),
  ));

  // 發送訊息給 AI（聊天室用）
  static Future<Map<String, dynamic>> sendMessage(String message) async {
    final res = await _dio.post('/ai/recommend', data: {
      'message': message,
    });
    return res.data;
  }
}