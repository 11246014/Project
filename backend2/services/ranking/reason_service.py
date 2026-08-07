# services/ranking/reason_service.py

"""
Reason Service

負責：
1. 產生商品推薦原因
2. 整合 Feature、Rating、Price、Brand 推薦理由
"""

from services.ranking.constants import FEATURE_REASON

from services.ranking.helper import (
    extract_product_features,
)

# ==================================================
# Popular Brand
# ==================================================

POPULAR_BRANDS = {
    "Apple",
    "Samsung",
    "Garmin",
    "Google",
    "Huawei",
    "Amazfit",
    "COROS",
    "Polar",
    "Suunto",
}

# ==================================================
# Generate Reason
# ==================================================

def generate_reason(product):
    """
    產生商品推薦原因
    """

    reasons = []

    # ==================================================
    # Feature
    # ==================================================

    for feature in extract_product_features(product):

        reason = FEATURE_REASON.get(feature)

        if reason and reason not in reasons:
            reasons.append(reason)

    # ==================================================
    # Rating
    # ==================================================

    try:
        rating = float(product.get("rating", 0))
    except Exception:
        rating = 0

    if rating >= 4.8:
        reasons.append("高評價商品")

    # ==================================================
    # Price
    # ==================================================

    try:
        price = int(product.get("price", 0))
    except Exception:
        price = 0

    if 0 < price <= 3000:
        reasons.append("價格具競爭力")

    # ==================================================
    # Brand
    # ==================================================

    brand = product.get("brand", "")

    if brand in POPULAR_BRANDS:
        reasons.append("熱門品牌商品")

    # ==================================================
    # Remove Duplicate
    # ==================================================

    reasons = list(dict.fromkeys(reasons))

    # ==================================================
    # Return
    # ==================================================

    if reasons:
        return "、".join(reasons[:2])

    return "符合智慧穿戴需求"