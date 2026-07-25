# product_rank_service.py

# ==================================================
# Query Mapping
# （供 Ranking 使用）
# ==================================================

DEVICE_QUERY_TERMS = {
    "smartwatch": "智慧手錶",
    "smart_band": "智慧手環",
    "smart_ring": "智慧戒指",
    "earbuds": "藍牙耳機",
}

USAGE_QUERY_TERMS = {
    "running": "跑步",
    "hiking": "登山",
    "health_monitoring": "健康監測",
    "sleep": "睡眠",

    # 中文 Mapping
    "日常": "",
    "商務": "",
    "戶外": "",
    "運動": "運動",
    "健康": "健康",
}

FEATURE_QUERY_TERMS = {
    "gps": "GPS",
    "heart_rate": "心率",
    "blood_oxygen": "血氧",
    "ecg": "ECG",
    "sleep_tracking": "睡眠監測",
    "water_resistance": "防水",
}

# ==================================================
# Score Mapping
# （商品評分）
# ==================================================

FEATURE_KEYWORDS = {

    "GPS": [
        "gps",
        "定位",
        "導航",
        "衛星",
    ],

    "睡眠": [
        "睡眠",
        "sleep",
    ],

    "血氧": [
        "血氧",
        "spo2",
    ],

    "ECG": [
        "ecg",
        "心電圖",
    ],

    "防水": [
        "防水",
        "ip68",
        "5atm",
    ],

    "心率": [
        "心率",
        "heart rate",
    ],
}

FEATURE_REASON = {

    "GPS": "支援GPS定位",

    "睡眠": "具備睡眠監測",

    "血氧": "支援血氧偵測",

    "ECG": "具備ECG心電圖功能",

    "心率": "提供心率監測",

    "防水": "具備防水功能",
}

CORE_FACTOR_KEYWORDS = {

    "battery_life": [
        "續航",
        "長續航",
        "電池",
    ],

    "location_accuracy": [
        "gps",
        "定位",
        "高精度",
        "精準",
        "感測",
    ],

    "durability": [
        "軍規",
        "防摔",
        "耐用",
    ],

    "value": [
        "cp值",
        "超值",
    ],
}

PRIORITY_EVIDENCE_TERMS = {

    "battery_life": [
        "長續航",
        "強勢續航",
        "超高續航",
        "續航",
        "solar",
        "太陽能",
    ],

    "location_accuracy": [
        "gps",
        "gps定位",
        "定位",
    ],

    "durability": [
        "耐用",
        "堅固",
        "軍規",
        "防摔",
    ],

    "ease_of_use": [
        "操作簡單",
        "簡單操作",
        "容易使用",
        "易用",
    ],
}

# ==================================================
# Score Config
# （權重設定）
# ==================================================

WEIGHT_CONFIG = {

    "GPS": 30,
    "睡眠": 30,
    "血氧": 35,
    "ECG": 40,
    "防水": 20,
    "心率": 25,

    "battery_life": 50,
    "durability": 50,
    "location_accuracy": 20,
    "value": 35,
}

# ==================================================
# Base Score Weight
# （基礎權重，可依需求動態調整）
# ==================================================

SCORE_WEIGHT = {
    "device": 20,
    "usage": 15,
    "priority": 10,
    "budget": 10,
    "rating": 1,
}

# ==================================================
# Brand Score
# ==================================================

BRAND_SCORE = {

    "Apple": 15,

    "Garmin": 15,

    "Samsung": 12,

    "Huawei": 10,

    "Amazfit": 10,

    "Fitbit": 10,

    "Google": 10,

    "COROS": 12,

    "Polar": 12,

    "Suunto": 12,
}

# ==================================================
# User Brand Match Score
# ==================================================

USER_BRAND_MATCH_SCORE = 30

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

DEVICE_KEYWORDS = {
    "smartwatch": [
        "智慧手錶",
        "apple watch",
        "galaxy watch",
        "garmin",
        "amazfit",
        "huawei watch",
        "pixel watch",
        "ticwatch",
    ],

    "smart_band": [
        "智慧手環",
        "smart band",
        "mi band",
        "fitbit inspire",
    ],

    "smart_ring": [
        "智慧戒指",
        "smart ring",
        "oura",
        "ringconn",
    ],

    "earbuds": [
        "藍牙耳機",
        "airpods",
        "galaxy buds",
        "buds",
        "earbuds",
    ]
}
# =========================
# Helper Functions
# =========================

def build_dynamic_weights(need):

    weights = SCORE_WEIGHT.copy()

    if need.usage:
        weights["usage"] = 40

    return weights

def extract_product_features(product):

    found = []

    features = _list(product.get("features"))

    for feature in features:

        feature = str(feature).strip()

        if feature and feature not in found:
            found.append(feature)

    return found

def _list(value):
    if not value:
        return []

    if isinstance(value, list):
        return value

    return [value]


def _text(product):
    return " ".join(
        str(product.get(key, ""))
        for key in (
            "title",
            "raw_title",
            "name",
            "desc",
            "description"
        )
    ).lower()


def _price(product):
    try:
        return int(product.get("price", 0) or 0)
    except Exception:
        return 0


def generate_reason(product):

    features = extract_product_features(product)

    if not features:
        return "符合使用需求"

    reasons = []

    for feature in features:

        reason = FEATURE_REASON.get(feature)

        if reason:
            reasons.append(reason)

    if reasons:
        return "、".join(reasons)

    return "、".join(features[:3])

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

# =========================
# Product Rank Service
# =========================

def calculate_product_score(product, need):

    reason_parts = []

    score = 0

    weights = build_dynamic_weights(need)

    debug_score = []

    text = _text(product)

    features = {
        str(item).lower()
        for item in _list(product.get("features"))
    }

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

        if any(keyword.lower() in text for keyword in keywords):
            score += weights["device"]

            debug_score.append(
                f"Device +{weights['device']}"
            )

    # =========================
    # Usage
    # =========================

    for usage in _list(need.usage):

        term = USAGE_QUERY_TERMS.get(
            usage,
            usage
        ).lower()

        if usage.lower() in text or term in text:

            score += weights["usage"]

            debug_score.append(
                f"Usage({usage}) +15"
            )
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

            weight = WEIGHT_CONFIG.get(
                feature_name,
                20
            )

            score += weight

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
            weight = WEIGHT_CONFIG.get(
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
    # Budget
    # =========================

    price = _price(product)
    if (
        need.budget.max
        and price
        and price <= need.budget.max
    ):
        score += weights["budget"]

        debug_score.append(
            "Budget +10"
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

    rating_score = int(rating * 5)

    score += rating_score

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

            score += 25

            debug_score.append(
                f"OS({need.preferences.os}) +25"
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
        score += USER_BRAND_MATCH_SCORE

        debug_score.append(
            f"UserBrand({user_brand}) +{USER_BRAND_MATCH_SCORE}"
        )
    print("\n========== Score ==========")
    print(product.get("title"))

    for item in debug_score:
        print(item)

    print(f"Total = {score}")
    print("===========================\n")

    return {
        "score": min(score,100),
        "reason": generate_reason(product),
    }

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