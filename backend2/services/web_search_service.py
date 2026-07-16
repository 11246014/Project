import os

import requests
from dotenv import load_dotenv
from services.product_filter_service import (
    clean_price,
    clean_title,
    detect_brand,
    generate_reason,
    extract_features
)
load_dotenv()

# =========================
# Search Config
# =========================
SEARCH_CACHE = {}

DEBUG_SEARCH = False

SEARCH_TIMEOUT = 30

MAX_SEARCH_RESULTS = 15

MIN_PRODUCT_PRICE = 100

MAX_PRODUCT_PRICE = 30000

TOP_MATCH_SCORE = 98

SERPAPI_KEY = os.getenv(
    "SERPAPI_KEY"
)



# =========================
# 配件 / 非手錶黑名單
# =========================

BAD_KEYWORDS = [

    "錶帶",
    "表帶",
    "皮帶",
    "皮带",

    "保護貼",
    "保護殼",

    "充電線",
    "充電器",

    "配件",
    "替換帶",
    "腕帶",

    "手機殼",
    "耳機殼",

    "臂帶",
    "胸帶",
    "感測器",

    "襪子",
    "鞋子"
]

# =========================
# 穿戴裝置白名單
# =========================

WEARABLE_KEYWORDS = [

    "智慧手錶",
    "智慧手環",
    "智慧腕錶",

    "智能手錶",
    "智能手表",

    "運動手錶",

    "smartwatch",

    "watch",

    "watch fit",

    "galaxy watch",

    "apple watch",

    "garmin",

    "amazfit",

    "fitbit",

    "huawei",

    "xiaomi watch",

    "mi watch",

    "穿戴",

    "腕錶",

    "手環",

    "智慧手環",

    "智能手環",

    "運動手環",

    "band",

    "xiaomi band",

    "mi band",

    "galaxy fit",

    "fit3",

    "fit 3",

    "huawei band",

    "smart band",

    "fit3",

    "fit 3",

    "galaxy fit3",
    
    "samsung fit",
    
    "戒指",

    "智慧戒指",

    "智能戒指",

    "指環",

    "智慧指環",

    "智能指環",

    "smart ring",

    "ring"
    
]

# =========================
# 智慧手錶強化白名單
# =========================

SMARTWATCH_KEYWORDS = [

    "智慧手錶",

    "智能手錶",

    "智慧腕錶",

    "smartwatch",

    "watch",

    "watch fit",

    "galaxy watch",

    "apple watch",

    "garmin",

    "huawei watch",

    "xiaomi watch"
]











# =========================
# 商品資料清理
# =========================

def clean_product(
    item,
    keyword
):

    rating = item.get(
        "rating",
        0
    )

    try:

        rating = float(rating)

    except (TypeError, ValueError):

        rating = 0

    raw_title = item.get(
        "title",
        ""
    )

    snippet = item.get(
        "snippet",
        ""
    )

    feature_text = (
        raw_title +
        " " +
        snippet
    ).lower()

    if DEBUG_SEARCH:

        print(
            "[Desc]",
            snippet
        )

    # =========================
    # 商品名稱清理
    # =========================

    clean_name = clean_title(
        raw_title
    )

    title_lower = clean_name.lower()

    # =========================
    # 黑名單過濾
    # =========================

    for word in BAD_KEYWORDS:

        if word.lower() in title_lower:

            print(
                f"[Filtered] {clean_name}"
            )

            return None

    # =========================
    # 穿戴裝置過濾
    # =========================

    is_wearable = any(

        keyword.lower() in title_lower

        for keyword in WEARABLE_KEYWORDS
    )

    smartwatch_match = any(

        keyword.lower() in title_lower

        for keyword in SMARTWATCH_KEYWORDS
    )

    if not is_wearable and not smartwatch_match:

        print(
            f"[Not Wearable] {clean_name}"
        )

        return None

    # =========================
    # Feature Extraction
    # =========================

    features = extract_features(
        feature_text
    )

    print(
        "[Features]",
        clean_name,
        features
    )

    return {

        "title": clean_name,

        "raw_title": raw_title,

        "price": clean_price(
            item.get("price", "0")
        ),

        "platform": item.get(
            "source",
            ""
        ),

        "desc": snippet,

        "link": item.get(
            "link",
            ""
        ),

        "image": item.get(
            "thumbnail",
            ""
        ),

        "features": features,

        "tags": [],

        "rating": rating,

        "match": int(
            rating * 10
        ),

        "reason": generate_reason(
            keyword,
            rating
        ),

        "brand": detect_brand(
            clean_name
        ),

        "isTop": False
    }

def _text(product):
    return " ".join(
        str(product.get(key, ""))
        for key in (
            "title",
            "raw_title",
            "name",
            "desc",
            "description"
        )
    ).lower()

# =========================
# Web Search
# =========================

def fetch_shopping_results(keyword):

    print("=" * 50)

    print(
        f"[Web Search] {keyword}"
    )

    url = (
        "https://serpapi.com/search"
    )

    params = {

        "engine": "google_shopping",

        "q": keyword,

        "api_key": SERPAPI_KEY,

        "gl": "tw",

        "hl": "zh-tw"
    }

    response = requests.get(

        url,

        params=params,

        timeout=SEARCH_TIMEOUT
    )

    response.raise_for_status()

    data = response.json()

    shopping_results = data.get(
        "shopping_results",
        []
    )

    print(
        f"[Shopping Results Count] "
        f"{len(shopping_results)}"
    )

    return shopping_results

def build_products(
    shopping_results,
    keyword
):

    products = []

    for item in shopping_results[:MAX_SEARCH_RESULTS]:

        print("=" * 30)
        print(item.get("title"))
        print(item.get("price"))

        product = clean_product(
            item=item,
            keyword=keyword
        )

        if not product:

            continue

        print(
            "Clean Title:",
            product["title"]
        )

        print(
            "Clean Price:",
            product["price"]
        )

        if (
            product["price"] < MIN_PRODUCT_PRICE
            or
            product["price"] > MAX_PRODUCT_PRICE
        ):

            continue

        if not product["title"]:

            continue

        products.append(
            product
        )

    return products


def finalize_products(products):

    print(
        f"[Before Dedup] "
        f"{len(products)}"
    )

    # products = remove_duplicate_brand(
    #     products
    # )

    print(
        f"[After Dedup] "
        f"{len(products)}"
    )

    products.sort(

        key=lambda x: x["rating"],

        reverse=True
    )

    if products:

        products[0]["isTop"] = True

        products[0]["match"] = TOP_MATCH_SCORE

    print(
        f"[Web Search] 找到 "
        f"{len(products)} 筆商品"
    )

    print("=" * 50)

    return products


def web_search_products(
    keyword
):

    if keyword in SEARCH_CACHE:

        print(
            f"[Cache Hit] {keyword}"
        )

        return SEARCH_CACHE[keyword]

    try:

        shopping_results = fetch_shopping_results(
            keyword
        )

        products = build_products(
            shopping_results,
            keyword
        )

        products = finalize_products(
            products
        )

        SEARCH_CACHE[keyword] = products

        return products

    except requests.RequestException as e:

        print(
            f"[Web Search Error] {e}"
        )

        print("=" * 50)

        return []