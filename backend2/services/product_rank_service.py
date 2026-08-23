# services/product_rank_service.py

"""
Product Rank Service

負責：
1. 商品排序
2. Raw Score -> Match Score 轉換
3. Base Score -> Final Score
4. 回傳前端排序結果
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

    score = round(raw_score)

    return max(
        0,
        min(score, 100)
    )


# ==================================================
# Final Score
# ==================================================

def calculate_final_score(
    base_score,
    sponsor_boost_rate=0,
):
    """
    計算合作加權後的最終排序分數

    目前 sponsor_boost_rate 預設為 0，
    等之後接上 Backend1 的合作廠商資料後，
    再使用實際的 boost rate。
    """

    return base_score + (
        base_score * sponsor_boost_rate
    )


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

        # ==================================================
        # Score Engine
        # ==================================================

        result = calculate_product_score(
            product,
            user_need,
        )

        product["raw_score"] = result["raw_score"]

        product["required_feature_status"] = result[
            "required_feature_status"
        ]

        # ==================================================
        # Base Score
        # ==================================================

        base_score = calculate_match_score(
            result["raw_score"]
        )

        product["base_score"] = base_score

        # ==================================================
        # Sponsor Boost
        # ==================================================
        # 目前尚未接 Backend1 Sponsor API
        # 因此 boost rate 暫時為 0。
        # ==================================================

        sponsor_boost_rate = 0

        final_score = calculate_final_score(
            base_score,
            sponsor_boost_rate,
        )

        product["final_score"] = final_score

        product["is_sponsored"] = False

        # ==================================================
        # 舊前端欄位
        # ==================================================
        # match 保留原本 API 格式，
        # 避免影響目前 Flutter 前端。
        # ==================================================

        product["match"] = base_score

        product["reason"] = result["reason"]

        ranked.append(product)

    # ==================================================
    # Ranking Sort
    # ==================================================

    budget_max = None

    if (
        user_need
        and user_need.budget
        and user_need.budget.max
    ):
        budget_max = user_need.budget.max

    # ==================================================
    # Price Distance
    # ==================================================

    def price_distance(product):

        if budget_max is None:
            return float("inf")

        try:
            price = float(
                product.get(
                    "price",
                    0
                )
            )

        except (
            TypeError,
            ValueError
        ):
            return float("inf")

        if price <= 0:
            return float("inf")

        return abs(
            price - budget_max
        )

    # ==================================================
    # Budget Fallback
    # ==================================================

    # 如果所有候選商品都超過預算，
    # 代表目前是 Budget Fallback，
    # 此時優先選擇最接近使用者預算的商品。

    budget_fallback = (
        budget_max is not None
        and len(ranked) > 0
        and all(
            price_distance(product) > 0
            for product in ranked
        )
    )

    # ==================================================
    # Ranking Sort
    # ==================================================

    if budget_fallback:

        ranked.sort(
            key=lambda item: (
                item.get(
                    "raw_score",
                    0
                ),
                -price_distance(item),
                item.get(
                    "rating",
                    0
                ),
            ),
            reverse=True,
        )

    else:

        ranked.sort(
            key=lambda item: (
                item.get(
                    "raw_score",
                    0
                ),
                item.get(
                    "rating",
                    0
                ),
            ),
            reverse=True,
        )

    # ==================================================
    # Return
    # ==================================================

    return ranked