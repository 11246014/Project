# services/ranking/requirement_score.py

"""
Requirement Score Service

負責：
1. Device Requirement 評分
2. 後續擴充 Usage、Feature、Budget 等需求評分
"""

from services.ranking.constants import (
    DEVICE_KEYWORDS,
    DEVICE_QUERY_TERMS,
)

from services.ranking.helper import (
    _text,
)

# ==================================================
# Requirement Score
# ==================================================

def score_requirement(
    product,
    need,
    weights,
):
    """
    Requirement 評分

    回傳：
    (
        requirement_score,
        reason_parts,
        debug_score,
    )
    """

    requirement_score = 0
    reason_parts = []
    debug_score = []

    text = _text(product)

    # ==================================================
    # Device
    # ==================================================

    if need.device_type:

        device_term = DEVICE_QUERY_TERMS.get(
            need.device_type,
            need.device_type,
        ).lower()

        keywords = DEVICE_KEYWORDS.get(
            need.device_type,
            [device_term],
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