# routers/search_router.py
from fastapi import APIRouter
from services.search_service import search_products
# 引入新寫好、用來對接後端 1 商品列表的函式
from services.backend1_client import get_db_products

router = APIRouter()

@router.get("/products/search")
def product_search(keyword: str):
    """
    原有的關鍵字搜尋功能 (保持不變)
    """
    results = search_products(keyword)
    return {
        "keyword": keyword,
        "results": results
    }

@router.get("/test-db-products")
async def test_db_products():
    """
    全新優化測試路由：
    前端呼叫此 API (5000 埠) -> 後端 2 透過 ngrok 戳後端 1 (8000 埠) -> 撈出真實 MySQL 商品資料
    """
    products = await get_db_products()

    return {
        "success": True,
        "message": "成功透過後端 2 代理抓取後端 1 的 MySQL 商品清單！",
        "data": products
    }