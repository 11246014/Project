import 'package:dio/dio.dart';
import '../core/constants/api_config.dart';

class ProductService {
  static final _dio = Dio(BaseOptions(baseUrl: ApiConfig.dbBaseUrl));

  // 取得所有商品
  static Future<List<Map<String, dynamic>>> getProducts() async {
    final res = await _dio.get('/products');
    
    // 後端回傳：[{ "id": 1, "name": "...", "price": 2990, "description": "..." }]
    // 前端需要：{ "name", "price", "tags", "rating", "type" }
    final rawList = List<Map<String, dynamic>>.from(res.data);

    return rawList.map((item) => _mapProduct(item)).toList();
  }

  /// 把 Backend1 的商品格式轉換成前端顯示用的格式
  static Map<String, dynamic> _mapProduct(Map<String, dynamic> raw) {
    // 從 description 嘗試判斷商品類型（也可以之後讓後端加欄位）
    final desc = raw['description']?.toString() ?? '';
    final name = raw['name']?.toString() ?? '';

    // 簡易判斷商品類型（用商品名稱或描述關鍵字猜測）
    String type = '其他';
    if (name.contains('手錶') || desc.contains('手錶')) type = '手錶';
    if (name.contains('手環') || desc.contains('手環')) type = '手環';
    if (name.contains('戒指') || desc.contains('戒指')) type = '戒指';

    return {
      'id': raw['id'],
      'name': name,
      'price': raw['price'] ?? 0,   // 保留 int，顯示時再格式化
      'description': desc,
      'tags': _extractTags(desc),   // 從描述文字抽出標籤
      'rating': 0.0,                // Backend1 沒有評分，先給 0
      'type': type,                 // 給首頁 tag 篩選用
      'image': raw['image']?.toString() ?? '',
    };
  }

  /// 從 description 抽出簡易標籤
  static List<String> _extractTags(String description) {
    final tags = <String>[];
    final keywords = ['心率', 'GPS', '睡眠', '防水', '血氧', 'NFC', '運動'];
    for (final kw in keywords) {
      if (description.contains(kw)) tags.add('#$kw');
    }
    return tags;
  }
}