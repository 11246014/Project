import 'package:flutter/material.dart';
import '../../../core/constants/app_colors.dart';
import '../../../core/constants/app_text_styles.dart';
import '../../../services/review_service.dart';
import '../../community/widgets/review_card.dart';
import '../../../services/product_service.dart';

/// 商品詳情頁「查看全部心得」用：顯示單一商品的完整心得列表
class ProductReviewsScreen extends StatefulWidget {
  final int productId;
  final String productName;
  const ProductReviewsScreen({
    super.key,
    required this.productId,
    required this.productName,
  });

  @override
  State<ProductReviewsScreen> createState() => _ProductReviewsScreenState();
}

class _ProductReviewsScreenState extends State<ProductReviewsScreen> {
  late Future<List<Map<String, dynamic>>> _future;
  final Map<int, Map<String, dynamic>> _productsById = {};

  @override
  void initState() {
    super.initState();
    _future = ReviewService.getProductReviews(widget.productId);
    _loadProducts(); // 新增：預先載入完整商品清單
  }

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
      debugPrint('商品心得頁預載商品清單失敗：$e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bg(context),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: Text(widget.productName, style: AppTextStyles.bodyLarge),
      ),
      body: FutureBuilder<List<Map<String, dynamic>>>(
        future: _future,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(
              child: Text('心得載入失敗，請稍後再試',
                  style: AppTextStyles.bodyMedium.copyWith(color: AppColors.textHint)),
            );
          }
          final reviews = snapshot.data ?? [];
          if (reviews.isEmpty) {
            return Center(
              child: Text('目前尚無心得',
                  style: AppTextStyles.bodyMedium.copyWith(color: AppColors.textHint)),
            );
          }
          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: reviews.length,
            itemBuilder: (context, index) => ReviewCard(review: reviews[index]),
          );
        },
      ),
    );
  }
}