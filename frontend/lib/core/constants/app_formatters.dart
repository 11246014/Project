
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
}