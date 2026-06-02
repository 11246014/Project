# services/backend1_client.py
import httpx

# 後端 1 的 ngrok 網址
BASE_URL = "https://champion-sandpit-rash.ngrok-free.dev" 

async def get_db_products():
    """向 backend1 請求 MySQL 裡的真實商品資料"""
    async with httpx.AsyncClient() as client:
        # 正確對齊他畫面上的 GET /products
        r = await client.get(f"{BASE_URL}/products")
        return r.json()