from fastapi import APIRouter

from services.recommendation_service import recommend_products

router = APIRouter()


@router.post("/ai/recommend")
def ai_recommend(data: dict):

    user_message = data.get("message", "")

    result = recommend_products(user_message)

    return result