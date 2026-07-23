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

SEARCH_TIMEOUT = 30

MAX_SEARCH_RESULTS = 15

MIN_PRODUCT_PRICE = 100

MAX_PRODUCT_PRICE = 30000

TOP_MATCH_SCORE = 98

SERPAPI_KEY = os.getenv(
    "SERPAPI_KEY"
)

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
        "hl": "zh-tw",
    }
    response = requests.get(
        url,
        params=params,
        timeout=SEARCH_TIMEOUT
    )

    response.raise_for_status()

    data = response.json()

    print("\n========== SerpAPI Response ==========")

    if "error" in data:
        print("Error:", data["error"])
    else:
        print(data.keys())

    print("======================================")

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

        print(
            f"[Item] {item.get('title')}"
        )
        product = clean_product(
            item=item,
            keyword=keyword
        )

        if not product:

            continue

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

        if products:
            SEARCH_CACHE[keyword] = products

        print(
            f"[Cache Save] {keyword}"
        )
        return products

    except requests.RequestException as e:

        print(
            f"[Web Search Error] {e}"
        )

        print("=" * 50)

        return []