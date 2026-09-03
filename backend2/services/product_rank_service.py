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

from services.backend1_client import (
    get_sponsors,
)

# ==================================================
# Match Score
# ==================================================

def calculate_match_score(raw_score):
    """
    將 Raw Score 轉成前端展示用 Match (%)

    原則：
    - 保留原本分數差距
    - 低於 60 時平滑拉高
    - 60 ~ 100 基本保留
    - 超過 100 時壓回 100 以下
    """

    score = float(raw_score)

    # 低於 60：往 60 拉近，但保留差距
    if score < 60:
        score = 60 + (score * 0.22)

    # 超過 100：壓縮到 100 以下
    elif score > 100:
        score = 100 - ((score - 100) * 0.5)

    score = round(score)

    return max(
        60,
        min(score, 99)
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

        sponsors = get_sponsors()

        sponsor_boost_rate = 0
        is_sponsored = False

        product_brand = str(
            product.get(
                "brand",
                ""
            )
        ).strip().lower()

        for sponsor in sponsors:

            sponsor_brand = str(
                sponsor.get(
                    "brand_name",
                    ""
                )
            ).strip().lower()

            if product_brand == sponsor_brand:

                sponsor_boost_rate = float(
                    sponsor.get(
                        "boost_rate",
                        0
                    )
                )

                is_sponsored = (
                    sponsor_boost_rate > 0
                )

                break

        final_score = calculate_final_score(
            base_score,
            sponsor_boost_rate,
        )

        product["final_score"] = final_score

        product["is_sponsored"] = is_sponsored

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
                    "final_score",
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
                    "final_score",
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
    # Match Score Display
    # ==================================================
    # 真正的 Ranking 已經完成，
    # 這裡只調整前端顯示用的 match，
    # 不影響 final_score 與實際排名。

    previous_raw_score = None
    tie_offset = 0

    for product in ranked:

        current_raw_score = product.get(
            "raw_score",
            0
        )

        if current_raw_score == previous_raw_score:
            tie_offset += 1
        else:
            tie_offset = 0

        display_score = max(
            60,
            product.get("base_score", 60) - tie_offset
        )

        product["match"] = display_score

        previous_raw_score = current_raw_score

    # ==================================================
    # Return
    # ==================================================

    return ranked