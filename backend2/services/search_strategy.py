# services/search_strategy.py

import asyncio

from services.db_search_service import (
    search_db_products,
)
from services.web_search_service import (
    web_search_products,
)

# ==================================================
# Search Config
# ==================================================

DEBUG_SEARCH = True

OS_SEARCH_TERMS = {
    "iOS": [
        "Apple Watch",
    ],
    "Android": [
        "Samsung",
    ],
}

# ==================================================
# Search Strategy
# ==================================================

def build_search_strategy(need):
    """
    建立搜尋策略

    目前：
    1. 已指定品牌則不額外補搜尋詞
    2. 依照 OS 補充搜尋建議

    （目前尚未正式套用於搜尋流程）
    """

    strategy = {
        "search_terms": [],
    }

    # 已指定品牌，不補搜尋策略
    if need.preferences.brand:
        return strategy

    os_name = need.preferences.os

    if os_name in OS_SEARCH_TERMS:

        strategy["search_terms"].extend(
            OS_SEARCH_TERMS[os_name]
        )

    return strategy


# ==================================================
# Async Helper
# ==================================================

def _run_async(coro):
    """
    執行 Async Function
    """

    try:
        asyncio.get_running_loop()

    except RuntimeError:
        return asyncio.run(coro)

    raise RuntimeError(
        "Cannot execute async search inside an active event loop."
    )

# ==================================================
# Product Deduplication
# ==================================================

def normalize_product_title(product):
    """
    將商品名稱標準化，供去重使用。
    """

    title = product.get(
        "title",
        "",
    )

    if not title:
        return ""

    title = title.strip().lower()

    return " ".join(
        title.split()
    )

def get_product_completeness(product):
    """
    計算商品資料完整度。

    分數越高，代表商品資訊越完整。
    """

    score = 0

    if product.get("link"):
        score += 5

    if product.get("price"):
        score += 2

    if product.get("image"):
        score += 2

    if product.get("rating"):
        score += 1

    if product.get("brand"):
        score += 1

    if product.get("desc"):
        score += 1

    return score

def deduplicate_products(products):
    """
    移除重複商品。

    若相同商品出現多次，
    保留資訊完整度較高的版本。
    """

    unique_products = {}
    
    for product in products:

        title = normalize_product_title(
            product
        )

        if not title:
            continue

        current_score = get_product_completeness(
            product
        )

        existing_product = unique_products.get(
            title
        )

        if existing_product is None:

            unique_products[title] = product

            continue

        existing_score = get_product_completeness(
            existing_product
        )

        if current_score > existing_score:

            unique_products[title] = product

    return list(
        unique_products.values()
    )

# ==================================================
# Candidate Retrieval
# ==================================================

def retrieve_candidates(search_query):
    """
    Candidate Retrieval

    Search Priority
    1. Database
    2. Taiwan Shopping
    3. Global Shopping (Fallback)
    """

    # =========================
    # Candidate Pool
    # =========================

    all_products = []

    # =========================
    # Database
    # =========================

    db_products = []
    try:

        db_products = _run_async(
            search_db_products(search_query)
        )

    except Exception as e:

        print(
            f"[DB Search Error] {e}"
        )

    if db_products:

        if DEBUG_SEARCH:
            print(
                f"[DB Search] {len(db_products)}"
            )

        all_products.extend(
            db_products
        )

    # =========================
    # Taiwan Search
    # =========================

    try:

        tw_products = web_search_products(
            search_query,
            region="tw",
        )

        if tw_products:

            if DEBUG_SEARCH:
                print(
                    f"[TW Search] {len(tw_products)}"
                )

            all_products.extend(
                tw_products
            )

        else:

            if DEBUG_SEARCH:
                print(
                    "[TW Search] No Result"
                )

    except Exception as e:

        print(
            f"[TW Search Error] {e}"
        )

    # =========================
    # Global Search (Fallback)
    # =========================

    if all_products:

        if DEBUG_SEARCH:
            print(
                f"[Hybrid Search] "
                f"DB + TW = {len(all_products)}"
            )

        all_products = deduplicate_products(
            all_products
        )

        if DEBUG_SEARCH:
            print(
                f"[Hybrid Search] "
                f"After Dedup = {len(all_products)}"
            )

        return all_products


    try:

        global_products = web_search_products(
            search_query,
            region="global",
        )

        if global_products:

            if DEBUG_SEARCH:
                print(
                    f"[Global Search] "
                    f"{len(global_products)}"
                )

            all_products.extend(
                global_products
            )

        else:

            if DEBUG_SEARCH:
                print(
                    "[Global Search] No Result"
                )

        all_products = deduplicate_products(
            all_products
        )

        if DEBUG_SEARCH:
            print(
                f"[Hybrid Search] "
                f"After Dedup = {len(all_products)}"
            )

        return all_products

    except Exception as e:

        print(
            f"[Global Search Error] {e}"
        )

        return all_products