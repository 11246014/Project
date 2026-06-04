import 'package:dio/dio.dart';
import '../core/constants/api_config.dart';

class ChatService {

  // 用裝置時間當簡易 session_id，每次開 App 重置
  static final String _sessionId =
      DateTime.now().millisecondsSinceEpoch.toString();

  static final _dio = Dio(BaseOptions(
    baseUrl: ApiConfig.aiBaseUrl,
    connectTimeout: const Duration(seconds: 30),
    receiveTimeout: const Duration(minutes: 5),
  ));

  // 發送訊息給 AI（聊天室用）
  static Future<Map<String, dynamic>> sendMessage(String message) async {
    final res = await _dio.post('/ai/recommend', data: {
      'message': message,
      'session_id': _sessionId,
    });
    return res.data;
  }
}