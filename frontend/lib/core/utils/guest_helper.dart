import 'dart:convert';
import 'dart:math';
import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// 訪客模式工具
///
/// 設計：
/// - 訪客 token = "guest_" + 32 碼隨機十六進位字串（沒有 @，不會和真實 email 撞名）
/// - 判斷是否為訪客以「token 前綴」為準（唯一真相，不會和旗標不同步）
/// - 另外也寫入 'is_guest' 旗標，方便之後其他地方直接讀取
/// - 訪客的個人資料存在 SecureStorage（key: guest_profile），登出時 deleteAll 會一併清掉
class GuestHelper {
  GuestHelper._();

  static const _storage = FlutterSecureStorage();

  static const String tokenPrefix = 'guest_';
  static const String _kToken = 'token';
  static const String _kIsGuest = 'is_guest';
  static const String _kProfile = 'guest_profile';

  /// 給定 token 是否為訪客 token
  static bool isGuestToken(String? token) =>
      token != null && token.startsWith(tokenPrefix);

  /// 目前登入者是否為訪客
  static Future<bool> isGuest() async =>
      isGuestToken(await _storage.read(key: _kToken));

  /// 產生訪客 token：guest_ + 128 bit 隨機碼
  static String _generateToken() {
    final rnd = Random.secure();
    final hex = List<int>.generate(16, (_) => rnd.nextInt(256))
        .map((b) => b.toRadixString(16).padLeft(2, '0'))
        .join();
    return '$tokenPrefix$hex';
  }

  /// 以訪客身分登入：寫入 token 與 is_guest 旗標
  static Future<String> signInAsGuest() async {
    final token = _generateToken();
    await _storage.write(key: _kToken, value: token);
    await _storage.write(key: _kIsGuest, value: 'true');
    await _storage.delete(key: _kProfile); // 新訪客從乾淨狀態開始
    return token;
  }

  /// 讀取訪客本機個人資料（key 與後端 /me 回傳一致，方便直接 hydrate）
  static Future<Map<String, dynamic>> readGuestProfile() async {
    const empty = {'age_range': '', 'occupation': '', 'current_device': ''};
    try {
      final raw = await _storage.read(key: _kProfile);
      if (raw == null || raw.isEmpty) return {...empty};
      final m = Map<String, dynamic>.from(jsonDecode(raw) as Map);
      return {
        'age_range': m['age_range']?.toString() ?? '',
        'occupation': m['occupation']?.toString() ?? '',
        'current_device': m['current_device']?.toString() ?? '',
      };
    } catch (e) {
      debugPrint('讀取訪客個人資料失敗：$e');
      return {...empty};
    }
  }

  /// 儲存訪客本機個人資料
  static Future<void> saveGuestProfile({
    required String ageRange,
    required String occupation,
    required String currentDevice,
  }) async {
    await _storage.write(
      key: _kProfile,
      value: jsonEncode({
        'age_range': ageRange,
        'occupation': occupation,
        'current_device': currentDevice,
      }),
    );
  }
}
