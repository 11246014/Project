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
    4. Product Format
    """

    if DEBUG_PIPELINE:
        print(
            "need.brand =",
            need.preferences.brand,
        )

    search_query = need.search_query

    if DEBUG_PIPELINE:
        print(
            "[Pipeline Search Query]",
            repr(search_query),
        )

    # =========================
    # Search
    # =========================

    candidates = retrieve_candidates(
        search_query
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

    if DEBUG_PIPELINE:
        print(
            f"[After Filter] {len(filtered)}"
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
        ranked,
        limit,
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