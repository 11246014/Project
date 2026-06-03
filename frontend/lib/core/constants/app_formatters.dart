
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
}