import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../core/constants/app_colors.dart';
import '../../../core/constants/app_routes.dart';
import '../../../core/constants/app_text_styles.dart';
import '../../../shared/widgets/custom_button.dart';
import '../../../services/filter_service.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/providers/user_profile_provider.dart';

/// 篩選器資料模型
/// [question]    題目標題
/// [subtitle]    題目副標（提示文字）
/// [options]     選項列表
/// [multiSelect] 是否可複選
/// [maxSelect]   最多可選幾個（複選限制用）
class FilterQuestion {
  final String question;
  final String subtitle;
  final List<String> options;
  final bool multiSelect;
  final int? maxSelect;
  final bool isOptional; // 是否為選填題，可跳過不選

  const FilterQuestion({
    required this.question,
    required this.subtitle,
    required this.options,
    this.multiSelect = false,
    this.maxSelect,
    this.isOptional = false,
  });
}

class FilterScreen extends ConsumerStatefulWidget {
  const FilterScreen({super.key});

  @override
  ConsumerState<FilterScreen> createState() => _FilterScreenState();
}

class _FilterScreenState extends ConsumerState<FilterScreen> {
  // 目前顯示第幾題（0-based）
  int _currentPage = 0;

  // 每題的已選答案，key = 題目index，value = 已選選項的 Set
  final Map<int, Set<String>> _answers = {};

  bool _isLoading = false;

  // 8 題問卷資料
  final List<FilterQuestion> _questions = const [
    FilterQuestion(
      question: '您的使用情境是？',
      subtitle: '可複選多個選項',
      options: [
        '運動（跑步 / 健身 / 戶外）',
        '日常生活（看時間 / 通知）',
        '工作 / 商務（訊息 / 行事曆）',
        '健康管理（心率 / 睡眠）',
        '穿搭 / 外型',
      ],
      multiSelect: true,
    ),
    FilterQuestion(
      question: '需要哪些功能？',
      subtitle: '可複選多個選項',
      options: [
        'GPS（定位 / 路線）',
        '心率監測',
        '血氧（SpO2）',
        '心電圖（ECG）',
        '睡眠追蹤',
        '運動分析（卡路里 / VO2max）',
        '通知（LINE / 電話）',
        '通話功能',
        '行動支付',
        'AI 語音助理',
        'App 下載 / 擴充',
        '防水需求（游泳）',
      ],
      multiSelect: true,
    ),
    FilterQuestion(
      question: '希望多久充一次電？',
      subtitle: '請選擇一個選項',
      options: [
        '每天',
        '2 – 3 天一次',
        '5 – 7 天一次',
        '10 天以上',
      ],
      multiSelect: false,
    ),
    FilterQuestion(
      question: '您的預算是？',
      subtitle: '請選擇一個選項',
      options: [
        'NT\$1,000 – 5,000',
        'NT\$5,000 – 15,000',
        'NT\$15,000 – 30,000',
        'NT\$30,000 以上',
      ],
      multiSelect: false,
    ),
    FilterQuestion(
      question: '偏好的作業系統？',
      subtitle: '請選擇一個選項',
      options: [
        'iOS',
        'Android',
        '跨平台（皆可）',
      ],
      multiSelect: false,
    ),
    FilterQuestion(
      question: '偏好的裝置類型？',
      subtitle: '請選擇一個選項',
      options: [
        '手錶',
        '手環',
        '戒指',
        '其他',
      ],
      multiSelect: false,
    ),
    FilterQuestion(
      question: '偏好的外型風格？',
      subtitle: '請選擇一個選項',
      options: [
        '運動風',
        '商務正式',
        '時尚 / 穿搭',
        '簡約',
      ],
      multiSelect: false,
    ),
    FilterQuestion(
      question: '最在意哪些因素？',
      subtitle: '請選 2 – 3 個選項',
      options: [
        'GPS 精準度',
        '電池續航',
        '耐用性',
        '感測器精準',
        'AI 功能',
        '生態整合',
        '易讀性',
        '售後服務',
        '外型設計',
        '價格',
        '睡眠追蹤',
      ],
      multiSelect: true,
      maxSelect: 3,
    ),
    // 新增第 9 題：使用情境定位（可跳過不選）
    FilterQuestion(
      question: '這台裝置主要是？',
      subtitle: '請選擇一個選項（可跳過）',
      options: [
        '個人使用',
        '家庭共用',
        '要送禮',
      ],
      multiSelect: false,
      isOptional: true,
    ),
  ];

