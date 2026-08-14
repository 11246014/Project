import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// 購物車商品資料模型
///
/// 設計原則：WearWise 的購物車定位是「決策支援與比較工具」，
/// 不做真正的交易，因此只保留「顯示」與「跳轉外部平台」所需的欄位，
/// 不需要 orderId、庫存、金流等交易相關欄位。
class CartItem {
  final String name;
  final dynamic price; // 後端可能回傳 int 或 String，統一交給 AppFormatters.formatPrice() 處理
  final String image;
  final List<String> tags;
  final String link; // 外部電商平台商品連結，跳轉購買時使用
  final String platform; // 資料來源平台（momo / PChome / 蝦皮 / MySQL...）
  int qty;

  CartItem({
    required this.name,
    required this.price,
    required this.image,
    required this.tags,
    required this.link,
    required this.platform,
    this.qty = 1,
  });

  /// 用「商品名稱 + 來源平台」當作唯一識別
  /// 同一商品重複加入購物車時，用這個 key 判斷要累加數量還是新增一筆
  String get key => '$platform-$name';

  /// 序列化成可存進 SharedPreferences 的 Map
  /// price 可能是 int 或 String，統一轉成字串存，讀回來時再交給呼叫端自行判斷/格式化
  Map<String, dynamic> toMap() => {
        'name': name,
        'price': price,
        'image': image,
        'tags': tags,
        'link': link,
        'platform': platform,
        'qty': qty,
      };

  /// 從本地儲存的 Map 還原成 CartItem
  factory CartItem.fromMap(Map<String, dynamic> map) {
    return CartItem(
      name: map['name']?.toString() ?? '未知商品',
      // price 存回來可能是 int 也可能被 json 轉成 num，這裡保留原始型別彈性
      price: map['price'] ?? 0,
      image: map['image']?.toString() ?? '',
      tags: List<String>.from(map['tags'] ?? []),
      link: map['link']?.toString() ?? '',
      platform: map['platform']?.toString() ?? '',
      qty: (map['qty'] is int) ? map['qty'] as int : int.tryParse('${map['qty']}') ?? 1,
    );
  }
}

/// 購物車狀態管理
/// 繼承 StateNotifier<List<CartItem>>，整個購物車就是一個商品清單
///
/// 持久化說明：
/// 每次購物車內容變動（新增／改數量／刪除／清空），都會把當前清單
/// 序列化成 JSON 字串寫入 SharedPreferences；App 啟動時會嘗試讀回。
/// 這樣重開 App 或重新整理網頁後，購物車內容才不會消失。
class CartNotifier extends StateNotifier<List<CartItem>> {
  CartNotifier() : super([]) {
    // Notifier 建立時立刻嘗試從本地儲存還原購物車
    _loadFromStorage();
  }

  // SharedPreferences 存放購物車資料用的 key
  static const String _storageKey = 'wearwise_cart_items';

  /// 從 SharedPreferences 讀取購物車資料並還原成 state
  /// 讀取失敗（例如首次安裝、資料損毀）不影響 App 啟動，僅記錄 log
  Future<void> _loadFromStorage() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final jsonStr = prefs.getString(_storageKey);

      if (jsonStr == null || jsonStr.isEmpty) return;

      final List<dynamic> decoded = jsonDecode(jsonStr) as List<dynamic>;
      state = decoded
          .map((item) => CartItem.fromMap(item as Map<String, dynamic>))
          .toList();
    } catch (e) {
      debugPrint('購物車讀取失敗，改用空購物車：$e');
    }
  }

  /// 把目前的購物車 state 寫入 SharedPreferences
  /// 每次 state 變動都呼叫這個，確保資料即時落地，不用等使用者手動存檔
  Future<void> _saveToStorage() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final jsonStr = jsonEncode(state.map((item) => item.toMap()).toList());
      await prefs.setString(_storageKey, jsonStr);
    } catch (e) {
      debugPrint('購物車儲存失敗：$e');
    }
  }

  /// 加入購物車
  /// [product] 是從商品卡片 / 詳情頁傳入的完整 Map（後端回傳的商品格式）
  /// 若購物車中已有相同商品（同 key），數量 +1；否則新增一筆，數量預設 1
  void addItem(Map<String, dynamic> product) {
    final newItem = CartItem(
      name: product['name']?.toString() ?? '未知商品',
      price: product['price'] ?? 0,
      image: product['image']?.toString() ?? '',
      tags: List<String>.from(product['tags'] ?? product['features'] ?? []),
      link: product['link']?.toString() ?? '',
      platform: product['platform']?.toString() ?? '',
    );

    final existingIndex = state.indexWhere((item) => item.key == newItem.key);

    if (existingIndex >= 0) {
      // 已存在同商品，數量 +1
      // 用新 List 觸發 Riverpod 的狀態更新（直接改物件內容 Riverpod 偵測不到）
      final updated = [...state];
      updated[existingIndex].qty += 1;
      state = updated;
    } else {
      state = [...state, newItem];
    }

    _saveToStorage();
  }

  /// 更新數量，delta 為正表示加、負表示減
  /// 數量降到 0 以下時自動從購物車移除該商品
  void updateQty(String key, int delta) {
    final updated = [...state];
    final index = updated.indexWhere((item) => item.key == key);
    if (index < 0) return;

    final newQty = updated[index].qty + delta;
    if (newQty <= 0) {
      updated.removeAt(index);
    } else {
      updated[index].qty = newQty;
    }
    state = updated;

    _saveToStorage();
  }

  /// 移除單一商品
  void removeItem(String key) {
    state = state.where((item) => item.key != key).toList();
    _saveToStorage();
  }

  /// 清空購物車
  void clear() {
    state = [];
    _saveToStorage();
  }
}

/// 全域購物車 Provider
final cartProvider = StateNotifierProvider<CartNotifier, List<CartItem>>((ref) {
  return CartNotifier();
});