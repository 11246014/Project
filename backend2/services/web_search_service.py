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

# =========================
# Store Link Resolver
# =========================

TAIWAN_STORE_PRIORITY = [
    "PChome 24h購物",
    "momo購物網",
    "Yahoo購物中心",
    "神腦生活",
    "Apple",
]


def select_store_link(
    stores,
    preferred_store=None,
):
    """
    從 Immersive Product 的 stores
    選擇適合的台灣電商商品連結。
    """

    if not stores:
        return ""

    # =========================
    # Preferred Store
    # =========================

    if preferred_store:

        for store in stores:

            name = store.get(
                "name",
                "",
            )

            if preferred_store.lower() in name.lower():

                link = store.get(
                    "link",
                    "",
                )

                if is_valid_store_link(link):
                    return link

    # =========================
    # Taiwan Store Priority
    # =========================

    for preferred_name in TAIWAN_STORE_PRIORITY:

        for store in stores:

            name = store.get(
                "name",
                "",
            )

            if preferred_name.lower() in name.lower():

                link = store.get(
                    "link",
                    "",
                )

                if is_valid_store_link(link):
                    return link

    # =========================
    # Fallback
    # =========================

    for store in stores:

        link = store.get(
            "link",
            "",
        )

        if is_valid_store_link(link):
            return link

    return ""

# =========================
# Store Offers
# =========================

def extract_store_offers(
    stores,
):
    """
    將 Immersive Product 的
    stores 資料轉換成 WearWise
    標準商店資訊。
    """

    offers = []

    if not stores:
        return offers

    for store in stores:

        name = store.get(
            "name",
            "",
        )

        link = store.get(
            "link",
            "",
        )

        price = store.get(
            "extracted_price",
        )

        if not price:

            price = store.get(
                "price",
                "",
            )

        if not name or not link:
            continue

        offers.append({

            "store": name,

            "title": store.get(
                "title",
                "",
            ),

            "price": price,

            "link": link,

            "currency": store.get(
                "currency",
                "",
            ),

            "rating": store.get(
                "rating",
                0,
            ),

            "reviews": store.get(
                "reviews",
                0,
            ),
        })

    return offers

# =========================
# Store Link Validation
# =========================

def is_valid_store_link(link):
    """
    判斷是否為可直接前往電商的商品 Link。
    """

    if not link:
        return False

    link = link.lower().strip()

    # Google Shopping / Google Search redirect
    if "google.com/search" in link:
        return False

    if "google.com/shopping" in link:
        return False

    # Google redirect
    if "googleadservices.com" in link:
        return False

    return (
        link.startswith("http://")
        or
        link.startswith("https://")
    )

# =========================
# Immersive Product Debug
# =========================
def fetch_immersive_product(
    api_url,
    preferred_store=None,
):
    """
    取得單一商品的
    Google Immersive Product 詳細資料，
    並解析商店商品連結。
    """

    if not api_url:
        return ""

    try:

        response = requests.get(
            api_url,
            params={
                "api_key": SERPAPI_KEY,
            },
            timeout=SEARCH_TIMEOUT,
        )

        response.raise_for_status()

        data = response.json()

        product_results = data.get(
            "product_results",
            {},
        )

        stores = product_results.get(
            "stores",
            [],
        )
        offers = extract_store_offers(
            stores
        )
        print(
            "\n========== Store Offers =========="
        )

        for offer in offers:

            print(
                "Store:",
                offer["store"]
            )

            print(
                "Price:",
                offer["price"]
            )

            print(
                "Link:",
                offer["link"]
            )

            print(
                "Valid:",
                is_valid_store_link(
                    offer["link"]
                )
            )

            print(
                "-" * 50
            )

        print(
            "=================================="
        )

        link = select_store_link(
            stores,
            preferred_store=preferred_store,
        )

        if DEBUG_SEARCH:

            print(
                "\n========== Store Link Resolver =========="
            )

            print(
                "Preferred Store:",
                preferred_store,
            )

            print(
                "Stores:",
                len(stores),
            )

            print(
                "Selected Link:",
                link,
            )

            print(
                "=========================================\n"
            )

        return link

    except requests.RequestException as e:

        print(
            f"[Immersive Product Error] {e}"
        )

        return ""
    
def build_products(
    shopping_results,
    keyword
):
    """
    將 SerpAPI Shopping Results
    轉換成 WearWise 商品格式
    """

    products = []

    for item in shopping_results[:MAX_SEARCH_RESULTS]:

        if DEBUG_SEARCH:
            print(
                f"[Item] {item.get('title')}"
            )

        # =========================
        # 商品資料標準化
        # =========================

        product = clean_product(
            item=item,
            keyword=keyword
        )

        if not product:
            continue

        # =========================
        # Step 8A-8
        # Resolve Real Store Link
        # =========================

        if DEBUG_SEARCH:

            immersive_api = item.get(
                "serpapi_immersive_product_api",
                ""
            )

            resolved_link = fetch_immersive_product(
                immersive_api,
                preferred_store=product.get(
                    "platform",
                    ""
                ),
            )

            if resolved_link:

                product["link"] = resolved_link
        # =========================
        # Link Debug
        # =========================

        if DEBUG_SEARCH:
            print(
                "[Link Debug]"
            )

            print(
                "Title:",
                product.get("title", "")
            )

            print(
                "Product ID:",
                product.get("product_id", "")
            )

            print(
                "Platform:",
                product.get("platform", "")
            )

            print(
                "Link:",
                product.get("link", "")
            )

            print(
                "-" * 50
            )

        # =========================
        # Product Validation
        # =========================

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