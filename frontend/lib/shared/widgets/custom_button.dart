import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_text_styles.dart';

/// 按鈕樣式種類
enum ButtonVariant { primary, outline, ghost }

/// 全 App 共用按鈕元件
/// [label]     按鈕文字
/// [onTap]     點擊事件
/// [isLoading] 是否顯示載入動畫（防止重複點擊）
/// [variant]   按鈕樣式，預設為 primary
/// [prefixIcon] 按鈕左側圖示（可選）
class CustomButton extends StatelessWidget {
  final String label;
  final VoidCallback? onTap;
  final bool isLoading;
  final ButtonVariant variant;
  final IconData? prefixIcon;

  const CustomButton({
    super.key,
    required this.label,
    this.onTap,
    this.isLoading = false,
    this.variant = ButtonVariant.primary,
    this.prefixIcon,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      // 載入中時禁止點擊
      onTap: isLoading ? null : onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 150),
        width: double.infinity,
        height: 52,
        decoration: _buildDecoration(),
        child: Center(
          child: isLoading
              // 載入動畫
              ? const SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    color: Colors.white,
                  ),
                )
              // 正常狀態：圖示 + 文字
              : Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    if (prefixIcon != null) ...[
                      Icon(prefixIcon, size: 18, color: _textColor),
                      const SizedBox(width: 8),
                    ],
                    Text(
                      label,
                      style: AppTextStyles.labelLarge
                          .copyWith(color: _textColor),
                    ),
                  ],
                ),
        ),
      ),
    );
  }

  /// 根據 variant 決定外框樣式
  BoxDecoration _buildDecoration() {
    switch (variant) {
      case ButtonVariant.primary:
        return BoxDecoration(
          gradient: AppColors.primaryGradient,
          borderRadius: BorderRadius.circular(12),
          // 藍色光暈效果
          boxShadow: [
            BoxShadow(
              color: AppColors.primary.withOpacity(0.35),
              blurRadius: 16,
              offset: const Offset(0, 4),
            ),
          ],
        );
      case ButtonVariant.outline:
        return BoxDecoration(
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: AppColors.primary, width: 1.5),
        );
      case ButtonVariant.ghost:
        return BoxDecoration(
          borderRadius: BorderRadius.circular(12),
        );
    }
  }

  /// 根據 variant 決定文字顏色
  Color get _textColor {
    switch (variant) {
      case ButtonVariant.primary:
        return Colors.white;
      case ButtonVariant.outline:
        return AppColors.primary;
      case ButtonVariant.ghost:
        return AppColors.textSecondary;
    }
  }
}