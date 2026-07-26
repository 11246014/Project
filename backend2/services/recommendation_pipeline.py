#recommendation_pipeline.py
import asyncio

from services.db_search_service import search_db_products
from services.product_formatter import format_product
from services.web_search_service import web_search_products
from services.backend1_client import save_product
from services.product_rank_service import (
    rank_products,
    DEVICE_QUERY_TERMS,
    USAGE_QUERY_TERMS,
    FEATURE_QUERY_TERMS,
)

# ==================================================
# Search Query Mapping
# （建立搜尋關鍵字）
# ==================================================

PRIORITY_QUERY_TERMS = {
    "battery_life": "長續航",
    "location_accuracy": "GPS",
    "value": "高CP值",
    "durability": "耐用",
    "ease_of_use": "操作簡單",
}

OS_QUERY_TERMS = {
    "iOS": "Apple Watch",
    "Android": "Galaxy Watch",
}

STYLE_MAPPING = {

    "business": [
        "商務",
    ],

    "fashion": [
        "時尚",
    ],

    "sport": [
        "運動",
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
    

def build_search_query(need):
    parts = []

    print("need.usage =", need.usage)

    if need.preferences.brand:
        parts.append(
            need.preferences.brand
        )

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

        mapped = USAGE_QUERY_TERMS.get(
            usage,
            usage
        )

        # 日常、商務、戶外等沒有搜尋價值就略過
        if mapped:
            parts.append(mapped)

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
        and need.preferences.os not in (
            "0",
            "Cross",
            "cross",
        )
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
            []
        )

        if style_keywords:
            parts.append(style_keywords[0])

    if need.preferences.battery:

        battery_keywords = BATTERY_MAPPING.get(
            need.preferences.battery,
            []
        )

        if battery_keywords:
            parts.append(battery_keywords[0])

    budget_min = need.budget.min
    budget_max = need.budget.max

    # if budget_min and budget_max:
    #     parts.append(f"{budget_min}到{budget_max}元")
    # elif budget_max:
    #     parts.append(f"{budget_max}元以下")
    # elif budget_min:
    #     parts.append(f"{budget_min}元以上")

    cleaned = []

    for part in parts:

        if not part:
            continue

        if part not in cleaned:
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

# def save_candidates(products):
#     for product in products:
#         try:
#             if product.get("title"):
#                 _run_async(
#                     save_product(product)
#                 )
#         except Exception as e:
#             print(f"[Save Error] {e}")

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

        SMARTWATCH_KEYWORDS = [

            "手錶",
            "腕錶",
            "跑錶",
            "運動錶",
            "watch",

            # Garmin
            "forerunner",
            "fenix",
            "epix",
            "instinct",
            "venu",
            "vivoactive",

            # Apple
            "apple watch",

            # Samsung
            "galaxy watch",

            # Amazfit
            "amazfit",
            "gtr",
            "gts",

            # COROS
            "coros",
            "pace",
            "apex",
            "vertix",

            # Polar
            "polar",
            "vantage",
            "ignite",

            # Suunto
            "suunto",
            "race",
            "vertical",
        ]

        return any(
            keyword in title
            for keyword in SMARTWATCH_KEYWORDS
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

        print(f"[Checking] {product.get('title')}")

        if not match_device_type(
            product,
            need
        ):
            print(f"[Device Filter] {product.get('title')}")
            continue

        if not match_os(
            product,
            need
        ):
            print(f"[OS Filter] {product.get('title')}")
            continue

        if not match_negative(
            product,
            need
        ):
            print(f"[Negative Filter] {product.get('title')}")
            continue

        price = _price(product)

        if price > 0:

            if budget_min and price < budget_min:
                print(f"[Budget Min] {product.get('title')} ({price})")
                continue

            if budget_max and price > budget_max:
                print(f"[Budget Max] {product.get('title')} ({price})")
                continue

        print(f"[PASS] {product.get('title')}")
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


def format_products(products, limit=3):
    return [
        format_product(product)
        for product in products[:limit]
    ]

def recommend_from_need(
    need,
    limit=3
):
    print("need.brand =", need.preferences.brand)

    search_query = build_search_query(need)

    candidates = retrieve_candidates(search_query)

    print(f"[Candidates] {len(candidates)}")

    filtered, budget_fallback = hard_filter_candidates(
        candidates,
        need
    )

    print(f"[After Filter] {len(filtered)}")

    ranked = rank_products(
        filtered,
        need
    )
    print("\n========== Ranked ==========")

    for idx, product in enumerate(ranked[:5], start=1):

        print(
            f"{idx}. "
            f"{product.get('title','')} | "
            f"Score={product.get('match',0)} | "
            f"Reason={product.get('reason','')}"
        )

    print("============================")
    
    print(f"[After Ranking] {len(ranked)}")

    formatted_products = format_products(
        ranked,
        limit
    )

    print(f"[Formatted] {len(formatted_products)}")

    return {
        "products": formatted_products,
        "search_query": search_query,
        "user_need": need.to_dict(),
        "budget_fallback": budget_fallback
    }