  // 取得目前題目
  FilterQuestion get _currentQuestion => _questions[_currentPage];

  // 取得目前題目的已選答案
  Set<String> get _currentAnswers => _answers[_currentPage] ?? {};

  // 是否為最後一題
  bool get _isLastPage => _currentPage == _questions.length - 1;

  // 進度百分比
  double get _progress => (_currentPage + 1) / _questions.length;

  /// 點擊選項邏輯
  void _onOptionTap(String option) {
    setState(() {
      final current = _answers[_currentPage] ?? {};

      if (_currentQuestion.multiSelect) {
        // 複選邏輯
        if (current.contains(option)) {
          // 已選 → 取消
          current.remove(option);
        } else {
          // 未選 → 檢查是否超過上限
          final max = _currentQuestion.maxSelect;
          if (max != null && current.length >= max) {
            // 超過上限，顯示提示
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('最多只能選 $max 個選項'),
                backgroundColor: AppColors.warning,
                duration: const Duration(seconds: 1),
              ),
            );
            return;
          }
          current.add(option);
        }
      } else {
        // 單選邏輯：清掉舊的，選新的
        current.clear();
        current.add(option);
      }

      _answers[_currentPage] = current;
    });
  }

  /// 下一題 / 完成
  void _onNext() {
    
    // Q8 複選至少選 2 個
    if (_currentQuestion.maxSelect != null &&
        _currentAnswers.isNotEmpty &&
        _currentAnswers.length < 2) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('請至少選擇 2 個選項，或不選則跳過'),
          backgroundColor: AppColors.error,
          duration: Duration(seconds: 1),
        ),
      );
      return;
    }

    if (_isLastPage) {
      // 全部完成，整理答案傳給推薦頁
      _onFinish();
    } else {
      setState(() => _currentPage++);
    }
  }

  /// 返回上一題或離開篩選頁
  /// 此方法同時被左上角箭頭按鈕、PopScope（物理返回鍵、iOS 右滑）呼叫
  /// 確保所有返回方式行為一致
  void _onBack() {
    if (_currentPage == 0) {
      // 第一題才真正離開 FilterScreen
      context.pop();
    } else {
      // 其他題回到上一題，保留已填答案
      setState(() => _currentPage--);
    }
  }

  /// 完成篩選，整理答案並跳到推薦頁
  Future<void> _onFinish() async {
    // 取得預算選項的完整字串
    final budgetString =
        (_answers[3] ?? {}).isNotEmpty ? _answers[3]!.first : '';

    // 初始化區間預設值 (0 ~ 999999 代表不限預算)
    int minPrice = 0;
    int maxPrice = 999999;

    // 完全比對選項字串，轉換成數字區間
    if (budgetString == 'NT\$30,000 以上') {
      minPrice = 30000;
      maxPrice = 999999;
    } else if (budgetString == 'NT\$15,000 – 30,000') {
      minPrice = 15000;
      maxPrice = 30000;
    } else if (budgetString == 'NT\$5,000 – 15,000') {
      minPrice = 5000;
      maxPrice = 15000;
    } else if (budgetString == 'NT\$1,000 – 5,000') {
      minPrice = 1000;
      maxPrice = 5000;
    }

    // 讀取「我的」頁面填寫的個人資訊（選填，沒填就是空字串）
    final profile = ref.read(userProfileProvider);

    // 抓取畫面選項，組裝成 JSON 結構傳給後端
    final filters = {
      "usage":
          (_answers[0] ?? {}).isNotEmpty ? _answers[0]!.first : "",
      "min_price": minPrice,
      "max_price": maxPrice,
      "features": (_answers[1] ?? {}).toList(),
      "battery":
          (_answers[2] ?? {}).isNotEmpty ? _answers[2]!.first : "",
      "os": (_answers[4] ?? {}).isNotEmpty ? _answers[4]!.first : "",
      "device_type":
          (_answers[5] ?? {}).isNotEmpty ? _answers[5]!.first : "",
      "style":
          (_answers[6] ?? {}).isNotEmpty ? _answers[6]!.first : "",
      "core_factors": (_answers[7] ?? {}).toList(),

      // 第 9 題：使用情境定位（選填）
      "usage_scope":
          (_answers[8] ?? {}).isNotEmpty ? _answers[8]!.first : "",

      // 合併個人資訊
      ...profile.toMap(),
    };

    // 傳遞給推薦頁，由推薦頁自行打 API
    context.go(
      AppRoutes.recommendation,
      extra: {'filters': filters, 'loading': true},
    );
  }

  @override
  Widget build(BuildContext context) {
    // ── PopScope：攔截所有系統層級的返回手勢 ──────────────
    //
    // 問題背景：
    //   Flutter 的 Scaffold 預設允許系統返回（Android 物理鍵、iOS 右滑），
    //   會直接 pop 整個 FilterScreen，跳過我們自訂的 _onBack() 邏輯。
    //   這會導致使用者填到第 5 題時，不小心滑到邊緣就整份問卷消失。
    //
    // PopScope 說明：
    //   canPop: false       → 告訴 Flutter「這個頁面現在不准直接 pop」
    //   onPopInvoked(false) → 系統嘗試 pop 但被攔截時觸發，交給 _onBack() 處理
    //   onPopInvoked(true)  → 實際發生 pop 時觸發（canPop:false 下不會出現）
    //
    // 注意：WillPopScope 在 Flutter 3.12+ 已 deprecated，改用 PopScope。
    // ─────────────────────────────────────────────────────
    return PopScope(
      canPop: false,
      onPopInvoked: (bool didPop) {
        // didPop = false：系統想 pop 但被攔截 → 交給自訂邏輯
        // didPop = true ：已經 pop 出去（canPop:false 下理論上不發生）
        if (!didPop) {
          _onBack();
        }
      },
      child: Scaffold(
        backgroundColor: AppColors.bg(context),
        body: SafeArea(
          child: Column(
            children: [
              // 頂部進度區（含返回箭頭、步驟數、進度條）
              _buildHeader(),

              // 選項列表（可捲動，Q2 選項較多）
              Expanded(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.symmetric(horizontal: 24),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const SizedBox(height: 8),

                      // 題目標題
                      Text(
                        _currentQuestion.question,
                        style: AppTextStyles.displayMedium.copyWith(
                          color: AppColors.textMain(context),
                        ),
                      ),
                      const SizedBox(height: 6),

                      // 題目副標
                      Text(
                        _currentQuestion.subtitle,
                        style: AppTextStyles.bodyMedium.copyWith(
                          color: AppColors.textMain(context),
                        ),
                      ),
                      const SizedBox(height: 24),

                      // 選項按鈕列表
                      ..._currentQuestion.options.map(
                        (option) => _buildOptionButton(option),
                      ),

                      const SizedBox(height: 24),
                    ],
                  ),
                ),
              ),

              // 底部「下一題 / 開始推薦」按鈕
              _buildBottomNav(),
            ],
          ),
        ),
      ),
    );
  }

  /// 頂部：返回箭頭 + 步驟數 + 進度條
  /// 返回箭頭呼叫 _onBack()，與 PopScope 行為完全一致
  Widget _buildHeader() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 12, 24, 16),
      child: Column(
        children: [
          Row(
            children: [
              // 返回按鈕：呼叫 _onBack()，與物理返回鍵行為相同
              IconButton(
                onPressed: _onBack,
                icon: Icon(
                  Icons.arrow_back_ios_new,
                  color: AppColors.textMain(context),
                  size: 18,
                ),
              ),

              // 步驟數（置中）
              Expanded(
                child: Text(
                  '${_currentPage + 1} / ${_questions.length}',
                  textAlign: TextAlign.center,
                  style: AppTextStyles.bodyMedium.copyWith(
                    fontWeight: FontWeight.w600,
                    color: AppColors.textMain(context),
                  ),
                ),
              ),

              // 右側佔位，讓步驟數視覺上置中
              const SizedBox(width: 48),
            ],
          ),
          const SizedBox(height: 10),

          // 進度條
          ClipRRect(
            borderRadius: BorderRadius.circular(2),
            child: LinearProgressIndicator(
              value: _progress,
              backgroundColor: AppColors.borderColor(context),
              valueColor:
                  const AlwaysStoppedAnimation<Color>(AppColors.primary),
              minHeight: 4,
            ),
          ),
        ],
      ),
    );
  }

  /// 單個選項按鈕
  /// 已選狀態：藍色邊框 + 淡藍底色
  /// 未選狀態：灰色邊框 + 卡片底色
  Widget _buildOptionButton(String option) {
    final isSelected = _currentAnswers.contains(option);

    return GestureDetector(
      onTap: () => _onOptionTap(option),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 150),
        margin: const EdgeInsets.only(bottom: 10),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        decoration: BoxDecoration(
          color: isSelected
              ? AppColors.primary.withOpacity(0.12)
              : AppColors.cardBg(context),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color:
                isSelected ? AppColors.primary : AppColors.borderColor(context),
            width: isSelected ? 1.5 : 1,
          ),
        ),
        child: Row(
          children: [
            // 選取指示器（複選：方框勾勾 / 單選：圓形）
            _buildIndicator(isSelected),
            const SizedBox(width: 12),

            // 選項文字
            Expanded(
              child: Text(
                option,
                style: AppTextStyles.bodyLarge.copyWith(
                  color: isSelected
                      ? AppColors.textMain(context)
                      : AppColors.textSub(context),
                  fontSize: 16,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// 複選用方框勾勾 / 單選用圓形指示器
  Widget _buildIndicator(bool isSelected) {
    if (_currentQuestion.multiSelect) {
      // 複選：方形 checkbox
      return AnimatedContainer(
        key: const ValueKey('checkbox_indicator'), // 與圓形指示器區分身分，避免跨題型動畫過渡
        duration: const Duration(milliseconds: 150),
        width: 20,
        height: 20,
        decoration: BoxDecoration(
          color: isSelected ? AppColors.primary : Colors.transparent,
          borderRadius: BorderRadius.circular(5),
          border: Border.all(
            color: isSelected
                ? AppColors.primary
                : AppColors.textPlaceholder(context),
            width: 1.5,
          ),
        ),
        child: isSelected
            ? const Icon(Icons.check, size: 13, color: Colors.white)
            : null,
      );
    } else {
      // 單選：圓形 radio
      return AnimatedContainer(
        key: const ValueKey('radio_indicator'), // 與方形指示器區分身分，避免跨題型動畫過渡
        duration: const Duration(milliseconds: 150),
        width: 20,
        height: 20,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          color: isSelected ? AppColors.primary : Colors.transparent,
          border: Border.all(
            color: isSelected
                ? AppColors.primary
                : AppColors.textPlaceholder(context),
            width: 1.5,
          ),
        ),
        child: isSelected
            ? const Center(
                child: CircleAvatar(
                  radius: 4,
                  backgroundColor: Colors.white,
                ),
              )
            : null,
      );
    }
  }

  /// 底部導覽按鈕：最後一題顯示「開始推薦」，其他顯示「下一題」
  Widget _buildBottomNav() {
  String label;
  if (_isLastPage) {
    label = '開始推薦';
  } else if (_currentAnswers.isEmpty) {
    label = '跳過';
  } else {
    label = '下一題';
  }

  return Container(
    padding: const EdgeInsets.fromLTRB(24, 12, 24, 24),
    decoration: BoxDecoration(
      color: AppColors.bg(context),
      border:
          Border(top: BorderSide(color: AppColors.borderColor(context))),
    ),
    child: CustomButton(
      label: label,
      onTap: _onNext,
      variant: ButtonVariant.primary,
    ),
  );
}
}