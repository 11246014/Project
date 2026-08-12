# services/ranking/metadata_score.py

"""
Metadata Score Service

負責：
1. Apple Watch 系列評分
2. 商品 Metadata 加分
"""
# ==================================================
# Metadata Config
# ==================================================

SERIES_SCORE = {

    "Apple": {
        "Ultra": 3,
        "Series": 2,
        "SE": 1,
    },

    "Garmin": {
        "Fenix": 4,
        "Forerunner": 3,
        "Instinct": 3,
        "Venu": 2,
        "Vivoactive": 2,
    },

    "Samsung": {
        "Ultra": 3,
        "Classic": 2,
        "Galaxy Watch": 2,
    },

    "Google": {
        "Pixel Watch": 2,
    },

    "Huawei": {
        "GT": 2,
        "Fit": 1,
        "Ultimate": 3,
    },

    "Amazfit": {
        "T-Rex": 3,
        "Balance": 3,
        "GTR": 2,
        "GTS": 2,
        "Bip": 1,
        "Active": 2,
    },

    "COROS": {
        "Vertix": 4,
        "Apex": 3,
        "Pace": 3,
    },

    "Polar": {
        "Vantage": 3,
        "Ignite": 2,
        "Pacer": 2,
    },

    "Suunto": {
        "Vertical": 4,
        "Race": 3,
    },
}

FEATURE_SCORE = {
    "GPS": 2,
    "雙頻GPS": 3,
    "AMOLED": 1,
    "ECG": 2,
    "血氧": 1,
    "睡眠": 1,
    "NFC": 1,
    "LTE": 2,
}

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

    brand = product.get("brand")
    series = product.get("series")

    series_score = (
        SERIES_SCORE
        .get(brand, {})
        .get(series, 0)
    )

    if series_score:

        metadata_score += series_score

        debug_score.append(
            f"Metadata({brand} {series}) +{series_score}"
        )

    return (
        metadata_score,
        debug_score,
    )