from fastapi import APIRouter

from services.filter_service import filter_products
from services.filter_recommend_service import generate_filter_recommendation

router = APIRouter()


@router.post("/products/filter")
def product_filter(filters: dict):

    results = filter_products(filters)

    ai_reply = generate_filter_recommendation(
        filters,
        results
    )

    return {
        "filters": filters,

        "reply": ai_reply,

        "results": results
    }