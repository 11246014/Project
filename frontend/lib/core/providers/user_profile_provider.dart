import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'dart:async';
import '../../services/user_service.dart';
import 'package:flutter/foundation.dart';

/// 使用者個人資訊（只放穩定不常變的屬性）

class UserProfile {
  final String ageRange;
  final String occupation;
  final String currentDevice;

  const UserProfile({
    this.ageRange = '',
    this.occupation = '',
    this.currentDevice = '',
  });

  UserProfile copyWith({
    String? ageRange,
    String? occupation,
    String? currentDevice,
  }) {
    return UserProfile(
      ageRange: ageRange ?? this.ageRange,
      occupation: occupation ?? this.occupation,
      currentDevice: currentDevice ?? this.currentDevice,
    );
  }

  Map<String, dynamic> toMap() => {
        'age_range': ageRange,
        'occupation': occupation,
        'current_device': currentDevice,
      };

  bool get isEmpty =>
      ageRange.isEmpty && occupation.isEmpty && currentDevice.isEmpty;
}

class UserProfileNotifier extends StateNotifier<UserProfile> {
  UserProfileNotifier() : super(const UserProfile());

  // 用來實作 debounce：使用者停止輸入一段時間後才送出更新
  Timer? _debounce;

  /// 登出時呼叫：清空本地個人資訊
  /// 避免下一次登入（或換帳號）時，畫面還殘留著前一位使用者的資料
  void reset() {
    _debounce?.cancel();
    state = const UserProfile();
  }

  void updateAgeRange(String value) {
    state = state.copyWith(ageRange: value);
    _scheduleSync();
  }

  void updateOccupation(String value) {
    state = state.copyWith(occupation: value);
    _scheduleSync();
  }

  void updateCurrentDevice(String value) {
    state = state.copyWith(currentDevice: value);
    _scheduleSync();
  }

  /// 登入後呼叫：將後端已存的個人資訊寫入 Provider
  /// 不會觸發回寫 API，避免「讀取資料」又立刻「送出更新」的無意義請求
  void hydrate(Map<String, dynamic> data) {
    state = UserProfile(
      ageRange: data['age_range']?.toString() ?? '',
      occupation: data['occupation']?.toString() ?? '',
      currentDevice: data['current_device']?.toString() ?? '',
    );
  }

  /// Debounce 800ms 後才呼叫 API，避免使用者每打一個字就送一次請求
  void _scheduleSync() {
    _debounce?.cancel();
    _debounce = Timer(const Duration(milliseconds: 800), () async {
      try {
        await UserService.updateProfile(
          ageRange: state.ageRange,
          occupation: state.occupation,
          currentDevice: state.currentDevice,
        );
      } catch (e) {
        // 同步失敗不影響使用者操作，僅記錄方便除錯
        debugPrint('個人資訊同步失敗：$e');
      }
    });
  }

  @override
  void dispose() {
    _debounce?.cancel();
    super.dispose();
  }
}

final userProfileProvider =
    StateNotifierProvider<UserProfileNotifier, UserProfile>((ref) {
  return UserProfileNotifier();
});