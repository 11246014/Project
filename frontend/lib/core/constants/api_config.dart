class ApiConfig {
  ApiConfig._();

  // 給 Backend1 (處理註冊、登入、商品 CRUD)
  static const String dbBaseUrl = 'https://champion-sandpit-rash.ngrok-free.dev/docs';
  
  // 給 Backend2 (處理 AI 推薦與搜尋)
  static const String aiBaseUrl = 'https://thumb-shakiness-zoom.ngrok-free.dev/docs';
}