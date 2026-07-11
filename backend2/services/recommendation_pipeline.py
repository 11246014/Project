import asyncio

from services.db_search_service import search_db_products
from services.filter_recommend_service import generate_filter_recommendation
from services.product_formatter import format_product
from services.web_search_service import web_search_products


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

    for product in candidates:
        price = _price(product)

        if price > 0:
            if need.budget.min and price < need.budget.min:
                continue

            if need.budget.max and price > need.budget.max:
                continue

        filtered.append(product)

    return filtered


def score_product(product, need):
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
        term = FEATURE_QUERY_TERMS.get(feature, feature).lower()

        if feature in features or feature in text or term in text:
            score += 25

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

    return min(score, 100)


def rank_candidates(candidates, need):
    ranked = []

    for product in candidates:
        product = product.copy()
        product["match"] = score_product(product, need)
        ranked.append(product)

    ranked.sort(
        key=lambda item: (
            item.get("match", 0),
            item.get("rating", 0)
        ),
        reverse=True
    )

    return ranked


def summarize_recommendation(need, products):
    if not products:
        return "目前沒有找到符合條件的推薦商品。"

    try:
        result = generate_filter_recommendation(
            need.to_dict(),
            products
        )

        if result and result.strip():
            return result

        return "已根據你的需求整理出以下推薦商品。"

    except Exception as e:
        print(f"[Pipeline Summary Error] {e}")
        return "已根據你的需求整理出以下推薦商品。"


def recommend_from_need(
    need,
    limit=3,
    generate_summary=True
):
    search_query = build_search_query(need)

    candidates = retrieve_candidates(search_query)

    filtered = hard_filter_candidates(
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

    formatted_products = [
        format_product(product)
        for product in ranked[:limit]
    ]

    if generate_summary:
        summary = summarize_recommendation(
            need,
            formatted_products
        )
    else:
        summary = ""

    return {
        "summary": summary,
        "products": formatted_products,
        "search_query": search_query,
        "user_need": need.to_dict()
    }
