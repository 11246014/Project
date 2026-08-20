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


# ==================================================
# Search Strategy
# ==================================================

def build_search_strategy(need):
    """
    建立搜尋策略。

    目前 Search Strategy 不直接修改
    Primary Search Query。

    Feature Search 由 retrieve_candidates()
    根據 UserNeed 建立。
    """

    strategy = {
        "search_terms": [],
    }

    # --------------------------------------------------
    # Brand
    # --------------------------------------------------

    if need.preferences.brand:
        strategy["search_terms"].append(
            need.preferences.brand
        )

        return strategy

    # --------------------------------------------------
    # OS
    # --------------------------------------------------

    os_name = need.preferences.os

    if os_name == "iOS":
        strategy["search_terms"].append(
            "Apple Watch"
        )

    elif os_name == "Android":
        strategy["search_terms"].append(
            "Samsung"
        )

    return strategy


# ==================================================
# Async Helper
# ==================================================

def _run_async(coro):
    """
    執行 Async Function。
    """

    try:
        asyncio.get_running_loop()

    except RuntimeError:
        return asyncio.run(
            coro
        )

    raise RuntimeError(
        "Cannot execute async search inside an active event loop."
    )


# ==================================================
# Product Deduplication
# ==================================================

def normalize_product_title(product):
    """
    將商品名稱標準化，
    供去重使用。
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

    分數越高，
    代表商品資訊越完整。
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

    相同商品出現多次時，
    保留資訊較完整的版本。
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
# Feature Fallback Query
# ==================================================

def build_feature_search_queries(need):
    """
    建立 Feature Fallback Search Query。

    例如：

    device_type = 智慧手錶
    features = [GPS]

    →

    智慧手錶 GPS

    注意：

    不加入 usage。

    目的：
    避免 Primary Query 過度限制搜尋結果。
    """

    queries = []

    device_type = (
        need.device_type
        or ""
    ).strip()

    brand = (
        need.preferences.brand
        or ""
    ).strip()

    features = (
        need.features
        or []
    )

    # --------------------------------------------------
    # 每個 Feature 分開搜尋
    # --------------------------------------------------

    for feature in features:
        feature = str(
            feature
        ).strip()

        if not feature:
            continue

        query_parts = []

        # Brand
        if brand:
            query_parts.append(
                brand
            )

        # Device Type
        elif device_type:
            query_parts.append(
                device_type
            )

        # Feature
        query_parts.append(
            feature
        )

        query_parts = list(
            dict.fromkeys(
                query_parts
            )
        )

        query_parts = [
            q.strip()
            for q in query_parts
            if q and q.strip()
        ]

        if not query_parts:
            continue

        query = " ".join(
            query_parts
        )

        if query not in queries:
            queries.append(
                query
            )

    return queries


# ==================================================
# Search Helpers
# ==================================================

def search_db(search_query):
    """
    DB Search。

    DB Search 失敗不阻斷
    Web Search。
    """

    try:
        products = _run_async(
            search_db_products(
                search_query
            )
        )

        if products:
            if DEBUG_SEARCH:
                print(
                    f"[DB Search] "
                    f"{len(products)}"
                )

        else:
            if DEBUG_SEARCH:
                print(
                    "[DB Search] No Result"
                )

        return products or []

    except Exception as e:
        print(
            f"[DB Search Error] "
            f"{e}"
        )

        return []


def search_web(
    search_query,
    region,
):
    """
    Web Search。

    這裡只負責呼叫
    web_search_service。
    """

    try:
        products = web_search_products(
            search_query,
            region=region,
        )

        if products:
            if DEBUG_SEARCH:
                print(
                    f"[{region.upper()} Search] "
                    f"{len(products)}"
                )

        else:
            if DEBUG_SEARCH:
                print(
                    f"[{region.upper()} Search] "
                    f"No Result"
                )

        return products or []

    except Exception as e:
        print(
            f"[{region.upper()} Search Error] "
            f"{e}"
        )

        return []


# ==================================================
# Candidate Retrieval
# ==================================================

def retrieve_candidates(
    search_query,
    need,
):
    """
    Candidate Retrieval。

    Search Strategy：

    Phase 1
        DB + TW Primary Search

    Phase 2
        TW Feature Search

    Phase 3
        Global Primary Search

    Phase 4
        Global Feature Search

    Search Strategy 只負責：

    - 決定搜尋順序
    - 決定 fallback
    - 合併候選商品
    - 去除重複

    不負責：

    - Ranking
    - Feature Score
    - User Budget Filter
    - Summary
    """

    all_products = []

    # ==================================================
    # Phase 1
    # Primary Search
    # ==================================================

    if DEBUG_SEARCH:
        print(
            "\n========== Primary Search =========="
        )

        print(
            "[Primary Query]",
            repr(search_query),
        )

    # --------------------------------------------------
    # DB
    # --------------------------------------------------

    db_products = search_db(
        search_query
    )

    if db_products:
        all_products.extend(
            db_products
        )

    # --------------------------------------------------
    # TW
    # --------------------------------------------------

    tw_products = search_web(
        search_query,
        "tw",
    )

    if tw_products:
        all_products.extend(
            tw_products
        )

    # --------------------------------------------------
    # Primary Result
    # --------------------------------------------------

    all_products = deduplicate_products(
        all_products
    )

    if DEBUG_SEARCH:
        print(
            "[Primary Search Results]",
            len(all_products),
        )

    # ==================================================
    # Phase 2
    # Feature Fallback
    # ==================================================

    if not all_products:
        feature_queries = build_feature_search_queries(
            need
        )

        if DEBUG_SEARCH:
            print(
                "\n========== Feature Search =========="
            )

            print(
                "[Feature Queries]",
                feature_queries,
            )

        for feature_query in feature_queries:
            if DEBUG_SEARCH:
                print(
                    "[Feature Query]",
                    repr(feature_query),
                )

            tw_feature_products = search_web(
                feature_query,
                "tw",
            )

            if tw_feature_products:
                all_products.extend(
                    tw_feature_products
                )

        all_products = deduplicate_products(
            all_products
        )

        if DEBUG_SEARCH:
            print(
                "[Feature Search Results]",
                len(all_products),
            )

    # ==================================================
    # Phase 3
    # Global Primary Search
    # ==================================================

    if not all_products:
        if DEBUG_SEARCH:
            print(
                "\n========== Global Search =========="
            )

            print(
                "[Global Primary Query]",
                repr(search_query),
            )

        global_products = search_web(
            search_query,
            "global",
        )

        if global_products:
            all_products.extend(
                global_products
            )

        all_products = deduplicate_products(
            all_products
        )

        if DEBUG_SEARCH:
            print(
                "[Global Primary Results]",
                len(all_products),
            )

    # ==================================================
    # Phase 4
    # Global Feature Search
    # ==================================================

    if not all_products:
        feature_queries = build_feature_search_queries(
            need
        )

        if DEBUG_SEARCH:
            print(
                "\n========== Global Feature Search =========="
            )

        for feature_query in feature_queries:
            if DEBUG_SEARCH:
                print(
                    "[Global Feature Query]",
                    repr(feature_query),
                )

            global_feature_products = search_web(
                feature_query,
                "global",
            )

            if global_feature_products:
                all_products.extend(
                    global_feature_products
                )

        all_products = deduplicate_products(
            all_products
        )

        if DEBUG_SEARCH:
            print(
                "[Global Feature Results]",
                len(all_products),
            )

    # ==================================================
    # Final Result
    # ==================================================

    if DEBUG_SEARCH:
        print(
            "\n========== Search Final =========="
        )

        print(
            f"[Final Candidates] "
            f"{len(all_products)}"
        )

        print(
            "=================================="
        )

    return all_products