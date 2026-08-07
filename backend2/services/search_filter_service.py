#search_filter_service.py
from services.ranking.helper import (
    _price,
)

DEBUG_SEARCH_FILTER = True

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
def match_device_type(product, need):
    """
    檢查商品是否符合使用者指定的裝置類型
    """

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

        smartwatch_keywords = [

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
            for keyword in smartwatch_keywords
        )

    return True

def match_os(product, need):
    """
    檢查商品是否符合使用者指定的作業系統
    """

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
    """
    排除不符合使用者風格需求的商品
    """

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

        if DEBUG_SEARCH_FILTER:
            print(
                f"[Checking] {product.get('title')}"
            )

        if not match_device_type(
            product,
            need
        ):
            if DEBUG_SEARCH_FILTER:
                print(
                    f"[Device Filter] {product.get('title')}"
                )
            continue

        if not match_os(
            product,
            need
        ):
            if DEBUG_SEARCH_FILTER:
                print(
                    f"[OS Filter] {product.get('title')}"
                )
            continue

        if not match_negative(
            product,
            need
        ):
            if DEBUG_SEARCH_FILTER:
                print(
                    f"[Negative Filter] {product.get('title')}"
                )
            continue

        price = _price(product)

        if price > 0:

            if budget_min and price < budget_min:

                if DEBUG_SEARCH_FILTER:
                    print(
                        f"[Budget Min] {product.get('title')} ({price})"
                    )

                continue

            if budget_max and price > budget_max:

                if DEBUG_SEARCH_FILTER:
                    print(
                        f"[Budget Max] {product.get('title')} ({price})"
                    )

                continue

        if DEBUG_SEARCH_FILTER:
            print(
                f"[PASS] {product.get('title')}"
            )

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

