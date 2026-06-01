from fastapi import APIRouter

from services.filter_service import filter_products
from services.filter_recommend_service import generate_filter_recommendation
from services.product_formatter import format_product

router = APIRouter()


@router.post("/products/filter")
def product_filter(filters: dict):

    # ===== 商品篩選 =====

    results = filter_products(filters)

    # ===== 統一商品格式 =====

    formatted_results = []

    for product in results:

        formatted_results.append(
            format_product(product)
        )

    # ===== AI 推薦文字 =====

    ai_reply = generate_filter_recommendation(
        filters,
        formatted_results
    )

    # ===== 回傳前端 =====

    return {
        "filters": filters,

        "reply": ai_reply,

        "results": formatted_results
    }