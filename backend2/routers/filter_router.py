from fastapi import APIRouter

from services.filter_service import (
    filter_products
)

router = APIRouter()


@router.post("/products/filter")
def product_filter(filters: dict):

    print("\n====== 前端清單資料 ======")

    print(filters)

    print("==========================\n")

    try:

        result = filter_products(
            filters
        )

        print(
            "[Filter Router] Success"
        )

        return result

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