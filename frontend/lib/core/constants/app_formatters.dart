import 'package:flutter/foundation.dart' show kIsWeb;
import 'api_config.dart';

/// 全域格式化工具
class AppFormatters {
  AppFormatters._();

  /// 把 price（int 或 String）統一格式化成 "NT$ 2,990" 的顯示字串
  /// 後端回傳 int，這裡負責加千分位與貨幣符號
  static String formatPrice(dynamic price) {
    // 如果已經是格式化字串（例如 "NT$ 2,990"），直接回傳
    if (price is String) return price;

    // 如果是數字，轉成有千分位的格式
    if (price is int || price is double) {
      final intPrice = price.toInt();
      // 用 RegExp 加千分位逗號
      final formatted = intPrice
          .toString()
          .replaceAllMapped(
            RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'),
            (match) => '${match[1]},',
          );
      return 'NT\$ $formatted';
    }

    return 'NT\$ 0';
  }

  /// 把後端回傳的 platform 原始值，轉換成使用者看得懂的顯示文字
  ///
  /// 目前對照表是暫定版本，之後跟後端確認完整的 platform 清單後
  /// 要補齊；找不到對照的值會直接顯示原始字串，不會噴錯或顯示空白。
  static String formatPlatform(String platform) {
    // 商品本質上都是從外部電商平台抓取後存入資料庫，
    // 因此預設一律顯示原始平台名稱，不再標示「WearWise 精選」。
    // 只有真的沒有平台資訊時（意外情況），才顯示備用文字。
    if (platform.isEmpty) {
      return '外部電商平台';
    }

    const Map<String, String> mapping = {
      'momo': 'momo購物網',
      'PChome': 'PChome線上購物',
      '蝦皮': '蝦皮購物',
      'Yahoo購物': 'Yahoo購物中心',
    };
    return mapping[platform] ?? platform;
  }
  
  /// 將商品圖片網址轉換成後端代理網址（僅限 Web 版使用）
  ///
  /// 背景：
  /// Flutter Web 版的 CanvasKit 渲染器要求圖片來源提供 CORS header，
  /// 電商圖片伺服器大多不支援，導致 Image.network() 在 Web 版讀取失敗。
  /// 後端2提供 /image-proxy 端點代為抓取圖片並附上 CORS header，解決這個問題。
  ///
  /// 手機 App 版本沒有這個限制（沒有瀏覽器 CORS 規則），
  /// 直接用原始網址即可，這樣可以省去代理的額外延遲，
  /// 也不會讓後端多背負原本不需要的圖片轉發流量。
  static String proxyImageUrl(String originalUrl) {
    if (originalUrl.isEmpty) return '';

    // 非 http 開頭的網址（例如本機路徑或空值）不需要代理
    if (!originalUrl.startsWith('http')) return originalUrl;

    // 只有 Web 版才需要透過後端代理，App 版直接回傳原始網址
    if (!kIsWeb) return originalUrl;

    final encoded = Uri.encodeComponent(originalUrl);
    return '${ApiConfig.aiBaseUrl}/image-proxy?url=$encoded';
  }
}