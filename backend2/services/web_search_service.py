import os
import re
import requests

from dotenv import load_dotenv

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")


def clean_price(price_text):

    if not price_text:
        return 0

    numbers = re.sub(
        r"[^\d]",
        "",
        str(price_text)
    )

    try:
        return int(numbers)
    except:
        return 0


def clean_product(item, keyword):

    rating = item.get("rating", 0)

    try:
        rating = float(rating)
    except:
        rating = 0

    return {

        "title": item.get(
            "title",
            ""
        ),

        "price": clean_price(
            item.get("price", "0")
        ),

        "platform": item.get(
            "source",
            ""
        ),

        "desc": item.get(
            "snippet",
            ""
        ),

        "link": item.get(
            "link",
            ""
        ),

        "image": item.get(
            "thumbnail",
            ""
        ),

        "tags": [],

        "rating": rating,

        "match": int(rating * 20),

        "reason": f"符合「{keyword}」需求",

        "isTop": False
    }


def web_search_products(keyword):

    print(f"[Web Search] {keyword}")

    url = "https://serpapi.com/search"

    params = {

        "engine": "google_shopping",

        "q": keyword,

        "api_key": SERPAPI_KEY,

        "gl": "tw",

        "hl": "zh-tw"
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=15
        )

        data = response.json()

        products = []

        for item in data.get(
            "shopping_results",
            []
        )[:10]:

            product = clean_product(
                item,
                keyword
            )

            # ===== 過濾異常價格 =====

            if product["price"] > 30000:
                continue

            products.append(product)

        # ===== 評分排序 =====

        products.sort(
            key=lambda x: x["rating"],
            reverse=True
        )

        # ===== 第一名標記 =====

        if products:

            products[0]["isTop"] = True

        print(
            f"[Web Search] 找到 {len(products)} 筆商品"
        )

        return products

    except Exception as e:

        print(
            f"[Web Search Error] {e}"
        )

        return []