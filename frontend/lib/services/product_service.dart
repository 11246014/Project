import 'package:dio/dio.dart';
import '../core/constants/api_config.dart';

class ProductService {
  static final _dio = Dio(BaseOptions(baseUrl: ApiConfig.dbBaseUrl));

  // 取得所有商品
  static Future<List<Map<String, dynamic>>> getProducts() async {
    final res = await _dio.get('/products');
    return List<Map<String, dynamic>>.from(res.data);
  }
}