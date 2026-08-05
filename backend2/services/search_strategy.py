import asyncio

from services.db_search_service import (
    search_db_products,
)

from services.web_search_service import (
    web_search_products,
)

# ==================================================
# Search Strategy
# ==================================================

OS_SEARCH_TERMS = {
    "iOS": ["Apple Watch"],
    "Android": ["Samsung"],
}


def build_search_strategy(need):

    strategy = {
        "search_terms": []
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

    db_products = []

    try:

        db_products = _run_async(
            search_db_products(search_query)
        )

    except Exception as e:

        print(
            f"[DB Search Error] {e}"
        )

    # 第一版保持目前策略
    # 有 DB 就回 DB
    if db_products:

        return db_products

    try:

        return web_search_products(
            search_query
        )

    except Exception as e:

        print(
            f"[Web Search Error] {e}"
        )

        return []