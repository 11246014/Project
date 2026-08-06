# product_rank_service.py

from services.ranking.constants import *

from services.ranking.helper import (
    _list,
    _price,
    _text,
    extract_product_features,
)

from services.ranking.metadata_score import score_metadata

from services.ranking.weight_service import (
    FEATURE_BONUS,
    build_dynamic_weights,
)
from services.ranking.reason_service import generate_reason

DEBUG_RANKING = True

# ==================================================
# Brand Score
# ==================================================

BRAND_SCORE = {
    "Apple": 5,
    "Garmin": 5,
    "Samsung": 4,
    "Huawei": 3,
    "Amazfit": 3,
    "Fitbit": 3,
    "Google": 4,
    "COROS": 4,
    "Polar": 4,
    "Suunto": 4,
}

# ==================================================
# User Brand Match Score
# ==================================================

USER_BRAND_MATCH_SCORE = 20

OS_BRAND_MAPPING = {
    "iOS": [
        "Apple",
    ],
    "Android": [
        "Samsung",
        "Google",
        "Huawei",
        "Amazfit",
        "Xiaomi",
    ],
}

USER_BRAND_MAPPING = {
    "apple": "Apple",
    "apple watch": "Apple",

    "garmin": "Garmin",

    "samsung": "Samsung",

    "huawei": "Huawei",

    "amazfit": "Amazfit",

    "fitbit": "Fitbit",

    "google": "Google",

    "coros": "COROS",

    "polar": "Polar",

    "suunto": "Suunto",
}


def score_preferences(product, need):
    score = 0
    text = _text(product)

    if (
        need.preferences.battery
        and "battery_life" not in _list(need.priorities)
    ):
        battery_terms = PRIORITY_EVIDENCE_TERMS["battery_life"]

        if any(
            term.lower() in text
            for term in battery_terms
        ):
            score += 10

    return score


def score_requirement(
    product,
    need,
    weights,
):

    requirement_score = 0

    reason_parts = []

    debug_score = []

    text = _text(product)

    # =========================
    # Device
    # =========================

    if need.device_type:

        device_term = DEVICE_QUERY_TERMS.get(
            need.device_type,
            need.device_type
        ).lower()

        keywords = DEVICE_KEYWORDS.get(
            need.device_type,
            [device_term]
        )

        if any(
            keyword.lower() in text
            for keyword in keywords
        ):

            requirement_score += weights["device"]

            debug_score.append(
                f"Device +{weights['device']}"
            )

    return (
        requirement_score,
        reason_parts,
        debug_score,
    )

# =========================
# Product Rank Service
# =========================

