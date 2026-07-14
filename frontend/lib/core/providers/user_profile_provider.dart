import 'package:flutter_riverpod/flutter_riverpod.dart';

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

  void updateAgeRange(String value) => state = state.copyWith(ageRange: value);
  void updateOccupation(String value) => state = state.copyWith(occupation: value);
  void updateCurrentDevice(String value) => state = state.copyWith(currentDevice: value);
}

final userProfileProvider =
    StateNotifierProvider<UserProfileNotifier, UserProfile>((ref) {
  return UserProfileNotifier();
});