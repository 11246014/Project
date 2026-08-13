import 'package:dio/dio.dart';

/// 統一建立 Dio 實例的工具類別
///
/// 背景：
/// Flutter Web 版打 ngrok 免費版網址時，ngrok 會偵測到請求來自瀏覽器，
/// 先回傳一個 HTML 警告攔截頁（不是我們後端的 JSON 回應），
/// 導致 Dio 解析失敗，噴出 DioException [connection error]。
/// 這個問題只在 Web 上發生，App（手機）不受影響。
///
/// 解法：
/// 所有請求都加上 'ngrok-skip-browser-warning' header，
/// 告訴 ngrok 略過警告頁，直接把請求轉發給真正的後端。
///
/// 之後如果還要加其他全域設定（例如 log interceptor、
/// 統一的 401 重新登入處理），都只需要改這一個檔案。
class DioClient {
  DioClient._();

  /// 建立一個統一設定好的 Dio 實例
  static Dio create(
    String baseUrl, {
    Duration? connectTimeout,
    Duration? receiveTimeout,
  }) {
    return Dio(
      BaseOptions(
        baseUrl: baseUrl,
        connectTimeout: connectTimeout ?? const Duration(seconds: 30),
        receiveTimeout: receiveTimeout ?? const Duration(seconds: 30),
        headers: {
          // 讓 ngrok 免費版略過瀏覽器警告攔截頁
          'ngrok-skip-browser-warning': 'true',
        },
      ),
    );
  }
}