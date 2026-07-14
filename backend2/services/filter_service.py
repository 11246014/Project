from services.filter_adapter import (
    adapt_filter_request,
)

from services.recommendation_pipeline import (
    recommend_from_need,
)

from services.summary_service import (
    generate_summary,
)


# =========================
# Filter Recommendation Flow
# =========================

def filter_products(filters):

    # =========================
    # Filter -> UserNeed
    # =========================

    recommendation_request = adapt_filter_request(
        filters
    )

    user_need = recommendation_request.need

    # =========================
    # Recommendation Pipeline
    # =========================

    result = recommend_from_need(
        user_need
    )

    products = result["products"]

    budget_fallback = result["budget_fallback"]

    # =========================
    # AI Recommendation Summary
    # =========================

    try:

        reply = generate_summary(

            products,

            user_need,

            budget_fallback
        )

    except Exception as e:

        print(
            f"[Filter Summary Error] {e}"
        )

        reply = (
            "目前 AI 推薦暫時無法產生，"
            "但已先列出符合條件的商品。"
        )

    # =========================
    # Debug Log
    # =========================

    print(
        f"[Filter] 找到 {len(products)} 筆商品"
    )

    for index, product in enumerate(
        products,
        start=1
    ):

        print(
            f"{index}. {product.get('name')}"
        )

    # =========================
    # API Response
    # =========================

    return {

        "success": True,

        "filters": filters,

        "user_need": user_need.to_dict(),

        "reply": reply,

        "results": products
    }