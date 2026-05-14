import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../core/constants/app_colors.dart';
import '../../../core/constants/app_routes.dart';
import '../../../core/constants/app_text_styles.dart';
import '../../../shared/widgets/custom_button.dart';
import '../widgets/auth_text_field.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmController = TextEditingController();
  bool _isLoading = false;

  @override
  void dispose() {
    // 頁面銷毀時釋放所有 Controller
    _nameController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _confirmController.dispose();
    super.dispose();
  }

  /// 註冊處理邏輯
  /// W2 串接 API 時只需替換此函式內容
  Future<void> _handleRegister() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    try {
      // TODO W2：替換為真實 API 呼叫
      // 例如：await AuthService.register(name, email, password);
      await Future.delayed(const Duration(seconds: 1)); // Mock 延遲

      if (mounted) {
        // 註冊成功提示
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('註冊成功！請登入'),
            backgroundColor: AppColors.success,
          ),
        );
        // 跳回登入頁
        context.go(AppRoutes.login);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('註冊失敗：$e'),
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
        decoration: const BoxDecoration(
          gradient: AppColors.backgroundGradient,
        ),
        child: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 24),
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const SizedBox(height: 20),

                  // 返回按鈕
                  IconButton(
                    onPressed: () => context.pop(),
                    icon: const Icon(
                      Icons.arrow_back_ios_new,
                      color: AppColors.textSecondary,
                      size: 20,
                    ),
                  ),
                  const SizedBox(height: 16),

                  // 頁面標題
                  Text('建立帳號', style: AppTextStyles.displayLarge),
                  const SizedBox(height: 8),
                  Text(
                    '加入 WearWise',
                    style: AppTextStyles.bodyMedium,
                  ),
                  const SizedBox(height: 40),

                  // 暱稱
                  AuthTextField(
                    label: '暱稱',
                    hint: '你想怎麼被稱呼？',
                    controller: _nameController,
                    prefixIcon: Icons.person_outline,
                    validator: (v) =>
                        (v == null || v.isEmpty) ? '請輸入暱稱' : null,
                  ),
                  const SizedBox(height: 20),

                  // Email
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
                  const SizedBox(height: 20),

                  // 密碼
                  AuthTextField(
                    label: '密碼',
                    hint: '至少 6 個字元',
                    controller: _passwordController,
                    isPassword: true,
                    prefixIcon: Icons.lock_outline,
                    validator: (v) {
                      if (v == null || v.isEmpty) return '請輸入密碼';
                      if (v.length < 6) return '密碼至少 6 個字元';
                      return null;
                    },
                  ),
                  const SizedBox(height: 20),

                  // 確認密碼
                  AuthTextField(
                    label: '確認密碼',
                    hint: '再輸入一次密碼',
                    controller: _confirmController,
                    isPassword: true,
                    prefixIcon: Icons.lock_outline,
                    validator: (v) {
                      if (v == null || v.isEmpty) return '請再次輸入密碼';
                      // 比對兩次密碼是否一致
                      if (v != _passwordController.text) return '兩次密碼不一致';
                      return null;
                    },
                  ),
                  const SizedBox(height: 32),

                  // 註冊按鈕
                  CustomButton(
                    label: '立即註冊',
                    onTap: _handleRegister,
                    isLoading: _isLoading,
                  ),
                  const SizedBox(height: 12),

                  // 返回登入
                  CustomButton(
                    label: '已有帳號？返回登入',
                    onTap: () => context.go(AppRoutes.login),
                    variant: ButtonVariant.ghost,
                  ),
                  const SizedBox(height: 40),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}