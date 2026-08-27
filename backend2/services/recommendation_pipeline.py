# recommendation_pipeline.py

from services.product_formatter import (
    format_product,
)

from services.product_rank_service import (
    rank_products,
)

from services.search_filter_service import (
    hard_filter_candidates,
)

from services.search_strategy import (
    retrieve_candidates,
)

from services.product_link_service import (
    fetch_immersive_product,
)

from services.search_query_builder import (
    USAGE_MAPPING,
)

from services.backend1_client import (
    log_recommendation_event,
    save_product,
)


# ==================================================
# Pipeline Config
# ==================================================

DEBUG_PIPELINE = True


# ==================================================
# Product Format
# ==================================================

def format_products(products, limit=3):
    """
    將商品轉換成 Frontend 格式
    """

    return [
        format_product(product)
        for product in products[:limit]
    ]


# ==================================================
# Recommendation Pipeline
# ==================================================

def recommend_from_need(
    need,
    limit=3,
):
    """
    推薦流程

    1. Search
    2. Search Filter
    3. Ranking
    4. Top Products
    5. Resolve Product Links
    6. Save Products to Backend1
    7. Product Format
    """

    if DEBUG_PIPELINE:
        print(
            "need.brand =",
            need.preferences.brand,
        )

    search_query = need.search_query

    # =========================
    # Filter Search Query
    # =========================

    if not search_query:

        query_parts = []

        # Brand
        if need.preferences.brand:
            query_parts.append(
                need.preferences.brand
            )

        # Device Type
        if need.device_type:
            query_parts.append(
                need.device_type
            )

        # Usage
        for usage in need.usage:

            mapped_usage = USAGE_MAPPING.get(
                usage,
                usage,
            )

            if mapped_usage:
                query_parts.append(
                    mapped_usage
                )

        # Remove Duplicate
        query_parts = list(
            dict.fromkeys(
                query_parts
            )
        )

        search_query = " ".join(
            str(part).strip()
            for part in query_parts
            if part and str(part).strip()
        )

    # =========================
    # Search
    # =========================

    candidates = retrieve_candidates(
        search_query,
        need,
    )

    if DEBUG_PIPELINE:
        print(
            f"[Candidates] {len(candidates)}"
        )

    # =========================
    # Search Filter
    # =========================

    filtered, budget_fallback = (
        hard_filter_candidates(
            candidates,
            need,
        )
    )
    # =========================
    # Ranking
    # =========================

    ranked = rank_products(
        filtered,
        need,
    )

    if DEBUG_PIPELINE:

        print("\n========== Ranked ==========")

        for idx, product in enumerate(
            ranked[:5],
            start=1,
        ):

            print(
                f"{idx}. "
                f"{product.get('title','')} | "
                f"Score={product.get('match',0)} | "
                f"Reason={product.get('reason','')}"
            )

        print("============================")

        print(
            f"[After Ranking] {len(ranked)}"
        )

    # =========================
    # Top Products
    # =========================

    top_products = ranked[:limit]

    if DEBUG_PIPELINE:
        print(
            f"[Top Products] {len(top_products)}"
        )

    # =========================
    # Resolve Product Links
    # =========================

    for product in top_products:

        api_url = product.get(
            "immersive_product_api",
            "",
        )

        if not api_url:

            if DEBUG_PIPELINE:
                print(
                    "[Product Link] No Immersive API:",
                    product.get(
                        "title",
                        "",
                    )
                )

            continue

        link = fetch_immersive_product(
            api_url,
        )

        if link:

            # =========================
            # Save Real E-commerce Link
            # =========================

            product["link"] = link

            if DEBUG_PIPELINE:
                print(
                    "[Product Link] Resolved:",
                    product.get(
                        "title",
                        "",
                    )
                )

                print(
                    "Link:",
                    link,
                )

            # =========================
            # Save Product to Backend1
            # =========================

            if DEBUG_PIPELINE:
                print(
                    "[Product DB] Saving:",
                    product.get(
                        "title",
                        "",
                    )
                )

            save_product(
                product
            )

        elif DEBUG_PIPELINE:

            print(
                "[Product Link] Failed:",
                product.get(
                    "title",
                    "",
                )
            )

    # =========================
    # Format
    # =========================

    formatted_products = format_products(
        top_products,
    )

    # =========================
    # Log Recommendation Event
    # =========================
    # 推薦流程完成後，將匿名化需求快照與最終推薦結果
    # 送給 Backend1，寫入 recommendation_events。
    # 統計紀錄失敗不應影響推薦結果本身。
    log_recommendation_event(
        need,
        formatted_products,
    )

    if DEBUG_PIPELINE:
        print(
            f"[Formatted] {len(formatted_products)}"
        )

    return {
        "products": formatted_products,
        "search_query": search_query,
        "user_need": need.to_dict(),
        "budget_fallback": budget_fallback,
    }