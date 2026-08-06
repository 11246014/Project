# services/product_rank_service.py

"""
Product Rank Service

負責：
1. 商品排序
2. Raw Score -> Match Score 轉換
3. 回傳前端排序結果
"""

from services.ranking.score_engine import (
    calculate_product_score,
)


# ==================================================
# Match Score
# ==================================================

def calculate_match_score(raw_score):
    """
    將 Raw Score 映射成前端顯示的 Match (%)
    """

    score = int(raw_score * 0.75 + 35)

    return max(50, min(score, 95))


# ==================================================
# Product Ranking
# ==================================================

def rank_products(
    products,
    user_need=None,
):
    """
    商品排序主流程
    """

    ranked = []

    for product in products:

        product = product.copy()

        result = calculate_product_score(
            product,
            user_need,
        )

        product["raw_score"] = result["raw_score"]

        product["match"] = calculate_match_score(
            result["raw_score"]
        )

        product["reason"] = result["reason"]

        ranked.append(product)

    ranked.sort(
        key=lambda item: (
            item.get("raw_score", 0),
            item.get("rating", 0),
        ),
        reverse=True,
    )

    return ranked