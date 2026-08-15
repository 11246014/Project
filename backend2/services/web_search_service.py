#web_search_service.py
import os

import requests
from dotenv import load_dotenv

from services.product_filter_service import (
    clean_product,
)

load_dotenv()


# =========================================================
# Search Config
# =========================================================

SEARCH_CACHE = {}

DEBUG_SEARCH = False

SEARCH_TIMEOUT = 30

MAX_SEARCH_RESULTS = 15

MIN_PRODUCT_PRICE = 100

MAX_PRODUCT_PRICE = 30000

SERPAPI_KEY = os.getenv(
    "SERPAPI_KEY"
)

SERPAPI_URL = (
    "https://serpapi.com/search"
)


# =========================================================
# Region Config
# =========================================================

REGION_CONFIG = {

    "tw": {
        "google_domain": "google.com",
        "hl": "zh-tw",
        "gl": "tw",
    },

    "us": {
        "google_domain": "google.com",
        "hl": "en",
        "gl": "us",
    },

    "global": {
        "google_domain": "google.com",
        "hl": "en",
        "gl": "us",
    },
}


def normalize_region(region):
    """
    統一 Search Region。

    支援：
    tw
    us
    global

    未知 region 預設使用 tw。
    """

    if not region:
        return "tw"

    region = str(
        region
    ).lower().strip()

    if region in REGION_CONFIG:
        return region

    return "tw"


# =========================================================
# SerpAPI Search
# =========================================================

def fetch_shopping_results(
    keyword,
    region="tw",
):
    """
    呼叫 SerpAPI Google Shopping，
    取得原始 Shopping Search Results。

    注意：
    這裡只負責 Search。
    不負責 Ranking。
    不負責 Summary。
    """

    region = normalize_region(
        region
    )

    config = REGION_CONFIG[
        region
    ]

    params = {
        "engine": "google_shopping",
        "q": keyword,
        "api_key": SERPAPI_KEY,

        "google_domain": config[
            "google_domain"
        ],

        "hl": config[
            "hl"
        ],

        "gl": config[
            "gl"
        ],

        "device": "desktop",
    }

    response = requests.get(
        SERPAPI_URL,
        params=params,
        timeout=SEARCH_TIMEOUT,
    )

    response.raise_for_status()

    data = response.json()

    print_search_debug(
        keyword,
        region,
        params,
        response,
        data,
    )

    return data.get(
        "shopping_results",
        [],
    )


# =========================================================
# SerpAPI Debug
# =========================================================

def print_search_debug(
    keyword,
    region,
    params,
    response,
    data,
):
    """
    SerpAPI Debug。

    API Key 不直接輸出。
    """

    if not DEBUG_SEARCH:
        return

    print("=" * 50)

    print(
        f"[Web Search] "
        f"{keyword} "
        f"(region={region})"
    )

    # -----------------------------------------------------
    # Request Params
    # -----------------------------------------------------

    print(
        "\n========== Search Parameters =========="
    )

    safe_params = params.copy()

    safe_params["api_key"] = "***"

    print(
        safe_params
    )

    print(
        "======================================"
    )

    # -----------------------------------------------------
    # HTTP Status
    # -----------------------------------------------------

    print(
        "Status:",
        response.status_code,
    )

    # -----------------------------------------------------
    # Shopping Results Count
    # -----------------------------------------------------

    shopping_results = data.get(
        "shopping_results",
        [],
    )

    print(
        "Shopping Results:",
        len(
            shopping_results
        ),
    )

    # -----------------------------------------------------
    # Search Information
    # -----------------------------------------------------

    print(
        "\n========== Search Information =========="
    )

    print(
        data.get(
            "search_information"
        )
    )

    print(
        "======================================"
    )

    # -----------------------------------------------------
    # Query
    # -----------------------------------------------------

    print(
        "Query:",
        keyword,
    )

    # -----------------------------------------------------
    # API Error
    # -----------------------------------------------------

    if "error" in data:

        print(
            "Error:",
            data["error"],
        )

    print("=" * 50)


