import 'dart:async'; // Timer：重新寄送冷卻倒數
import 'package:dio/dio.dart'; // DioException：解析後端錯誤訊息
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../core/constants/app_colors.dart';
import '../../../core/constants/app_routes.dart';
import '../../../core/constants/app_text_styles.dart';
import '../../../shared/widgets/custom_button.dart';
import '../widgets/auth_text_field.dart';
import '../../../services/auth_service.dart';

class ForgotPasswordScreen extends StatefulWidget {
  const ForgotPasswordScreen({super.key});

  @override
  State<ForgotPasswordScreen> createState() => _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends State<ForgotPasswordScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _codeController = TextEditingController();     // 6 位數驗證碼
  final _passwordController = TextEditingController(); // 新密碼
  final _confirmController = TextEditingController();  // 確認新密碼
  bool _isLoading = false;

  /// 目前步驟：0 = 輸入 Email；1 = 輸入驗證碼＋新密碼
  int _step = 0;

  /// 重新寄送冷卻倒數（秒），0 代表可以重寄
  int _cooldown = 0;
  Timer? _cooldownTimer;
  static const int _resendSeconds = 60;

  @override
  void dispose() {
    _cooldownTimer?.cancel(); // 離開頁面一定要停掉計時器
    _emailController.dispose();
    _codeController.dispose();
    _passwordController.dispose();
    _confirmController.dispose();
    super.dispose();
  }

  /// 取出要顯示給使用者的錯誤訊息
  /// 後端錯誤格式：{"detail": "訊息"}（400 驗證碼錯誤或過期、429 太頻繁或嘗試過多）
  String _errorMessage(Object e) {
    if (e is DioException) {
      if (e.response == null) return '無法連線到伺服器，請檢查網路後再試';
      final data = e.response!.data;
      if (data is Map && data['detail'] is String) {
        return data['detail'] as String;
      }
      // 422（格式驗證失敗）的 detail 是 List，不直接顯示
      if (e.response!.statusCode == 422) return '格式不正確，請檢查輸入內容';
    }
    return '發生未預期的錯誤，請稍後再試';
  }

