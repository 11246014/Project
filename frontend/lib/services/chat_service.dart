import 'package:dio/dio.dart';
import '../core/constants/api_config.dart';
import '../core/providers/user_profile_provider.dart';
import '../core/utils/dio_client.dart';

class ChatService {

  // 用裝置時間當簡易 session_id，每次開 App 重置
  static final String _sessionId =
      DateTime.now().millisecondsSinceEpoch.toString();

  static final _dio = DioClient.create(
    ApiConfig.aiBaseUrl,
    connectTimeout: const Duration(seconds: 30),
    receiveTimeout: const Duration(minutes: 5),
  );

  // 發送訊息給 AI（聊天室用）
  static Future<Map<String, dynamic>> sendMessage(
    String message, {
    UserProfile? profile,
  }) async {
    String finalMessage = message;
    Map<String, dynamic>? personaJson;

    // 若有個人資訊（皆為選填），組成背景描述附加在訊息前面
    // 同時額外組一份結構化 JSON，避免完全依賴 AI 從文字重新猜測
    if (profile != null && !profile.isEmpty) {
      final parts = <String>[];
      if (profile.ageRange.isNotEmpty) parts.add('年齡層${profile.ageRange}');
      if (profile.occupation.isNotEmpty) parts.add('職業為${profile.occupation}');
      if (profile.currentDevice.isNotEmpty) parts.add('目前正在使用${profile.currentDevice}');

      if (parts.isNotEmpty) {
        finalMessage = '[使用者背景：${parts.join('，')}]\n$message';
      }

      personaJson = {
        'age_range': profile.ageRange.isNotEmpty ? profile.ageRange : null,
        'occupation': profile.occupation.isNotEmpty ? profile.occupation : null,
        'current_device':
            profile.currentDevice.isNotEmpty ? profile.currentDevice : null,
      };
    }

    final res = await _dio.post('/ai/recommend', data: {
      'message': finalMessage,
      'session_id': _sessionId,
      if (personaJson != null) 'persona': personaJson,
    });
    return res.data;
  }
}