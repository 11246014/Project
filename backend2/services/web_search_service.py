import os
import re
import requests

from dotenv import load_dotenv

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")


KNOWN_BRANDS = [
    "Apple",
    "Samsung",
    "Garmin",
    "Xiaomi",
    "Fitbit",
    "Huawei",
    "Amazfit",
    "Google",
    "OPPO",
    "realme"
]


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


def detect_brand(title):

    title_lower = title.lower()

    for brand in KNOWN_BRANDS:

        if brand.lower() in title_lower:
            return brand

    return "Other"


def generate_reason(keyword, rating):

    if rating >= 4.5:
        return f"高評價商品，適合有「{keyword}」需求的使用者"

    elif rating >= 4.0:
        return f"熱門選擇，符合「{keyword}」使用情境"

    return f"符合「{keyword}」需求"


def clean_product(item, keyword):

    rating = item.get("rating", 0)

    try:
        rating = float(rating)
    except:
        rating = 0

    title = item.get("title", "")

    return {

        "title": title,

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

        "reason": generate_reason(
            keyword,
            rating
        ),

        "brand": detect_brand(title),

        "isTop": False
    }


def remove_duplicate_brand(products):

    brand_products = {}

    for product in products:

        brand = product.get(
            "brand",
            "Other"
        )

        if brand not in brand_products:

            brand_products[brand] = product

        else:

            old_rating = brand_products[
                brand
            ]["rating"]

            new_rating = product[
                "rating"
            ]

            if new_rating > old_rating:

                brand_products[
                    brand
                ] = product

    return list(
        brand_products.values()
    )


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

            # 過濾異常價格

            if product["price"] > 30000:
                continue

            products.append(product)

        # 品牌去重複

        products = remove_duplicate_brand(
            products
        )

        # 評分排序

        products.sort(
            key=lambda x: x["rating"],
            reverse=True
        )

        # 第一名標記

        if products:

            products[0]["isTop"] = True

            products[0]["match"] = 98

        print(
            f"[Web Search] 找到 {len(products)} 筆商品"
        )

        return products

    except Exception as e:

        print(
            f"[Web Search Error] {e}"
        )

        return []