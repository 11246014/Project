import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../constants/app_colors.dart';

/// 外部連結開啟工具
///
/// 統一處理商品連結跳轉，並針對以下情況做防呆：
/// 1. link 是空字串（例如首頁 MySQL 來源的商品，後端尚未補上 link 欄位前會發生）
/// 2. link 格式不是合法網址（SerpAPI 偶爾會回傳異常資料）
/// 3. 裝置沒有瀏覽器或無法開啟該連結
class LaunchHelper {
  LaunchHelper._();

  /// 嘗試開啟商品的外部購買連結
  /// 任何失敗情況都用 SnackBar 提示使用者，不會讓 App 崩潰或無反應
  static Future<void> openProductLink(
    BuildContext context,
    String? link,
  ) async {
    // 情況 1：連結是空的
    if (link == null || link.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('此商品暫無外部購買連結'),
          backgroundColor: AppColors.warning,
        ),
      );
      return;
    }

    final uri = Uri.tryParse(link);

    // 情況 2：格式不合法
    if (uri == null || !uri.hasScheme) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('商品連結格式異常，暫時無法開啟'),
          backgroundColor: AppColors.warning,
        ),
      );
      return;
    }

    // 情況 3：開啟失敗（裝置環境問題）
    final success = await launchUrl(uri, mode: LaunchMode.externalApplication);

    if (!success && context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('無法開啟外部連結，請稍後再試'),
          backgroundColor: AppColors.error,
        ),
      );
    }
  }
}