def calculate_product_score(product, need):

    reason_parts = []
    score = 0
    base_score = 0          # 基本能力
    requirement_score = 0   # 使用者需求
    adjustment_score = 0    # 品牌修正

    weights = build_dynamic_weights(need)

    debug_score = []

    text = _text(product)

    features = {
        str(item).lower()
        for item in _list(product.get("features"))
    }

    requirement_score_part, reason_part, requirement_debug = score_requirement(
        product,
        need,
        weights,
    )

    score += requirement_score_part
    requirement_score += requirement_score_part

    reason_parts.extend(reason_part)

    debug_score.extend(requirement_debug)



    # =========================
    # Usage
    # =========================

    for usage in _list(need.usage):

        keywords = USAGE_KEYWORDS.get(
            usage,
            [usage]
        )

        if any(
            keyword.lower() in text
            for keyword in keywords
        ):

            score += weights["usage"]
            requirement_score += weights["usage"]

            debug_score.append(
                f"Usage({usage}) +{weights['usage']}"
            )
            reason = USAGE_REASON.get(usage)

            if reason and reason not in reason_parts:
                reason_parts.append(reason)

    # =========================
    # Feature Score
    # =========================

    for feature in _list(need.features):

        feature_name = FEATURE_QUERY_TERMS.get(
            str(feature).lower(),
            feature
        )

        if feature_name == "睡眠監測":
            feature_name = "睡眠"

        keywords = FEATURE_KEYWORDS.get(
            feature_name,
            []
        )

        if (
            feature_name.lower() in features
            or any(
                keyword.lower() in text
                for keyword in keywords
            )
        ):

            weight = max(
                FEATURE_BONUS.get(feature_name, 20),
                weights["feature"]
            )

            score += weight
            requirement_score += weight

            debug_score.append(
                f"Feature({feature_name}) +{weight}"
            )

            reason = FEATURE_REASON.get(
                feature_name
            )

            if (
                reason
                and reason not in reason_parts
            ):
                reason_parts.append(reason)

    # =========================
    # Priority
    # =========================

    for priority in _list(need.priorities):

        evidence_terms = PRIORITY_EVIDENCE_TERMS.get(
            priority,
            [priority]
        )

        if any(
            term.lower() in text
            for term in evidence_terms
        ):

            score += weights["priority"]

            debug_score.append(
                f"Priority({priority}) +10"
            )
    # =========================
    # Core Factor
    # =========================

    for priority in _list(need.priorities):

        keywords = CORE_FACTOR_KEYWORDS.get(
            priority,
            []
        )

        if any(
            keyword.lower() in text
            for keyword in keywords
        ):
            weight = FEATURE_BONUS.get(
                priority,
                20
            )

            score += weight

            debug_score.append(
                f"CoreFactor({priority}) +{weight}"
            )

    # =========================
    # Preference
    # =========================

    preference_score = score_preferences(
        product,
        need
    )

    score += preference_score

    if preference_score:

        debug_score.append(
            f"Preference +{preference_score}"
        )

    # =========================
    # Metadata
    # =========================

    metadata_score, metadata_debug = score_metadata(
        product,
        need,
        weights,
    )

    score += metadata_score
    base_score += metadata_score

    debug_score.extend(metadata_debug)

    # =========================
    # Budget
    # =========================

    price = _price(product)
    if (
        need.budget.max
        and price
        and price <= need.budget.max
    ):
        score += weights["budget"]
        requirement_score += weights["budget"]

        debug_score.append(
            f"Budget +{weights['budget']}"
        )
    # =========================
    # Rating
    # =========================
    try:
        rating = float(
            product.get(
                "rating",
                0
            )
        )
    except Exception:
        rating = 0

    rating_score = int(rating * 2)

    score += rating_score
    base_score += rating_score

    debug_score.append(
        f"Rating +{rating_score}"
    )

    # =========================
    # OS
    # =========================
    if need.preferences.os:

        brands = OS_BRAND_MAPPING.get(
            need.preferences.os,
            []
        )

        brand = product.get(
            "brand",
            ""
        )

        if brand in brands:

            requirement_score += weights["os"]

            debug_score.append(
                f"OS({need.preferences.os}) +{weights['os']}"
            )

    # =========================
    # Brand
    # =========================

    brand = product.get(
        "brand",
        ""
    )

    # 商品品牌基礎分
    brand_score = BRAND_SCORE.get(
        brand,
        0
    )

    score += brand_score
    adjustment_score += brand_score

    if brand_score:

        debug_score.append(
            f"Brand({brand}) +{brand_score}"
        )

    # 使用者指定品牌
    user_brand = (
        need.preferences.brand
        if need and need.preferences
        else None
    )

    if user_brand:
        user_brand = USER_BRAND_MAPPING.get(
            user_brand.lower(),
            user_brand
        )

    if (
        user_brand
        and brand.lower() == user_brand.lower()
    ):
        requirement_score += USER_BRAND_MATCH_SCORE

        debug_score.append(
            f"UserBrand({user_brand}) +{USER_BRAND_MATCH_SCORE}"
        )
    score = (
        base_score
        + requirement_score
        + adjustment_score
    )

    if DEBUG_RANKING:
        print("\n========== Score ==========")
        print(product.get("title"))

        for item in debug_score:
            print(item)

        print(f"Base Score = {base_score}")
        print(f"Requirement Score = {requirement_score}")
        print(f"Adjustment Score = {adjustment_score}")
        print(f"Total = {score}")
        print("===========================\n")

    if not reason_parts:
        reason = generate_reason(product)
    else:
        reason = "、".join(reason_parts)

    return {
        "raw_score": score,
        "score": score,
        "reason": reason,
    }

def score_mapper(raw_score):

    score = int(raw_score * 0.75 + 35)

    return max(50, min(score, 95))

def rank_products(products, user_need=None):

    ranked = []

    for product in products:

        product = product.copy()

        result = calculate_product_score(
            product,
            user_need
        )

        product["match"] = result["score"]
        product["reason"] = result["reason"]

        ranked.append(product)

    ranked.sort(
        key=lambda item: (
            item.get("match", 0),
            item.get("rating", 0)
        ),
        reverse=True
    )

    return ranked