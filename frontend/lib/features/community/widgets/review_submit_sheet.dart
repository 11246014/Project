import 'package:flutter/material.dart';
import '../../../core/constants/app_colors.dart';
import '../../../core/constants/app_text_styles.dart';
import '../../../services/review_service.dart';

/// 開啟留言表單的共用函式
/// productId 有值代表已知商品，為 null 代表要在表單內先選商品
Future<bool?> openReviewSubmitSheet(
  BuildContext context, {
  int? productId,
  String? productName,
  List<Map<String, dynamic>>? productListForSearch,
}) {
  return showModalBottomSheet<bool>(
    context: context,
    isScrollControlled: true,
    backgroundColor: AppColors.cardBg(context),
    shape: const RoundedRectangleBorder(
      borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
    ),
    builder: (_) => ReviewSubmitSheet(
      initialProductId: productId,
      initialProductName: productName,
      productListForSearch: productListForSearch ?? [],
    ),
  );
}

class ReviewSubmitSheet extends StatefulWidget {
  final int? initialProductId;
  final String? initialProductName;
  final List<Map<String, dynamic>> productListForSearch;

  const ReviewSubmitSheet({
    super.key,
    this.initialProductId,
    this.initialProductName,
    this.productListForSearch = const [],
  });

  @override
  State<ReviewSubmitSheet> createState() => _ReviewSubmitSheetState();
}

class _ReviewSubmitSheetState extends State<ReviewSubmitSheet> {
  int? _selectedProductId;
  String? _selectedProductName;
  int _rating = 3;
  final _contentController = TextEditingController();
  final _searchController = TextEditingController();
  List<Map<String, dynamic>> _searchResults = [];
  bool _isSubmitting = false;

  @override
  void initState() {
    super.initState();
    _selectedProductId = widget.initialProductId;
    _selectedProductName = widget.initialProductName;
  }

  /// 本地字串比對篩選商品清單，不打 API
  void _onSearchChanged(String keyword) {
    if (keyword.trim().isEmpty) {
      setState(() => _searchResults = []);
      return;
    }
    setState(() {
      _searchResults = widget.productListForSearch
          .where((p) => (p['name']?.toString() ?? '').contains(keyword))
          .take(6)
          .toList();
    });
  }

  Future<void> _submit() async {
    if (_selectedProductId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('請先選擇商品')),
      );
      return;
    }
    setState(() => _isSubmitting = true);
    try {
      await ReviewService.createReview(
        productId: _selectedProductId!,
        rating: _rating,
        content: _contentController.text.trim(),
      );
      if (mounted) Navigator.of(context).pop(true);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('送出失敗，請稍後再試')),
        );
      }
    } finally {
      if (mounted) setState(() => _isSubmitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(
        left: 20, right: 20, top: 20,
        bottom: MediaQuery.of(context).viewInsets.bottom + 20,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('分享使用心得', style: AppTextStyles.displayMedium
              .copyWith(color: AppColors.textMain(context))),
          const SizedBox(height: 16),

          if (_selectedProductId != null)
            Row(
              children: [
                Expanded(child: Text('商品：$_selectedProductName')),
                TextButton(
                  onPressed: () => setState(() => _selectedProductId = null),
                  child: const Text('更換'),
                ),
              ],
            )
          else ...[
            TextField(
              controller: _searchController,
              onChanged: _onSearchChanged,
              decoration: const InputDecoration(
                hintText: '搜尋商品名稱...',
                prefixIcon: Icon(Icons.search),
              ),
            ),
            ..._searchResults.map((p) => ListTile(
              title: Text(p['name']?.toString() ?? ''),
              onTap: () => setState(() {
                _selectedProductId = p['id'] as int;
                _selectedProductName = p['name']?.toString();
                _searchResults = [];
              }),
            )),
          ],
          const SizedBox(height: 20),

          Text('你的評價', style: AppTextStyles.bodyMedium),
          const SizedBox(height: 8),
          Row(
            children: [
              _ratingRadio(label: '不滿意', value: 1),
              _ratingRadio(label: '普通', value: 2),
              _ratingRadio(label: '滿意', value: 3),
            ],
          ),
          const SizedBox(height: 16),

          Text('想說點什麼？（可留空）', style: AppTextStyles.bodyMedium),
          const SizedBox(height: 8),
          TextField(
            controller: _contentController,
            maxLines: 4,
            decoration: const InputDecoration(border: OutlineInputBorder()),
          ),
          const SizedBox(height: 12),
          Text('🔒 你的心得將以匿名方式發布',
              style: AppTextStyles.caption.copyWith(color: AppColors.textHint)),
          const SizedBox(height: 20),

          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: _isSubmitting ? null : _submit,
              child: Text(_isSubmitting ? '送出中...' : '送出心得'),
            ),
          ),
        ],
      ),
    );
  }

  Widget _ratingRadio({required String label, required int value}) {
    return Expanded(
      child: RadioListTile<int>(
        title: Text(label, style: AppTextStyles.caption),
        value: value,
        groupValue: _rating,
        onChanged: (v) => setState(() => _rating = v!),
        contentPadding: EdgeInsets.zero,
      ),
    );
  }
}