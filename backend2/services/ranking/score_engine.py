# services/ranking/score_engine.py

"""
Score Engine Service

負責：
1. 商品總分計算
2. Requirement / Metadata / Brand 評分整合
3. 回傳 Ranking Score 與推薦原因
"""

from services.ranking.constants import (
    CORE_FACTOR_KEYWORDS,
    FEATURE_KEYWORDS,
    FEATURE_QUERY_TERMS,
    FEATURE_REASON,
    PRIORITY_EVIDENCE_TERMS,
    USAGE_KEYWORDS,
    USAGE_REASON,
)

from services.ranking.helper import (
    _list,
    _price,
    _text,
)

from services.ranking.metadata_score import (
    score_metadata,
)

from services.ranking.reason_service import (
    generate_reason,
)

from services.ranking.requirement_score import (
    score_requirement,
)

from services.ranking.weight_service import (
    FEATURE_BONUS,
    build_dynamic_weights,
)

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
# User Brand Match
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

# ==================================================
# Preference Score
# ==================================================

def score_preferences(
    product,
    need,
):
    """
    Preference 額外加分
    """

    score = 0

    text = _text(product)

    if (
        need.preferences
        and need.preferences.battery
        and "battery_life" not in _list(need.priorities)
    ):

        battery_terms = PRIORITY_EVIDENCE_TERMS[
            "battery_life"
        ]

        if any(
            term.lower() in text
            for term in battery_terms
        ):

            score += 10

    return score


# ==================================================
# Product Score Engine
# ==================================================

def calculate_product_score(
    product,
    need,
):

    reason_parts = []

    # ==================================================
    # Score Bucket
    # ==================================================

    base_score = 0
    requirement_score = 0
    adjustment_score = 0

    weights = build_dynamic_weights(
        need,
    )

    debug_score = []

    text = _text(product)

    features = {
        str(item).lower()
        for item in _list(
            product.get("features")
        )
    }
    if DEBUG_RANKING:
        print(
            f"[Ranking Debug] "
            f"{product.get('title')} | "
            f"product_features={features} | "
            f"product_text={text}"
        )

    requirement_score_part, reason_part, requirement_debug = score_requirement(
        product,
        need,
        weights,
    )

    requirement_score += requirement_score_part

    reason_parts.extend(reason_part)

    debug_score.extend(
        requirement_debug
    )

    # ==================================================
    # Usage
    # ==================================================

    for usage in _list(need.usage):

        keywords = USAGE_KEYWORDS.get(
            usage,
            [usage],
        )
        if DEBUG_RANKING:
            print(
                f"[Usage Debug] "
                f"usage={usage} | "
                f"keywords={keywords} | "
                f"matched={any(keyword.lower() in text for keyword in keywords)}"
            )

        if any(
            keyword.lower() in text
            for keyword in keywords
        ):

            requirement_score += weights["usage"]

            debug_score.append(
                f"Usage({usage}) +{weights['usage']}"
            )

            reason = USAGE_REASON.get(
                usage
            )

            if (
                reason
                and reason not in reason_parts
            ):
                reason_parts.append(reason)

    # ==================================================
    # Feature
    # ==================================================

    for feature in _list(need.features):

        feature_name = FEATURE_QUERY_TERMS.get(
            str(feature).lower(),
            feature,
        )

        if feature_name == "睡眠監測":
            feature_name = "睡眠"

        keywords = FEATURE_KEYWORDS.get(
            feature_name,
            [],
        )

        feature_text_match = any(
            keyword.lower() in text
            for keyword in keywords
        )

        feature_list_match = (
            feature_name.lower() in features
        )

        if DEBUG_RANKING:
            print(
                f"[Feature Debug] "
                f"feature={feature} | "
                f"feature_name={feature_name} | "
                f"keywords={keywords} | "
                f"feature_list={features} | "
                f"text_match={feature_text_match} | "
                f"list_match={feature_list_match}"
            )

        if feature_list_match or feature_text_match:

            weight = max(
                FEATURE_BONUS.get(
                    feature_name,
                    20,
                ),
                weights["feature"],
            )

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
    # ==================================================
    # Priority
    # ==================================================

    for priority in _list(need.priorities):

        evidence_terms = PRIORITY_EVIDENCE_TERMS.get(
            priority,
            [priority],
        )

        if any(
            term.lower() in text
            for term in evidence_terms
        ):

            requirement_score += weights["priority"]

            debug_score.append(
                f"Priority({priority}) +{weights['priority']}"
            )

    # ==================================================
    # Core Factor
    # ==================================================

    for priority in _list(need.priorities):

        keywords = CORE_FACTOR_KEYWORDS.get(
            priority,
            [],
        )

        if any(
            keyword.lower() in text
            for keyword in keywords
        ):

            weight = FEATURE_BONUS.get(
                priority,
                20,
            )

            requirement_score += weight

            debug_score.append(
                f"CoreFactor({priority}) +{weight}"
            )

    # ==================================================
    # Preference
    # ==================================================

    preference_score = score_preferences(
        product,
        need,
    )

    requirement_score += preference_score

    if preference_score:

        debug_score.append(
            f"Preference +{preference_score}"
        )

    # ==================================================
    # Metadata
    # ==================================================

    metadata_score, metadata_debug = score_metadata(
        product,
        need,
        weights,
    )

    base_score += metadata_score

    debug_score.extend(
        metadata_debug
    )

    # ==================================================
    # Budget
    # ==================================================

    price = _price(product)

    if (
        need.budget.max
        and price
        and price <= need.budget.max
    ):

        requirement_score += weights["budget"]

        debug_score.append(
            f"Budget +{weights['budget']}"
        )

    # ==================================================
    # Rating
    # ==================================================

    try:
        rating = float(
            product.get(
                "rating",
                0,
            )
        )

    except Exception:

        rating = 0

    rating_score = int(rating * 2)

    base_score += rating_score

    debug_score.append(
        f"Rating +{rating_score}"
    )

    # ==================================================
    # OS
    # ==================================================

    if (
        need.preferences
        and need.preferences.os
    ):

        brands = OS_BRAND_MAPPING.get(
            need.preferences.os,
            [],
        )

        brand = product.get(
            "brand",
            "",
        )

        if brand in brands:

            requirement_score += weights["os"]

            debug_score.append(
                f"OS({need.preferences.os}) +{weights['os']}"
            )

    # ==================================================
    # Brand
    # ==================================================

    brand = product.get(
        "brand",
        "",
    )

    brand_score = BRAND_SCORE.get(
        brand,
        0,
    )

    adjustment_score += brand_score

    if brand_score:

        debug_score.append(
            f"Brand({brand}) +{brand_score}"
        )

    # ==================================================
    # User Brand
    # ==================================================

    user_brand = (
        need.preferences.brand
        if need and need.preferences
        else None
    )

    if user_brand:

        user_brand = USER_BRAND_MAPPING.get(
            user_brand.lower(),
            user_brand,
        )

    if (
        user_brand
        and brand.lower() == user_brand.lower()
    ):

        requirement_score += USER_BRAND_MATCH_SCORE

        debug_score.append(
            f"UserBrand({user_brand}) +{USER_BRAND_MATCH_SCORE}"
        )

    # ==================================================
    # Final Score
    # ==================================================

    score = (
        base_score
        + requirement_score
        + adjustment_score
    )

    # ==================================================
    # Debug
    # ==================================================

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

    # ==================================================
    # Recommendation Reason
    # ==================================================

    if reason_parts:

        reason = "、".join(reason_parts)

    else:

        reason = generate_reason(product)

    return {
        "raw_score": score,
        "score": score,
        "reason": reason,
    }