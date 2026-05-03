import 'package:flutter/material.dart';
import '../../../core/constants/app_colors.dart';
import '../../../core/constants/app_text_styles.dart';

/// 訊息角色
enum MessageRole { user, ai }

/// 訊息資料模型
class ChatMessage {
  final String content;
  final MessageRole role;
  final DateTime time;
  final List<Map<String, dynamic>>? products; // AI 推薦的商品（可選）

  const ChatMessage({
    required this.content,
    required this.role,
    required this.time,
    this.products,
  });
}

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _inputController = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  // 是否正在等待 AI 回應
  bool _isLoading = false;

  // 對話紀錄
  final List<ChatMessage> _messages = [
    ChatMessage(
      content: '你好！我是 WearAI 助理，請告訴我你想找什麼樣的穿戴裝置？\n\n你可以直接描述需求，例如：「我想找續航力強、有 GPS 的運動手錶，預算 15,000 以內」',
      role: MessageRole.ai,
      time: DateTime.now(),
    ),
  ];

  @override
  void dispose() {
    _inputController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  /// 捲動到最底部
  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  /// 送出訊息
  Future<void> _sendMessage() async {
    final text = _inputController.text.trim();
    if (text.isEmpty || _isLoading) return;

    // 新增使用者訊息
    setState(() {
      _messages.add(ChatMessage(
        content: text,
        role: MessageRole.user,
        time: DateTime.now(),
      ));
      _isLoading = true;
      _inputController.clear();
    });

    _scrollToBottom();

    try {
      // TODO W3：替換為真實 AI API 呼叫
      // 例如：final response = await ChatService.sendMessage(text);
      await Future.delayed(const Duration(seconds: 2)); // Mock 延遲

      // Mock AI 回應
      if (mounted) {
        setState(() {
          _messages.add(ChatMessage(
            content: '根據您的需求，我幫您找到以下幾款適合的穿戴裝置，供您參考：',
            role: MessageRole.ai,
            time: DateTime.now(),
            // Mock 商品資料（W3 串接後從 API 取得）
            products: [
              {
                'name': 'Garmin Fenix 7',
                'price': 'NT\$ 18,500',
                'tags': ['#GPS', '#續航14天', '#登山'],
                'rating': 4.7,
              },
              {
                'name': 'Apple Watch Series 9',
                'price': 'NT\$ 12,900',
                'tags': ['#血氧', '#GPS', '#防水'],
                'rating': 4.8,
              },
            ],
          ));
          _isLoading = false;
        });
        _scrollToBottom();
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _messages.add(ChatMessage(
            content: '抱歉，目前無法取得回應，請稍後再試。',
            role: MessageRole.ai,
            time: DateTime.now(),
          ));
          _isLoading = false;
        });
        _scrollToBottom();
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      // 頂部 AppBar
      appBar: _buildAppBar(),
      body: Column(
        children: [
          // 對話訊息列表
          Expanded(child: _buildMessageList()),
          // 打字中提示
          if (_isLoading) _buildTypingIndicator(),
          // 輸入框
          _buildInputBar(),
        ],
      ),
    );
  }

  /// 頂部導覽列
  PreferredSizeWidget _buildAppBar() {
    return AppBar(
      backgroundColor: AppColors.surface,
      elevation: 0,
      leading: IconButton(
        onPressed: () => Navigator.of(context).pop(),
        icon: const Icon(
          Icons.arrow_back_ios_new,
          color: AppColors.textSecondary,
          size: 18,
        ),
      ),
      title: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          // AI 頭像
          Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              gradient: AppColors.primaryGradient,
              borderRadius: BorderRadius.circular(10),
            ),
            child: const Icon(
              Icons.smart_toy_outlined,
              color: Colors.white,
              size: 16,
            ),
          ),
          const SizedBox(width: 10),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('WearAI 助理',
                  style: AppTextStyles.labelLarge.copyWith(fontSize: 14)),
              Text('線上服務中',
                  style: AppTextStyles.caption
                      .copyWith(color: AppColors.success)),
            ],
          ),
        ],
      ),
      centerTitle: false,
      bottom: PreferredSize(
        preferredSize: const Size.fromHeight(1),
        child: Container(height: 1, color: AppColors.border),
      ),
    );
  }

  /// 訊息列表
  Widget _buildMessageList() {
    return ListView.builder(
      controller: _scrollController,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      itemCount: _messages.length,
      itemBuilder: (context, index) {
        final message = _messages[index];
        return message.role == MessageRole.ai
            ? _buildAiBubble(message)
            : _buildUserBubble(message);
      },
    );
  }

  /// AI 氣泡（左側）
  Widget _buildAiBubble(ChatMessage message) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          // AI 頭像
          Container(
            width: 28,
            height: 28,
            decoration: BoxDecoration(
              gradient: AppColors.primaryGradient,
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Icon(
              Icons.smart_toy_outlined,
              color: Colors.white,
              size: 14,
            ),
          ),
          const SizedBox(width: 8),

          // 訊息內容
          Flexible(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // 文字氣泡
                Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 14, vertical: 10),
                  decoration: BoxDecoration(
                    color: AppColors.surfaceVariant,
                    borderRadius: const BorderRadius.only(
                      topLeft: Radius.circular(16),
                      topRight: Radius.circular(16),
                      bottomRight: Radius.circular(16),
                      bottomLeft: Radius.circular(2),
                    ),
                    border: Border.all(color: AppColors.border),
                  ),
                  child: Text(
                    message.content,
                    style: AppTextStyles.bodyMedium
                        .copyWith(color: AppColors.textPrimary),
                  ),
                ),

                // 商品推薦卡片（如果有）
                if (message.products != null) ...[
                  const SizedBox(height: 8),
                  ...message.products!.map(
                    (product) => _buildProductCard(product),
                  ),
                ],

                // 時間戳記
                const SizedBox(height: 4),
                Text(
                  _formatTime(message.time),
                  style: AppTextStyles.caption,
                ),
              ],
            ),
          ),
          const SizedBox(width: 40),
        ],
      ),
    );
  }

  /// 使用者氣泡（右側）
  Widget _buildUserBubble(ChatMessage message) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.end,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          const SizedBox(width: 40),
          Flexible(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                // 文字氣泡（藍色漸層）
                Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 14, vertical: 10),
                  decoration: BoxDecoration(
                    gradient: AppColors.primaryGradient,
                    borderRadius: const BorderRadius.only(
                      topLeft: Radius.circular(16),
                      topRight: Radius.circular(16),
                      bottomLeft: Radius.circular(16),
                      bottomRight: Radius.circular(2),
                    ),
                  ),
                  child: Text(
                    message.content,
                    style: AppTextStyles.bodyMedium
                        .copyWith(color: Colors.white),
                  ),
                ),
                // 時間戳記
                const SizedBox(height: 4),
                Text(
                  _formatTime(message.time),
                  style: AppTextStyles.caption,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// AI 推薦商品卡片（氣泡內）
  Widget _buildProductCard(Map<String, dynamic> product) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.border),
      ),
      child: Row(
        children: [
          // 商品圖示
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              color: AppColors.surfaceVariant,
              borderRadius: BorderRadius.circular(10),
            ),
            child: const Icon(
              Icons.watch_rounded,
              color: AppColors.primary,
              size: 24,
            ),
          ),
          const SizedBox(width: 10),

          // 商品資訊
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  product['name'],
                  style: AppTextStyles.bodyMedium.copyWith(
                    color: AppColors.textPrimary,
                    fontWeight: FontWeight.w600,
                    fontSize: 13,
                  ),
                ),
                const SizedBox(height: 3),
                Text(
                  (product['tags'] as List<String>).join(' '),
                  style: AppTextStyles.caption
                      .copyWith(color: AppColors.accent),
                ),
                const SizedBox(height: 4),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      product['price'],
                      style: AppTextStyles.caption.copyWith(
                        color: AppColors.primary,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    Row(
                      children: [
                        const Icon(Icons.star_rounded,
                            color: AppColors.warning, size: 12),
                        const SizedBox(width: 2),
                        Text('${product['rating']}',
                            style: AppTextStyles.caption),
                      ],
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// AI 打字中動畫
  Widget _buildTypingIndicator() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 0, 16, 8),
      child: Row(
        children: [
          Container(
            width: 28,
            height: 28,
            decoration: BoxDecoration(
              gradient: AppColors.primaryGradient,
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Icon(
              Icons.smart_toy_outlined,
              color: Colors.white,
              size: 14,
            ),
          ),
          const SizedBox(width: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
            decoration: BoxDecoration(
              color: AppColors.surfaceVariant,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: AppColors.border),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: List.generate(3, (i) {
                return _TypingDot(delay: Duration(milliseconds: i * 200));
              }),
            ),
          ),
        ],
      ),
    );
  }

  /// 底部輸入框
  Widget _buildInputBar() {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
      decoration: BoxDecoration(
        color: AppColors.surface,
        border: Border(top: BorderSide(color: AppColors.border)),
      ),
      child: Row(
        children: [
          // 文字輸入框
          Expanded(
            child: TextField(
              controller: _inputController,
              style: AppTextStyles.bodyMedium
                  .copyWith(color: AppColors.textPrimary),
              maxLines: 4,
              minLines: 1,
              textInputAction: TextInputAction.send,
              onSubmitted: (_) => _sendMessage(),
              decoration: InputDecoration(
                hintText: '輸入您的需求...',
                hintStyle: AppTextStyles.bodyMedium,
                filled: true,
                fillColor: AppColors.surfaceVariant,
                contentPadding: const EdgeInsets.symmetric(
                    horizontal: 16, vertical: 10),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(20),
                  borderSide: const BorderSide(color: AppColors.border),
                ),
                enabledBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(20),
                  borderSide: const BorderSide(color: AppColors.border),
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(20),
                  borderSide: const BorderSide(
                      color: AppColors.borderFocus, width: 1.5),
                ),
              ),
            ),
          ),
          const SizedBox(width: 10),

          // 送出按鈕
          GestureDetector(
            onTap: _sendMessage,
            child: Container(
              width: 44,
              height: 44,
              decoration: BoxDecoration(
                gradient: _isLoading
                    ? null
                    : AppColors.primaryGradient,
                color: _isLoading ? AppColors.surfaceVariant : null,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(
                Icons.send_rounded,
                color: _isLoading
                    ? AppColors.textHint
                    : Colors.white,
                size: 18,
              ),
            ),
          ),
        ],
      ),
    );
  }

  /// 時間格式化
  String _formatTime(DateTime time) {
    return '${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}';
  }
}

/// 打字動畫點點元件
class _TypingDot extends StatefulWidget {
  final Duration delay;
  const _TypingDot({required this.delay});

  @override
  State<_TypingDot> createState() => _TypingDotState();
}

class _TypingDotState extends State<_TypingDot>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 600),
    );
    _animation = Tween<double>(begin: 0, end: -6).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOut),
    );
    // 延遲後開始循環動畫
    Future.delayed(widget.delay, () {
      if (mounted) _controller.repeat(reverse: true);
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) {
        return Transform.translate(
          offset: Offset(0, _animation.value),
          child: Container(
            width: 6,
            height: 6,
            margin: const EdgeInsets.symmetric(horizontal: 3),
            decoration: const BoxDecoration(
              color: AppColors.textHint,
              shape: BoxShape.circle,
            ),
          ),
        );
      },
    );
  }
}