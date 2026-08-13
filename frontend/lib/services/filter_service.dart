import '../core/constants/api_config.dart';
import '../core/utils/dio_client.dart';

class FilterService {
  static final _dio = DioClient.create(
    ApiConfig.aiBaseUrl,
    // Ollama 較慢，timeout設長一點 
    connectTimeout: const Duration(seconds: 30),
    receiveTimeout: const Duration(minutes: 5),
  );

  // 把整理好的問卷 Map (filters) 直接送給後端
  static Future<Map<String, dynamic>> recommend(Map<String, dynamic> filters) async {
    
    // 將 filters 當作 data 丟出去，後端收到的就會是完整的 JSON dict
    final res = await _dio.post('/products/filter', data: filters);
    
    return res.data;
  }
}