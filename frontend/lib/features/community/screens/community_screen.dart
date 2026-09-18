import 'package:flutter/material.dart';
import '../../../core/constants/app_colors.dart';
import '../../../services/review_service.dart';
import '../../../services/product_service.dart';
import '../widgets/review_card.dart';
import '../widgets/review_submit_sheet.dart';
import '../../../core/constants/app_text_styles.dart';

class CommunityScreen extends StatefulWidget {
  const CommunityScreen({super.key});
  @override
  State<CommunityScreen> createState() => _CommunityScreenState();
}

class _CommunityScreenState extends State<CommunityScreen> {
  final _scrollController = ScrollController();
  final List<Map<String, dynamic>> _reviews = [];
  final Map<int, Map<String, dynamic>> _productsById = {};
  bool _isLoading = false;
  bool _hasMore = true;
  int _offset = 0;
  static const _pageSize = 20;

  @override
  void initState() {
    super.initState();
    _loadMore();
    _loadProducts(); // 預先載入完整商品清單
    _scrollController.addListener(() {
      if (_scrollController.position.pixels >
          _scrollController.position.maxScrollExtent - 200) {
        _loadMore();
      }
    });
  }

  Future<void> _loadMore() async {
    if (_isLoading || !_hasMore) return;
    setState(() => _isLoading = true);
    try {
      final newItems = await ReviewService.getReviews(
        limit: _pageSize, offset: _offset,
      );
      setState(() {
        _reviews.addAll(newItems);
        _offset += newItems.length;
        _hasMore = newItems.length == _pageSize;
      });
    } catch (e) {
      debugPrint('社群心得載入失敗：$e');  // ← 先看這行印出什麼，就知道真正原因
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('載入失敗，請稍後再試')),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);  // ← 不管成功失敗，一定會把轉圈關掉
    }
  }

  /// 預先載入完整商品清單，讓點擊心得卡片時能查到含 price/link 的完整資料
Future<void> _loadProducts() async {
  try {
    final products = await ProductService.getProducts();
    if (!mounted) return;
    setState(() {
      for (final p in products) {
        final id = p['id'];
        if (id is int) _productsById[id] = p;
      }
    });
  } catch (e) {
    debugPrint('社群頁預載商品清單失敗：$e');
    // 失敗不影響主流程，ReviewCard 會自動退回簡易版資料
  }
}

  Future<void> _openSubmitSheet() async {
    try {
      final products = await ProductService.getProducts();
      if (!mounted) return;
      final success = await openReviewSubmitSheet(
        context,
        productListForSearch: products,
      );
      if (success == true) {
        setState(() { _reviews.clear(); _offset = 0; _hasMore = true; });
        _loadMore();
      }
    } catch (e) {
      debugPrint('開啟留言表單失敗：$e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('無法載入商品清單，請稍後再試')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bg(context),
      appBar: AppBar(
        title: Text(
          '社群心得',
          style: AppTextStyles.displayMedium.copyWith(
            fontSize: 18,  // 想再小可以調這個數字
            color: AppColors.textMain(context),
          ),
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _openSubmitSheet,
        child: const Icon(Icons.edit),
      ),
      body: _reviews.isEmpty && !_isLoading
          ? const Center(child: Text('目前還沒有人留言，成為第一個分享的人吧'))
          : ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.all(16),
              itemCount: _reviews.length + (_hasMore ? 1 : 0),
              itemBuilder: (context, index) {
                if (index >= _reviews.length) {
                  return const Padding(
                    padding: EdgeInsets.symmetric(vertical: 16),
                    child: Center(child: CircularProgressIndicator(strokeWidth: 2)),
                  );
                }
                return ReviewCard(review: _reviews[index], productsById: _productsById);
              },
            ),
    );
  }
}