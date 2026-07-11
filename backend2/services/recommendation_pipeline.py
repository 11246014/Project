import asyncio

from services.db_search_service import search_db_products
from services.product_formatter import format_product
from services.web_search_service import web_search_products
from services.backend1_client import save_product

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

    if need.preferences.os:
        parts.append(need.preferences.os)

    if need.preferences.style:
        parts.append(need.preferences.style)

    if need.preferences.battery:
        parts.append(
            PRIORITY_QUERY_TERMS.get(
                "battery_life",
                "長續航"
            )
        )

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


def hard_filter_candidates(candidates, need):
    filtered = []

    budget_fallback = False

    budget_min = need.budget.min or 0
    budget_max = need.budget.max or 0

    for product in candidates:

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

    fallback = sorted(
        candidates,
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

    if need.device_type:
        device_term = DEVICE_QUERY_TERMS.get(
            need.device_type,
            need.device_type
        ).lower()

        if need.device_type in text or device_term in text:
            score += 20

    for usage in _list(need.usage):
        term = USAGE_QUERY_TERMS.get(usage, usage).lower()

        if usage in text or term in text:
            score += 15

    for feature in _list(need.features):

        feature = feature.lower()

        if feature == "gps":

            if "gps" in features or "gps" in text:

                score += 40
                reason_parts.append("支援GPS定位")

        elif feature in ["sleep_tracking", "sleep"]:

            if "睡眠" in features or "睡眠" in text:

                score += 40
                reason_parts.append("具備睡眠監測")

        elif feature == "heart_rate":

            if "心率" in features or "心率" in text:

                score += 30
                reason_parts.append("提供心率監測")

        elif feature == "blood_oxygen":

            if "血氧" in features or "血氧" in text:

                score += 30
                reason_parts.append("支援血氧偵測")

        elif feature == "ecg":

            if "ecg" in features or "心電圖" in text:

                score += 30
                reason_parts.append("具備ECG心電圖功能")

        elif feature == "water_resistance":

            if "防水" in features or "防水" in text:

                score += 20
                reason_parts.append("具備防水功能")

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

    score += score_preferences(product, need)

    price = _price(product)

    if need.budget.max and price and price <= need.budget.max:
        score += 10

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
