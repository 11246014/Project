# services/ranking/metadata_score.py

"""
Metadata Score Service

負責：
1. Apple Watch 系列評分
2. 商品 Metadata 加分
"""


# ==================================================
# Metadata Score
# ==================================================

def score_metadata(
    product,
    need,
    weights,
):
    """
    Metadata 評分

    回傳：
    (
        metadata_score,
        debug_score,
    )
    """

    metadata_score = 0
    debug_score = []

    series = product.get("series")

    # ==================================================
    # Apple Watch Series
    # ==================================================

    if series == "Ultra":

        metadata_score += 3
        debug_score.append("Metadata(Ultra) +3")

    elif series == "Series":

        metadata_score += 2
        debug_score.append("Metadata(Series) +2")

    elif series == "SE":

        metadata_score += 1
        debug_score.append("Metadata(SE) +1")

    return (
        metadata_score,
        debug_score,
    )