  void _showMessage(String msg, {required bool isError}) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(msg),
        backgroundColor: isError ? AppColors.error : AppColors.success,
      ),
    );
  }

  /// 啟動 60 秒重寄冷卻倒數
  void _startCooldown() {
    _cooldownTimer?.cancel();
    setState(() => _cooldown = _resendSeconds);
    _cooldownTimer = Timer.periodic(const Duration(seconds: 1), (t) {
      if (!mounted) {
        t.cancel();
        return;
      }
      setState(() => _cooldown--);
      if (_cooldown <= 0) t.cancel();
    });
  }

  /// 寄送驗證碼（第一步送出 / 第二步「重新寄送」共用）
  /// [fromStepOne] 為 true 時先驗證 Email 欄位；重新寄送時畫面上是第二步表單，不能驗證
  Future<void> _sendCode({bool fromStepOne = true}) async {
    if (fromStepOne && !_formKey.currentState!.validate()) return;
    setState(() => _isLoading = true);

    try {
      await AuthService.requestResetCode(_emailController.text.trim());
      if (!mounted) return;
      setState(() {
        _step = 1;
        _codeController.clear(); // 舊驗證碼作廢，清掉避免誤送
      });
      _startCooldown();
      _showMessage('若此 Email 已註冊，驗證碼已寄出（10 分鐘內有效）', isError: false);
    } catch (e) {
      if (mounted) _showMessage(_errorMessage(e), isError: true);
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  /// 第二步送出：驗證碼 + 新密碼
  Future<void> _handleReset() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _isLoading = true);

    try {
      await AuthService.resetPassword(
        _emailController.text.trim(),
        _codeController.text.trim(),
        _passwordController.text,
      );
      if (!mounted) return;
      _showMessage('密碼已重設，請使用新密碼登入', isError: false);
      context.go(AppRoutes.login); // 成功後導回登入頁
    } catch (e) {
      // 驗證碼錯誤或過期、嘗試過多等，都直接顯示後端訊息
      if (mounted) _showMessage(_errorMessage(e), isError: true);
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  /// 回到第一步（更換 Email）
  void _backToEmailStep() {
    _cooldownTimer?.cancel();
    setState(() {
      _step = 0;
      _cooldown = 0;
      _codeController.clear();
      _passwordController.clear();
      _confirmController.clear();
    });
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
            child: _step == 0 ? _buildFormView() : _buildResetView(),
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
            '輸入您的 Email，我們將寄送 6 位數驗證碼給您',
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
            label: '寄送驗證碼',
            onTap: _sendCode,
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

  /// 第二步：輸入驗證碼 + 新密碼（規則與註冊頁一致）
  Widget _buildResetView() {
    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(height: 20),

          // 返回上一步（更換 Email）
          IconButton(
            onPressed: _backToEmailStep,
            icon: Icon(
              Icons.arrow_back_ios_new,
              color: AppColors.textMain(context),
              size: 20,
            ),
          ),
          const SizedBox(height: 24),

          // 圖示
          Container(
            width: 56,
            height: 56,
            decoration: BoxDecoration(
              color: AppColors.primary.withOpacity(0.12),
              borderRadius: BorderRadius.circular(14),
            ),
            child: const Icon(Icons.mark_email_read_outlined,
                color: AppColors.primary, size: 28),
          ),
          const SizedBox(height: 24),

          Text('輸入驗證碼',
              style: AppTextStyles.displayLarge
                  .copyWith(color: AppColors.textMain(context))),
          const SizedBox(height: 8),
          Text(
            '驗證碼已寄至 ${_emailController.text.trim()}（10 分鐘內有效）\n若沒收到，請檢查垃圾郵件匣',
            style: AppTextStyles.bodyLarge
                .copyWith(color: AppColors.textMain(context)),
          ),
          const SizedBox(height: 32),

          // 驗證碼
          AuthTextField(
            label: '驗證碼',
            hint: '6 位數字',
            controller: _codeController,
            keyboardType: TextInputType.number,
            prefixIcon: Icons.pin_outlined,
            validator: (v) {
              if (v == null || v.trim().isEmpty) return '請輸入驗證碼';
              if (!RegExp(r'^\d{6}$').hasMatch(v.trim())) return '請輸入 6 位數字驗證碼';
              return null;
            },
          ),
          const SizedBox(height: 20),

          // 新密碼（與註冊頁相同規則）
          AuthTextField(
            label: '新密碼',
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

          // 確認新密碼
          AuthTextField(
            label: '確認新密碼',
            hint: '再輸入一次新密碼',
            controller: _confirmController,
            isPassword: true,
            prefixIcon: Icons.lock_outline,
            validator: (v) {
              if (v == null || v.isEmpty) return '請再次輸入密碼';
              if (v != _passwordController.text) return '兩次密碼不一致';
              return null;
            },
          ),
          const SizedBox(height: 32),

          // 重設密碼
          CustomButton(
            label: '重設密碼',
            onTap: _handleReset,
            isLoading: _isLoading,
          ),
          const SizedBox(height: 12),

          // 重新寄送（60 秒冷卻；冷卻中半透明且不可按）
          Opacity(
            opacity: _cooldown > 0 ? 0.5 : 1,
            child: CustomButton(
              label: _cooldown > 0
                  ? '重新寄送驗證碼（$_cooldown 秒）'
                  : '重新寄送驗證碼',
              onTap: (_cooldown > 0 || _isLoading)
                  ? null
                  : () => _sendCode(fromStepOne: false),
              variant: ButtonVariant.outline,
            ),
          ),
          const SizedBox(height: 12),

          // 返回登入
          CustomButton(
            label: '返回登入',
            onTap: () => context.go(AppRoutes.login),
            variant: ButtonVariant.ghost,
          ),
          const SizedBox(height: 40),
        ],
      ),
    );
  }
}
