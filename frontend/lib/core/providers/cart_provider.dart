import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../services/cart_service.dart'; // 新增：雲端購物車同步

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
  Map<String, dynamic> toMap() => {
        'name': name,
        'price': price,
        'image': image,
        'tags': tags,
        'link': link,
        'platform': platform,
        'qty': qty,
      };

  /// 從本地儲存（或雲端 API）的 Map 還原成 CartItem
  factory CartItem.fromMap(Map<String, dynamic> map) {
    return CartItem(
      name: map['name']?.toString() ?? '未知商品',
      price: map['price'] ?? 0,
      image: map['image']?.toString() ?? '',
      tags: List<String>.from(map['tags'] ?? []),
      link: map['link']?.toString() ?? '',
      platform: map['platform']?.toString() ?? '',
      qty: (map['qty'] is int)
          ? map['qty'] as int
          : int.tryParse('${map['qty']}') ?? 1,
    );
  }
}

/// 購物車狀態管理
/// 繼承 StateNotifier<List<CartItem>>，整個購物車就是一個商品清單
///
/// 持久化說明：
/// 本地 SharedPreferences 只是「離線快取」，讓 App 啟動時能立刻顯示
/// 上次的購物車內容，不用等 API 回來才有畫面。
/// 真正的資料權威來源是後端 MySQL：每次加入/修改/刪除都會
/// 本地立即更新（讓 UI 有即時反應）+ 背景打 API 同步雲端。
class CartNotifier extends StateNotifier<List<CartItem>> {
  CartNotifier() : super([]) {
    // Notifier 建立時先從本地快取還原，讓畫面立刻有資料可顯示
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
  /// 本地立即更新 + 背景同步到雲端（不 await，避免加入購物車的操作感覺卡頓）
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

    // 背景同步到雲端資料庫；CartService 內部已 try-catch，
    // 就算 ngrok 網址過期或暫時斷線，也不會讓加入購物車的操作報錯
    CartService.addItem(
      name: newItem.name,
      price: newItem.price,
      image: newItem.image,
      tags: newItem.tags,
      link: newItem.link,
      platform: newItem.platform,
      qty: 1,
    );
  }

  /// 更新數量，delta 為正表示加、負表示減
  /// 數量降到 0 以下時自動從購物車移除該商品
  void updateQty(String key, int delta) {
    final updated = [...state];
    final index = updated.indexWhere((item) => item.key == key);
    if (index < 0) return;

    final newQty = updated[index].qty + delta;
    final platform = updated[index].platform;
    final name = updated[index].name;

    if (newQty <= 0) {
      updated.removeAt(index);
    } else {
      updated[index].qty = newQty;
    }
    state = updated;

    _saveToStorage();

    // 同步「絕對數量」到雲端；newQty <= 0 時由後端負責刪除該列
    CartService.updateQty(platform: platform, name: name, qty: newQty);
  }

  /// 移除單一商品
  void removeItem(String key) {
    // 先取出要刪除的項目資訊，才能同步告訴後端刪哪一筆
    final target = state.where((item) => item.key == key).toList();

    state = state.where((item) => item.key != key).toList();
    _saveToStorage();

    if (target.isNotEmpty) {
      CartService.removeItem(
        platform: target.first.platform,
        name: target.first.name,
      );
    }
  }

  /// 清空購物車（本地 + 雲端）
  void clear() {
    state = [];
    _saveToStorage();
    CartService.clearCart();
  }

  /// 登入成功後呼叫：直接用雲端資料覆蓋本地購物車
  ///
  /// 因為系統沒有訪客模式，登入前不會有需要合併的本地購物車資料，
  /// 所以這裡不做合併運算，單純把雲端最新結果同步下來即可，
  /// 確保換裝置登入同一帳號時看到的是同一份購物車。
  Future<void> loadFromServer() async {
    try {
      final cloudItems = await CartService.getCart();
      state = cloudItems.map((m) => CartItem.fromMap(m)).toList();
      await _saveToStorage();
    } catch (e) {
      debugPrint('讀取雲端購物車失敗，暫時顯示本地快取：$e');
    }
  }

  /// 登出時呼叫：只清空「本地快取」，不會呼叫後端刪除雲端資料
  /// 避免同一裝置換帳號登入時，看到前一位使用者的購物車內容
  void clearLocalOnLogout() {
    state = [];
    _saveToStorage();
  }
}

/// 全域購物車 Provider
final cartProvider = StateNotifierProvider<CartNotifier, List<CartItem>>((ref) {
  return CartNotifier();
});