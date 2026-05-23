import 'package:flutter/material.dart';
import '../../../core/constants/app_colors.dart';
import '../../../core/constants/app_text_styles.dart';

/// 登入／註冊頁專用輸入框
/// [label]        欄位上方標籤文字
/// [hint]         輸入框內提示文字
/// [controller]   綁定的 TextEditingController
/// [isPassword]   是否為密碼欄位（true 時顯示眼睛圖示）
/// [keyboardType] 鍵盤類型，預設為一般文字
/// [validator]    表單驗證函式，回傳 null 代表驗證通過
/// [prefixIcon]   左側圖示（可選）
class AuthTextField extends StatefulWidget {
  final String label;
  final String hint;
  final TextEditingController controller;
  final bool isPassword;
  final TextInputType keyboardType;
  final String? Function(String?)? validator;
  final IconData? prefixIcon;

  const AuthTextField({
    super.key,
    required this.label,
    required this.hint,
    required this.controller,
    this.isPassword = false,
    this.keyboardType = TextInputType.text,
    this.validator,
    this.prefixIcon,
  });

  @override
  State<AuthTextField> createState() => _AuthTextFieldState();
}

class _AuthTextFieldState extends State<AuthTextField> {
  // 控制密碼是否顯示，預設隱藏
  bool _obscureText = true;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // 欄位標籤
        Text(
          widget.label,
          style: AppTextStyles.bodyMedium.copyWith(
            color: AppColors.textMain(context),
            fontWeight: FontWeight.w500,
          ),
        ),
        const SizedBox(height: 8),

        // 輸入框本體
        TextFormField(
          controller: widget.controller,
          // 密碼欄位才隱藏文字
          obscureText: widget.isPassword && _obscureText,
          keyboardType: widget.keyboardType,
          validator: widget.validator,
          style: AppTextStyles.bodyLarge.copyWith(
  color: AppColors.textMain(context),
),
          decoration: InputDecoration(
            hintText: widget.hint,

            // 左側圖示
            prefixIcon: widget.prefixIcon != null
                ? Icon(
                    widget.prefixIcon,
                    size: 18,
                    color: AppColors.textHint,
                  )
                : null,

            // 密碼欄位右側眼睛按鈕
            suffixIcon: widget.isPassword
                ? IconButton(
                    icon: Icon(
                      _obscureText
                          ? Icons.visibility_outlined
                          : Icons.visibility_off_outlined,
                      color: AppColors.textHint,
                      size: 18,
                    ),
                    onPressed: () => setState(
                      () => _obscureText = !_obscureText,
                    ),
                  )
                : null,
          ),
        ),
      ],
    );
  }
}