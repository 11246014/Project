import os
import re
import requests

from dotenv import load_dotenv

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")

search_cache = {}


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

    try:

        text = str(price_text)

        # 移除貨幣符號與逗號
        text = text.replace("$", "")
        text = text.replace("NT$", "")
        text = text.replace(",", "")

        # 取整數部分
        value = float(text)

        return int(value)

    except Exception:

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

# ===== Cache =====

    if keyword in search_cache:

        print(
            f"[Cache Hit] {keyword}"
        )

        return search_cache[keyword]

def web_search_products(keyword):

    print("=" * 50)
    print(f"[Web Search] {keyword}")

    print(
        f"[SERPAPI_KEY Loaded] {SERPAPI_KEY[:10]}..."
        if SERPAPI_KEY
        else "[SERPAPI_KEY NOT FOUND]"
    )

    url = "https://serpapi.com/search"

    params = {

        "engine": "google_shopping",

        "q": keyword,

        "api_key": SERPAPI_KEY,

        "gl": "tw",

        "hl": "zh-tw"
    }

    try:

        print("[SerpAPI Request Start]")

        response = requests.get(
            url,
            params=params,
            timeout=30
        )

        print("[SerpAPI Response OK]")

        print(
            f"[Status Code] {response.status_code}"
        )

        print("[Response Preview]")
        print(response.text[:1000])

        data = response.json()

        shopping_results = data.get(
            "shopping_results",
            []
        )

        print(
            f"[Shopping Results Count] {len(shopping_results)}"
        )

        products = []

        for item in shopping_results[:10]:

            print("=" * 30)
            print(item.get("title"))
            print(item.get("price"))

            product = clean_product(
                item,
                keyword
            )

            print("Clean Price:", product["price"])

            if product["price"] > 30000:

                print("Price Filtered")

                continue

            products.append(product)

        print(
            f"[Before Dedup] {len(products)}"
        )

        products = remove_duplicate_brand(
            products
        )

        print(
            f"[After Dedup] {len(products)}"
        )

        products.sort(
            key=lambda x: x["rating"],
            reverse=True
        )

        if products:

            products[0]["isTop"] = True

            products[0]["match"] = 98

        print(
            f"[Web Search] 找到 {len(products)} 筆商品"
        )

        print("=" * 50)

        return products

    except Exception as e:

        print(
            f"[Web Search Error] {e}"
        )

        print("=" * 50)

        return []