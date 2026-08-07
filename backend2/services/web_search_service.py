#web_search_service.py
import os

import requests
from dotenv import load_dotenv
from services.product_filter_service import (
    clean_product
)

load_dotenv()

# =========================
# Search Config
# =========================
SEARCH_CACHE = {}

DEBUG_SEARCH = True

SEARCH_TIMEOUT = 30

MAX_SEARCH_RESULTS = 15

MIN_PRODUCT_PRICE = 100

MAX_PRODUCT_PRICE = 30000

TOP_MATCH_SCORE = 98

SERPAPI_KEY = os.getenv(
    "SERPAPI_KEY"
)

SERPAPI_URL = "https://serpapi.com/search"

# =========================
# Web Search
# =========================
def fetch_shopping_results(
    keyword,
    region="tw",
):
    """
    呼叫 SerpAPI Google Shopping，取得原始搜尋結果
    """

    params = {
        "engine": "google_shopping",
        "q": keyword,
        "api_key": SERPAPI_KEY,
    }

    if region == "tw":

        params["gl"] = "tw"
        params["hl"] = "zh-tw"

    response = requests.get(
        SERPAPI_URL,
        params=params,
        timeout=SEARCH_TIMEOUT,
    )

    response.raise_for_status()

    data = response.json()

    print_search_debug(
        keyword,
        params,
        response,
        data,
    )

    shopping_results = data.get(
        "shopping_results",
        [],
    )

    if DEBUG_SEARCH:
        print(
            f"[Shopping Results Count] "
            f"{len(shopping_results)}"
        )

    return shopping_results

# =========================
# Debug
# =========================

def print_search_debug(
    keyword,
    params,
    response,
    data,
):
    if not DEBUG_SEARCH:
        return

    print("=" * 50)
    print(f"[Web Search] {keyword}")

    print("\n========== Request Params ==========")
    print(params)
    print("====================================")

    print("Status:", response.status_code)
    print("URL:", response.url)

    print(
        "shopping_results:",
        len(data.get("shopping_results", []))
    )

    print("\n========== Search Parameters ==========")
    print(data.get("search_parameters"))
    print("======================================")

    print("\n========== Search Information ==========") 
    print(data.get("search_information"))
    print("======================================")

    print("Query:", keyword)

    if "error" in data:
        print("Error:", data["error"])

    print("=" * 50)

# =========================
# Product Validation
# =========================

def is_valid_product(product):
    """
    檢查商品資料是否完整
    """

    return bool(
        product.get("title")
    )


def is_valid_price(product):
    """
    檢查商品價格是否在有效範圍
    """
    return (
        MIN_PRODUCT_PRICE
        <= product["price"]
        <= MAX_PRODUCT_PRICE
    )

# =========================
# Product Post Process
# =========================

def mark_top_product(products):
    """
    標記第一名商品
    """

    if not products:
        return

    products[0]["isTop"] = True
    products[0]["match"] = TOP_MATCH_SCORE

def build_products(
    shopping_results,
    keyword
):
    """
    將 SerpAPI Shopping Results 轉換成 WearWise 商品格式
    """
    products = []

    for item in shopping_results[:MAX_SEARCH_RESULTS]:

        if DEBUG_SEARCH:
            print(
                f"[Item] {item.get('title')}"
            )
        # 商品資料標準化
        product = clean_product(
            item=item,
            keyword=keyword
        )

        if not product:

            continue

        if not is_valid_price(product):

            continue

        if not is_valid_product(product):
            continue

        products.append(product)

    return products


def finalize_products(products):
    """
    商品後處理
    1. 排序
    2. 標記 Top Product
    """
    if DEBUG_SEARCH:
        print(
            f"[Before Dedup] "
            f"{len(products)}"
        )

    products.sort(

        key=lambda x: x["rating"],

        reverse=True
    )

    mark_top_product(products)

    if DEBUG_SEARCH:
        print(
            f"[Web Search] 找到 "
            f"{len(products)} 筆商品"
        )

        print("=" * 50)

    return products


def web_search_products(
    keyword,
    region="tw",
):
    """
    Web 商品搜尋主流程

    流程：
    1. Cache
    2. SerpAPI Search
    3. Product Clean
    4. Product Post Process
    5. Cache Save
    """

    # =========================
    # Cache
    # =========================

    if keyword in SEARCH_CACHE:

        if DEBUG_SEARCH:
            print(
                f"[Cache Hit] {keyword}"
            )

        return SEARCH_CACHE[keyword]

    # =========================
    # Search
    # =========================

    try:

        shopping_results = fetch_shopping_results(
            keyword,
            region
        )

        products = build_products(
            shopping_results,
            keyword,
        )

        if DEBUG_SEARCH:
            print(
                f"[Clean Products] {len(products)}"
            )

        products = finalize_products(
            products,
        )

        # =========================
        # Cache Save
        # =========================

        if products:

            SEARCH_CACHE[keyword] = products

            if DEBUG_SEARCH:
                print(
                    f"[Cache Save] {keyword}"
                )

        return products

    # =========================
    # Error
    # =========================

    except requests.RequestException as e:

        print(
            f"[Web Search Error] {e}"
        )

        if DEBUG_SEARCH:
            print("=" * 50)

        return []