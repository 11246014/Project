from fastapi import APIRouter

from services.filter_service import filter_products
from services.filter_recommend_service import (
    generate_filter_recommendation
)
from services.product_formatter import (
    format_product
)

router = APIRouter()


@router.post("/products/filter")
def product_filter(filters: dict):

    try:

        # ===== 商品篩選 =====

        results = filter_products(
            filters
        )

        print(
            f"[Filter] 找到 {len(results)} 筆商品"
        )

        # ===== 統一商品格式 =====

        formatted_results = []

        for product in results:

            formatted_results.append(
                format_product(product)
            )

        # ===== AI 推薦文字 =====

        try:

            ai_reply = (
                generate_filter_recommendation(
                    filters,
                    formatted_results
                )
            )

        except Exception as e:

            print(
                f"[Filter AI Error] {e}"
            )

            ai_reply = (
                "目前 AI 推薦暫時無法產生，"
                "但已先列出符合條件的商品。"
            )

        # ===== 回傳前端 =====

        return {

            "success": True,

            "filters": filters,

            "reply": ai_reply,

            "results": formatted_results
        }

    except Exception as e:

        print(
            f"[Filter Router Error] {e}"
        )

        return {

            "success": False,

            "reply": "商品篩選系統暫時發生問題",

            "results": [],

            "error": str(e)
        }