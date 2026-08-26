# backend1_client.py

import requests

BASE_URL = "https://champion-sandpit-rash.ngrok-free.dev"


# =========================
# 儲存商品
# =========================

def save_product(product):

    try:

        payload = {

            "name": product.get(
                "title",
                ""
            ),

            "price": product.get(
                "price",
                0
            ),

            "description": product.get(
                "desc",
                ""
            ),

            "platform": product.get(
                "platform",
                ""
            ),

            "image": product.get(
                "image",
                ""
            ),

            "rating": int(
                product.get(
                    "rating",
                    0
                )
            ),

            "reason": product.get(
                "reason",
                ""
            ),

            "link": product.get(
                "link",
                ""
            )
        }

        response = requests.post(

            f"{BASE_URL}/products",

            json=payload,

            timeout=10
        )

        print(
            f"[Save Product] {response.status_code}"
        )

    except Exception as e:

        print(
            f"[Save Error] {e}"
        )


# =========================
# 紀錄推薦事件
# =========================

def log_recommendation_event(user_need, recommend_results):

    try:

        # Filter 流程會把原始問卷放在 user_need.raw.filters；
        # Chat 流程則放在 user_need.raw.text。
        source = (
            "filter"
            if getattr(user_need.raw, "filters", None) is not None
            else "chat"
        )

        payload = {
            "source": source,

            # UserNeed -> Persona
            "age_range": getattr(
                user_need.persona,
                "age_range",
                None
            ),

            "occupation": getattr(
                user_need.persona,
                "occupation",
                None
            ),

            "usage_scope": getattr(
                user_need.persona,
                "usage_scope",
                None
            ),

            # UserNeed 直接欄位
            "device_type": user_need.device_type,

            "usage": ",".join(
                user_need.usage or []
            ),

            "features": ",".join(
                user_need.features or []
            ),

            # UserNeed -> Preferences
            "os": getattr(
                user_need.preferences,
                "os",
                None
            ),

            "brand_preference": getattr(
                user_need.preferences,
                "brand",
                None
            ),

            # UserNeed -> Budget
            "budget_min": getattr(
                user_need.budget,
                "min",
                None
            ),

            "budget_max": getattr(
                user_need.budget,
                "max",
                None
            ),

            # 本次最終推薦前 3 名
            "top_brands": ",".join(
                [
                    str(product.get("brand", ""))
                    for product in recommend_results[:3]
                    if product.get("brand")
                ]
            ),

            "top_platforms": ",".join(
                [
                    str(product.get("platform", ""))
                    for product in recommend_results[:3]
                    if product.get("platform")
                ]
            ),

            "product_count": len(
                recommend_results
            ),
        }

        response = requests.post(
            f"{BASE_URL}/analytics/events",
            json=payload,
            timeout=10
        )

        print(
            f"[Analytics Event] {response.status_code}"
        )

    except Exception as e:

        # 統計紀錄失敗不能讓推薦 API 整個失敗。
        print(
            f"[Analytics Error] {e}"
        )


# =========================
# 查詢資料庫商品
# =========================

async def get_db_products():

    try:

        response = requests.get(

            f"{BASE_URL}/products",

            timeout=10
        )

        data = response.json()

        return data

    except Exception as e:

        print(
            f"[DB Search Error] {e}"
        )

        return []


# =========================
# 查詢合作廠商
# =========================

def get_sponsors():

    try:

        response = requests.get(

            f"{BASE_URL}/sponsors",

            timeout=10
        )

        data = response.json()

        return data

    except Exception as e:

        print(
            f"[Sponsor Search Error] {e}"
        )

        return []