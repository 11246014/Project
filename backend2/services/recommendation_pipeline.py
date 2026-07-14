import asyncio

from services.db_search_service import search_db_products
from services.product_formatter import format_product
from services.web_search_service import web_search_products
from services.backend1_client import save_product

# ==================================================
# Search Query Mapping
# （建立搜尋關鍵字）
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
}

FEATURE_QUERY_TERMS = {
    "gps": "GPS",
    "heart_rate": "心率",
    "blood_oxygen": "血氧",
    "ecg": "ECG",
    "sleep_tracking": "睡眠監測",
    "water_resistance": "防水",
}

PRIORITY_QUERY_TERMS = {
    "battery_life": "長續航",
    "location_accuracy": "GPS",
    "value": "高CP值",
    "durability": "耐用",
    "ease_of_use": "操作簡單",
}

OS_QUERY_TERMS = {
    "iOS": "iPhone",
    "Android": "Android",
}

STYLE_MAPPING = {

    "business": [
        "商務",
        "金屬",
        "正式",
    ],

    "fashion": [
        "時尚",
        "設計",
        "AMOLED",
    ],

    "sport": [
        "運動",
        "防水",
        "GPS",
    ],
}

BATTERY_MAPPING = {

    "low": [
        "高性能",
    ],

    "medium": [
        "續航",
    ],

    "high": [
        "長續航",
    ],
}
# ==================================================
# Search Filter Mapping
# （搜尋階段硬性過濾）
# ==================================================

NEGATIVE_STYLE_KEYWORDS = {
    "business": [
        "兒童",
        "卡通",
        "玩具",
    ],
    "fashion": [
        "軍規",
        "粗獷",
    ],
}
IOS_ONLY_KEYWORDS = [
    "apple watch",
]

ANDROID_ONLY_KEYWORDS = [
    "galaxy watch",
    "wear os",
]
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
        "電池"
    ],
    "location_accuracy": [
        "gps",
        "定位",
        "高精度",
        "精準",
        "感測"
    ],
    "durability": [
        "軍規",
        "防摔",
        "耐用"
    ],
    "value": [
        "cp值",
        "超值"
    ]
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

def build_search_query(need):
    parts = []

    if need.device_type:
        parts.append(
            DEVICE_QUERY_TERMS.get(
                need.device_type,
                need.device_type
            )
        )
    else:
        parts.append("智慧穿戴")

    for usage in _list(need.usage):
        parts.append(
            USAGE_QUERY_TERMS.get(
                usage,
                usage
            )
        )

    for feature in _list(need.features):
        parts.append(
            FEATURE_QUERY_TERMS.get(
                feature,
                feature
            )
        )

    for priority in _list(need.priorities):
        parts.append(
            PRIORITY_QUERY_TERMS.get(
                priority,
                priority
            )
        )

    if (
        need.preferences.os
        and need.preferences.os != "0"
    ):

        parts.append(
            OS_QUERY_TERMS.get(
                need.preferences.os,
                need.preferences.os
            )
        )

    if need.preferences.style:

        style_keywords = STYLE_MAPPING.get(
            need.preferences.style,
            [need.preferences.style]
        )

        parts.extend(style_keywords)

    if need.preferences.battery:

        battery_keywords = BATTERY_MAPPING.get(
            need.preferences.battery,
            ["長續航"]
        )

        parts.extend(battery_keywords)

    budget_min = need.budget.min
    budget_max = need.budget.max

    if budget_min and budget_max:
        parts.append(f"{budget_min}到{budget_max}元")
    elif budget_max:
        parts.append(f"{budget_max}元以下")
    elif budget_min:
        parts.append(f"{budget_min}元以上")

    cleaned = []

    for part in parts:
        if part and part not in cleaned:
            cleaned.append(part)

    return " ".join(cleaned)


def _run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    raise RuntimeError(
        "recommend_from_need cannot run async DB search inside an active event loop"
    )

def save_candidates(products):
    for product in products:
        try:
            if product.get("title"):
                _run_async(
                    save_product(product)
                )
        except Exception as e:
            print(f"[Save Error] {e}")

def retrieve_candidates(search_query):
    candidates = []

    try:
        candidates = _run_async(
            search_db_products(search_query)
        )
    except Exception as e:
        print(f"[Pipeline DB Search Error] {e}")

    if candidates:
        return candidates

    try:
        return web_search_products(search_query)
    except Exception as e:
        print(f"[Pipeline Web Search Error] {e}")
        return []

