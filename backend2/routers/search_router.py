from fastapi import APIRouter

from services.search_service import search_products

router = APIRouter()

@router.get("/products/search")
def product_search(keyword: str):

    results = search_products(keyword)

    return {
        "keyword": keyword,
        "results": results
    }