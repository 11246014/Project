import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../core/constants/app_colors.dart';
import '../../../core/constants/app_routes.dart';
import '../../../core/constants/app_text_styles.dart';
import '../../../shared/widgets/custom_button.dart';
import '../widgets/auth_text_field.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;

  @override
  void dispose() {
    // 頁面銷毀時釋放 Controller，避免記憶體洩漏
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  /// 登入處理邏輯
  /// W2 串接 API 時只需替換此函式內容
  Future<void> _handleLogin() async {
    // 先執行表單驗證，未通過則直接返回
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    try {
      // TODO W2：替換為真實 API 呼叫
      // 例如：await AuthService.login(email, password);
      await Future.delayed(const Duration(seconds: 1)); // Mock 延遲

      // 登入成功，跳轉首頁
      if (mounted) context.go(AppRoutes.home);
    } catch (e) {
      // 登入失敗，顯示錯誤提示
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('登入失敗：$e'),
            backgroundColor: AppColors.error,
          ),
        );
      }
    } finally {
      // 無論成功或失敗都關閉載入狀態
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        // 背景漸層
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
                  const SizedBox(height: 60),

                  // 頂部品牌區塊
                  _buildHeader(),
                  const SizedBox(height: 48),

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
                  const SizedBox(height: 20),

                  // 密碼輸入框
                  AuthTextField(
                    label: '密碼',
                    hint: '請輸入密碼',
                    controller: _passwordController,
                    isPassword: true,
                    prefixIcon: Icons.lock_outline,
                    validator: (v) {
                      if (v == null || v.isEmpty) return '請輸入密碼';
                      if (v.length < 6) return '密碼至少 6 個字元';
                      return null;
                    },
                  ),
                  const SizedBox(height: 12),

                  // 忘記密碼連結
                  Align(
                    alignment: Alignment.centerRight,
                    child: TextButton(
                      onPressed: () {
                        // TODO：忘記密碼頁面
                      },
                      child: Text(
                        '忘記密碼？',
                        style: AppTextStyles.bodyMedium
                            .copyWith(color: AppColors.primary),
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),

                  // 登入按鈕
                  CustomButton(
                    label: '登入',
                    onTap: _handleLogin,
                    isLoading: _isLoading,
                  ),
                  const SizedBox(height: 16),

                  // 分隔線
                  _buildDivider(),
                  const SizedBox(height: 16),

                  // 前往註冊按鈕
                  CustomButton(
                    label: '還沒有帳號？立即註冊',
                    onTap: () => context.push(AppRoutes.register),
                    variant: ButtonVariant.outline,
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

  /// 頂部品牌 Logo + 標題
  Widget _buildHeader() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // App 品牌圖示
        Container(
          width: 52,
          height: 52,
          decoration: BoxDecoration(
            gradient: AppColors.primaryGradient,
            borderRadius: BorderRadius.circular(14),
            boxShadow: [
              BoxShadow(
                color: AppColors.primary.withOpacity(0.4),
                blurRadius: 20,
                offset: const Offset(0, 6),
              ),
            ],
          ),
          child: Image.asset('assets/images/LOGO.png', width: 26, height: 26), //LOGO
        ),
        const SizedBox(height: 24),
        Text('歡迎回來', style: AppTextStyles.displayLarge),
        const SizedBox(height: 8),
        Text(
          '登入以探索智慧穿戴裝置推薦',
          style: AppTextStyles.bodyMedium,
        ),
      ],
    );
  }

  /// 中間分隔線（或）
  Widget _buildDivider() {
    return Row(
      children: [
        Expanded(child: Divider(color: AppColors.border)),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 12),
          child: Text('或', style: AppTextStyles.caption),
        ),
        Expanded(child: Divider(color: AppColors.border)),
      ],
    );
  }
}