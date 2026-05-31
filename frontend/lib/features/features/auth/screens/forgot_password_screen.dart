import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../core/constants/app_colors.dart';
import '../../../core/constants/app_routes.dart';
import '../../../core/constants/app_text_styles.dart';
import '../../../shared/widgets/custom_button.dart';
import '../widgets/auth_text_field.dart';

class ForgotPasswordScreen extends StatefulWidget {
  const ForgotPasswordScreen({super.key});

  @override
  State<ForgotPasswordScreen> createState() => _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends State<ForgotPasswordScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  bool _isLoading = false;
  bool _isSent = false; // 是否已送出

  @override
  void dispose() {
    _emailController.dispose();
    super.dispose();
  }

  Future<void> _handleSubmit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _isLoading = true);

    try {
      // TODO W2：替換為真實 API 呼叫
      await Future.delayed(const Duration(seconds: 1));
      if (mounted) setState(() => _isSent = true);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('發送失敗：$e'),
            backgroundColor: AppColors.error,
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: AppColors.bgGradient(context),
        ),
        child: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 24),
            child: _isSent ? _buildSuccessView() : _buildFormView(),
          ),
        ),
      ),
    );
  }

  /// 表單畫面
  Widget _buildFormView() {
    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(height: 20),

          // 返回按鈕
          IconButton(
            onPressed: () => context.pop(),
            icon: Icon(
              Icons.arrow_back_ios_new,
              color: AppColors.textMain(context),
              size: 20,
            ),
          ),
          const SizedBox(height: 24),

          // Logo
          Container(
            width: 56,
            height: 56,
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: AppColors.borderColor(context), width: 1.5),
            ),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(12),
              child: Image.asset(
                'assets/images/LOGO.png',
                fit: BoxFit.contain,
              ),
            ),
          ),
          const SizedBox(height: 24),

          Text('忘記密碼', style: AppTextStyles.displayLarge.copyWith(color: AppColors.textMain(context))),
          const SizedBox(height: 8),
          Text(
            '輸入您的 Email，我們將發送重置連結給您',
            style: AppTextStyles.bodyLarge.copyWith(
  color: AppColors.textMain(context),
),
          ),
          const SizedBox(height: 40),

          // Email 輸入框
          AuthTextField(
            label: 'Email',
            hint: 'your@email.com',
            controller: _emailController,
            keyboardType: TextInputType.emailAddress,
            prefixIcon: Icons.email_outlined,
            validator: (v) {
              if (v == null || v.isEmpty) return '請輸入 Email';
              if (!v.contains('@')) return 'Email 格式錯誤';
              return null;
            },
          ),
          const SizedBox(height: 32),

          // 送出按鈕
          CustomButton(
            label: '發送重置連結',
            onTap: _handleSubmit,
            isLoading: _isLoading,
          ),
          const SizedBox(height: 16),

          // 返回登入
          CustomButton(
            label: '返回登入',
            onTap: () => context.go(AppRoutes.login),
            variant: ButtonVariant.ghost,
          ),
        ],
      ),
    );
  }

  /// 發送成功畫面
  Widget _buildSuccessView() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        const SizedBox(height: 100),

        // 成功圖示
        Container(
          width: 80,
          height: 80,
          decoration: BoxDecoration(
            color: AppColors.success.withOpacity(0.12),
            shape: BoxShape.circle,
          ),
          child: const Icon(
            Icons.mark_email_read_outlined,
            color: AppColors.success,
            size: 40,
          ),
        ),
        const SizedBox(height: 28),

        Text('已發送重置信！', style: AppTextStyles.displayLarge.copyWith(color: AppColors.textMain(context))),
        const SizedBox(height: 12),
        Text(
          '請檢查 ${_emailController.text} 的信箱\n並點擊信中的重置連結',
          style: AppTextStyles.bodyLarge.copyWith(
  color: AppColors.textMain(context),
),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 48),

        // 重新發送
        CustomButton(
          label: '重新發送',
          onTap: () => setState(() => _isSent = false),
          variant: ButtonVariant.outline,
        ),
        const SizedBox(height: 16),

        // 返回登入
        CustomButton(
          label: '返回登入',
          onTap: () => context.go(AppRoutes.login),
          variant: ButtonVariant.ghost,
        ),
      ],
    );
  }
}