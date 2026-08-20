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