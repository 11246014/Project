from fastapi import APIRouter

from models.schemas import UserRequest
from services.recommendation_service import recommend_products

router = APIRouter()

@router.post("/ai/recommend")
def ai_recommend(req: UserRequest):

    result = recommend_products(req.message)

    return result