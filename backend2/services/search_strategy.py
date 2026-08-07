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
# Candidate Retrieval
# ==================================================

def retrieve_candidates(search_query):
    """
    取得搜尋候選商品

    搜尋流程：
    1. Database Search
    2. Web Search（DB 無結果時）
    """

    db_products = []

    # =========================
    # Database Search
    # =========================

    try:

        db_products = _run_async(
            search_db_products(search_query)
        )

    except Exception as e:

        if DEBUG_SEARCH:
            print(
                f"[DB Search Error] {e}"
            )

    if db_products:

        if DEBUG_SEARCH:
            print(
                f"[DB Search] {len(db_products)} Products"
            )

        return db_products

    # =========================
    # Web Search
    # =========================

    try:

        if DEBUG_SEARCH:
            print(
                "[Search Fallback] Web Search"
            )

        return web_search_products(
            search_query
        )

    except Exception as e:

        print(
            f"[Web Search Error] {e}"
        )

        return []