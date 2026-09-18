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
        response.raise_for_status()
        return response.json().get('id')

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
# 查詢產品評論
# =========================

def get_reviews_by_product(product_id):
    """
    取得指定商品的所有評論。

    Backend1 API：
        GET /products/{product_id}/reviews

    回傳：
        list
    """

    try:

        response = requests.get(
            f"{BASE_URL}/products/{product_id}/reviews",
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        # 如果 API 直接回傳 list
        if isinstance(data, list):
            return data

        # 如果 API 回傳 {"reviews": [...]}
        if isinstance(data, dict):
            return data.get(
                "reviews",
                []
            )

        return []

    except requests.RequestException as e:

        print(
            f"[Backend1 Reviews Error] {e}"
        )

        return []

    except ValueError as e:

        print(
            f"[Backend1 Reviews JSON Error] {e}"
        )

        return []


# =========================
# 查詢所有商品評論摘要
# =========================

def get_all_review_summaries():
    """
    取得 Backend1 所有商品的評論摘要。

    Backend2 Ranking 會在一次推薦流程開始時呼叫，
    不在每個商品的迴圈裡重複呼叫。

    回傳格式：
        {
            product_id: summary,
            ...
        }
    """

    try:

        response = requests.get(
            f"{BASE_URL}/review_summaries",
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        # Backend1 若直接回傳：
        # {
        #     "123": {...},
        #     "456": {...}
        # }
        if isinstance(data, dict):

            # 如果 API 使用 summaries 包裝
            if "summaries" in data:
                summaries = data.get(
                    "summaries",
                    []
                )

                if isinstance(summaries, list):

                    return {
                        str(item.get("product_id")): item
                        for item in summaries
                        if isinstance(item, dict)
                        and item.get("product_id") is not None
                    }

                if isinstance(summaries, dict):
                    return summaries

            return data

        # 若 API 回傳 list：
        # [
        #     {"product_id": 1, ...},
        #     {"product_id": 2, ...}
        # ]
        if isinstance(data, list):

            return {
                str(item.get("product_id")): item
                for item in data
                if isinstance(item, dict)
                and item.get("product_id") is not None
            }

        return {}

    except requests.RequestException as e:

        print(
            f"[Backend1 Review Summary Error] {e}"
        )

        return {}

    except ValueError as e:

        print(
            f"[Backend1 Review Summary JSON Error] {e}"
        )

        return {}


# =========================
# 更新單則評論
# =========================

def update_review(review_id, data: dict):
    """
    更新指定評論的 AI 分析結果。

    例如：
        {
            "pros": ["續航佳", "配戴舒適"],
            "cons": ["價格偏高"]
        }

    回傳：
        Backend1 API 回傳資料
    """

    try:

        response = requests.patch(
            f"{BASE_URL}/reviews/{review_id}",
            json=data,
            timeout=10
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as e:

        print(
            f"[Backend1 Review Update Error] {e}"
        )

        return None

    except ValueError as e:

        print(
            f"[Backend1 Review Update JSON Error] {e}"
        )

        return None


# =========================
# 新增 / 更新商品評論摘要
# =========================

def upsert_review_summary(product_id, data: dict):
    """
    新增或更新指定商品的評論摘要。

    例如：
        {
            "top_pros": ["續航佳", "配戴舒適"],
            "top_cons": ["價格偏高"],
            "summary_text": "多數使用者認為續航與配戴舒適度表現不錯..."
        }

    回傳：
        Backend1 API 回傳資料
    """

    try:

        payload = {
            "review_count": data.get("review_count", 0),
            "positive_ratio": data.get("positive_ratio", 0.0),
            "top_pros": ",".join(data.get("top_pros", [])),
            "top_cons": ",".join(data.get("top_cons", [])),
            "summary_text": data.get("summary_text", ""),
        }

        response = requests.post(
            f"{BASE_URL}/products/{product_id}/review_summary",
            json=payload,
            timeout=15
        )

        response.raise_for_status()
        return response.json()

    except requests.RequestException as e:

        print(
            f"[Backend1 Review Summary Update Error] {e}"
        )

        return None

    except ValueError as e:

        print(
            f"[Backend1 Review Summary Update JSON Error] {e}"
        )

        return None
    
# =========================
# 查詢合作廠商
# =========================

def get_sponsors():
    """
    取得 Backend1 的合作廠商資料。

    Backend1 /sponsors 回傳格式：
    {
        "sponsors": [...]
    }

    這裡只回傳 sponsors list，
    讓後面的 Ranking 可以直接：
        for sponsor in sponsors:
    """

    try:

        response = requests.get(
            f"{BASE_URL}/sponsors",
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        return data.get(
            "sponsors",
            []
        )

    except requests.RequestException as e:

        print(
            f"[Backend1 Sponsor Error] {e}"
        )

        return []

    except ValueError as e:

        print(
            f"[Backend1 Sponsor JSON Error] {e}"
        )

        return []