def match_device_type(product, need):

    if not need.device_type:
        return True

    title = product.get(
        "title",
        ""
    ).lower()

    if need.device_type == "smart_ring":

        return (
            "戒指" in title
            or "指環" in title
            or "ring" in title
        )

    elif need.device_type == "smart_band":

        return (
            "手環" in title
            or "band" in title
            or "fit" in title
        )

    elif need.device_type == "smartwatch":

        return (
            "手錶" in title
            or "腕錶" in title
            or "watch" in title
        )

    return True

def match_os(product, need):

    os_type = need.preferences.os

    if not os_type:
        return True

    title = product.get(
        "title",
        ""
    ).lower()

    if os_type == "iOS":

        for keyword in ANDROID_ONLY_KEYWORDS:

            if keyword.lower() in title:
                return False

    elif os_type == "Android":

        for keyword in IOS_ONLY_KEYWORDS:

            if keyword.lower() in title:
                return False

    return True

def match_negative(product, need):

    style = need.preferences.style

    if not style:
        return True

    title = product.get(
        "title",
        ""
    ).lower()

    desc = product.get(
        "desc",
        ""
    ).lower()

    text = f"{title} {desc}"

    bad_keywords = NEGATIVE_STYLE_KEYWORDS.get(
        style,
        []
    )

    for keyword in bad_keywords:

        if keyword.lower() in text:
            return False

    return True
def hard_filter_candidates(candidates, need):
    filtered = []

    budget_fallback = False

    budget_min = need.budget.min or 0
    budget_max = need.budget.max or 0

    for product in candidates:

        if not match_device_type(
            product,
            need
        ):
            continue

        if not match_os(
            product,
            need
        ):
            continue

        if not match_negative(
            product,
            need
        ):
            continue

        price = _price(product)

        if price > 0:

            if budget_min and price < budget_min:
                continue

            if budget_max and price > budget_max:
                continue

        filtered.append(product)

    if filtered:
        return filtered, budget_fallback

    if not budget_max:
        return candidates, budget_fallback

    budget_fallback = True

    fallback_candidates = [

        product

        for product in candidates

        if match_device_type(
            product,
            need
        )
    ]

    fallback = sorted(

        fallback_candidates,

        key=lambda p: (

            _price(p) < budget_min,

            abs(_price(p) - budget_min)

        )
    )

    return fallback[:3], budget_fallback


def score_product(product, need):

    reason_parts = []

    score = 0

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

    if device_term in text:
        score += 20

    # =========================
    # Usage
    # =========================

    for usage in _list(need.usage):

        term = USAGE_QUERY_TERMS.get(
            usage,
            usage
        ).lower()

        if usage.lower() in text or term in text:

            score += 15

    # =========================
    # Feature Score
    # =========================

    for feature in _list(need.features):

        feature_name = FEATURE_QUERY_TERMS.get(
            feature,
            feature
        )

        if feature_name == "睡眠監測":
            feature_name = "睡眠"

        keywords = FEATURE_KEYWORDS.get(
            feature_name,
            []
        )

        if any(
            keyword.lower() in text
            for keyword in keywords
        ):

            score += WEIGHT_CONFIG.get(
                feature_name,
                20
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

            score += 10
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

            score += WEIGHT_CONFIG.get(
                priority,
                20
            )

    # =========================
    # Preference
    # =========================

    score += score_preferences(
        product,
        need
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
        score += 10

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
    score += int(rating * 5)

    # =========================
    # Reason
    # =========================

    if reason_parts:
        reason = "、".join(reason_parts)
    else:
        reason = "符合使用需求"

    return {
        "score": min(score, 100),
        "reason": reason,
    }


def rank_candidates(candidates, need):
    ranked = []

    for product in candidates:
        product = product.copy()
        result = score_product(product, need)
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

def format_products(products, limit=3):
    return [
        format_product(product)
        for product in products[:limit]
    ]

def recommend_from_need(
    need,
    limit=3
):
    search_query = build_search_query(need)

    candidates = retrieve_candidates(search_query)
    save_candidates(candidates)

    filtered, budget_fallback = hard_filter_candidates(
        candidates,
        need
    )

    print("\n========== PIPELINE CANDIDATES ==========")

    for index, product in enumerate(filtered, start=1):
        print(f"\n--- Candidate {index} ---")
        print("title:", product.get("title"))
        print("price:", product.get("price"))
        print("features:", product.get("features"))
        print("desc:", product.get("desc"))
        print("rating:", product.get("rating"))
        print("raw_title:", product.get("raw_title", ""))

    print("\n=========================================\n")

    ranked = rank_candidates(
        filtered,
        need
    )

    formatted_products = format_products(
        ranked,
        limit
    )

    return {
        "products": formatted_products,
        "search_query": search_query,
        "user_need": need.to_dict(),
        "budget_fallback": budget_fallback
    }