# =========================================================
# Product Validation
# =========================================================

def is_valid_product(product):
    """
    商品至少需要有名稱。
    """

    return bool(
        product.get(
            "title"
        )
    )


def is_valid_price(product):
    """
    檢查商品價格是否存在，
    並確認是否落在合理範圍。

    注意：
    這不是 User Budget Filter。

    User Budget 由
    search_filter_service.py
    負責。

    這裡只做 Web 商品資料的基本品質檢查。
    """

    price = product.get(
        "price"
    )

    if price is None:
        return False

    try:

        price = float(
            price
        )

    except (
        TypeError,
        ValueError,
    ):

        return False

    return (
        MIN_PRODUCT_PRICE
        <= price
        <= MAX_PRODUCT_PRICE
    )


# =========================================================
# Build Products
# =========================================================

def build_products(
    shopping_results,
    keyword,
    region="tw",
):
    """
    將 SerpAPI Shopping Results
    轉換成 WearWise Product。

    Web Search 在這裡只負責：

    1. 呼叫 clean_product()
    2. 基本 Product Validation

    不負責：

    - Ranking
    - Top Product
    - Summary
    - User Requirement Filter
    """

    region = normalize_region(
        region
    )

    products = []

    for item in shopping_results[
        :MAX_SEARCH_RESULTS
    ]:

        if DEBUG_SEARCH:

            print(
                f"[Item] "
                f"{item.get('title')}"
            )

        # -------------------------------------------------
        # Product Clean
        # -------------------------------------------------

        product = clean_product(
            item=item,
            keyword=keyword,
            region=region,
        )

        if not product:
            continue

        # -------------------------------------------------
        # Basic Validation
        # -------------------------------------------------

        if not is_valid_product(
            product
        ):
            continue

        if not is_valid_price(
            product
        ):
            continue

        # -------------------------------------------------
        # Product Debug
        # -------------------------------------------------

        if DEBUG_SEARCH:

            print(
                "[Product]",
                product.get(
                    "title",
                    "",
                ),
                "| price =",
                product.get(
                    "price",
                    "",
                ),
                "| currency =",
                product.get(
                    "currency",
                    "",
                ),
            )

        products.append(
            product
        )

    return products


# =========================================================
# Main Web Search
# =========================================================

def web_search_products(
    keyword,
    region="tw",
):
    """
    Web 商品搜尋主流程：

    1. Normalize Region
    2. Cache Check
    3. SerpAPI Search
    4. Product Clean
    5. Basic Validation
    6. Cache Save

    注意：

    Web Search 不做：
    - Ranking
    - Top Product
    - User Budget Filter
    - Summary
    """

    region = normalize_region(
        region
    )

    # =====================================================
    # Cache Key
    # =====================================================

    cache_key = (
        keyword,
        region,
    )

    # =====================================================
    # Cache Hit
    # =====================================================

    if cache_key in SEARCH_CACHE:

        if DEBUG_SEARCH:

            print(
                f"[Cache Hit] "
                f"{keyword} "
                f"(region={region})"
            )

        return SEARCH_CACHE[
            cache_key
        ]

    # =====================================================
    # Search
    # =====================================================

    try:

        shopping_results = (
            fetch_shopping_results(
                keyword,
                region,
            )
        )

        # =================================================
        # Product Build
        # =================================================

        products = build_products(
            shopping_results,
            keyword,
            region,
        )

        if DEBUG_SEARCH:

            print(
                f"[Clean Products] "
                f"{len(products)}"
            )

        # =================================================
        # Cache Save
        # =================================================

        if products:

            SEARCH_CACHE[
                cache_key
            ] = products

            if DEBUG_SEARCH:

                print(
                    f"[Cache Save] "
                    f"{keyword} "
                    f"(region={region})"
                )

        return products

    # =====================================================
    # Request Error
    # =====================================================

    except requests.RequestException as e:

        print(
            f"[Web Search Error] "
            f"{e}"
        )

        return []