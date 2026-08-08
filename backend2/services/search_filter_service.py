from services.ranking.helper import (
    _price,
)


# ==================================================
# Search Filter Config
# ==================================================

DEBUG_SEARCH_FILTER = True


# ==================================================
# Negative Style Keywords
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


# ==================================================
# OS Compatibility Keywords
# ==================================================

IOS_ONLY_KEYWORDS = [
    "apple watch",
]

ANDROID_ONLY_KEYWORDS = [
    "galaxy watch",
    "wear os",
]


# ==================================================
# Device Type Filter
# ==================================================

def match_device_type(product, need):
    """
    檢查商品是否符合使用者指定的裝置類型。

    如果使用者沒有指定裝置類型，
    則直接視為符合。
    """

    if not need.device_type:
        return True

    title = product.get(
        "title",
        ""
    ).lower()

    # ==================================================
    # Smart Ring
    # ==================================================

    if need.device_type == "smart_ring":

        return (
            "戒指" in title
            or "指環" in title
            or "ring" in title
        )

    # ==================================================
    # Smart Band
    # ==================================================

    elif need.device_type == "smart_band":

        return (
            "手環" in title
            or "band" in title
            or "fit" in title
        )

    # ==================================================
    # Smartwatch
    # ==================================================

    elif need.device_type == "smartwatch":

        smartwatch_keywords = [

            # General
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

    # ==================================================
    # Unknown Device Type
    # ==================================================

    return True


# ==================================================
# OS Filter
# ==================================================

def match_os(product, need):
    """
    檢查商品是否符合使用者指定的作業系統。

    目前採用「排除明顯不相容商品」的策略，
    而不是完整的 OS 相容性判斷。
    """

    os_type = need.preferences.os

    # 沒有指定 OS
    if not os_type:
        return True

    title = product.get(
        "title",
        ""
    ).lower()

    # ==================================================
    # iOS
    # ==================================================

    if os_type == "iOS":

        for keyword in ANDROID_ONLY_KEYWORDS:

            if keyword.lower() in title:

                return False

    # ==================================================
    # Android
    # ==================================================

    elif os_type == "Android":

        for keyword in IOS_ONLY_KEYWORDS:

            if keyword.lower() in title:

                return False

    return True


# ==================================================
# Negative Style Filter
# ==================================================

def match_negative(product, need):
    """
    排除不符合使用者風格需求的商品。

    目前只處理系統已定義的
    NEGATIVE_STYLE_KEYWORDS。
    """

    style = need.preferences.style

    # 沒有指定風格
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

    text = (
        f"{title} "
        f"{desc}"
    )

    bad_keywords = (
        NEGATIVE_STYLE_KEYWORDS.get(
            style,
            []
        )
    )

    for keyword in bad_keywords:

        if keyword.lower() in text:

            return False

    return True


# ==================================================
# Hard Filter
# ==================================================

def hard_filter_candidates(
    candidates,
    need,
):
    """
    對候選商品進行硬性條件篩選。

    Filter 順序：

    1. Device Type
    2. OS
    3. Negative Style
    4. Budget

    如果所有商品都因預算被排除，
    則啟用 Budget Fallback。

    Budget Fallback 會保留：

    1. Device Type
    2. OS
    3. Negative Style

    然後選擇價格最接近需求的商品。
    """

    filtered = []

    budget_fallback = False

    # ==================================================
    # Budget
    # ==================================================

    budget_min = (
        need.budget.min
        or 0
    )

    budget_max = (
        need.budget.max
        or 0
    )

    # ==================================================
    # Normal Filtering
    # ==================================================

    for product in candidates:

        if DEBUG_SEARCH_FILTER:

            print(
                f"[Checking] "
                f"{product.get('title')}"
            )

        # ==================================================
        # Device Type
        # ==================================================

        if not match_device_type(
            product,
            need
        ):

            if DEBUG_SEARCH_FILTER:

                print(
                    f"[Device Filter] "
                    f"{product.get('title')}"
                )

            continue

        # ==================================================
        # OS
        # ==================================================

        if not match_os(
            product,
            need
        ):

            if DEBUG_SEARCH_FILTER:

                print(
                    f"[OS Filter] "
                    f"{product.get('title')}"
                )

            continue

        # ==================================================
        # Negative Style
        # ==================================================

        if not match_negative(
            product,
            need
        ):

            if DEBUG_SEARCH_FILTER:

                print(
                    f"[Negative Filter] "
                    f"{product.get('title')}"
                )

            continue

        # ==================================================
        # Budget
        # ==================================================

        price = _price(
            product
        )

        if price > 0:

            # -------------------------
            # Minimum Budget
            # -------------------------

            if (
                budget_min
                and price < budget_min
            ):

                if DEBUG_SEARCH_FILTER:

                    print(
                        f"[Budget Min] "
                        f"{product.get('title')} "
                        f"({price})"
                    )

                continue

            # -------------------------
            # Maximum Budget
            # -------------------------

            if (
                budget_max
                and price > budget_max
            ):

                if DEBUG_SEARCH_FILTER:

                    print(
                        f"[Budget Max] "
                        f"{product.get('title')} "
                        f"({price})"
                    )

                continue

        # ==================================================
        # PASS
        # ==================================================

        if DEBUG_SEARCH_FILTER:

            print(
                f"[PASS] "
                f"{product.get('title')}"
            )

        filtered.append(
            product
        )

    # ==================================================
    # Normal Result
    # ==================================================

    if filtered:

        return (
            filtered,
            budget_fallback
        )

    # ==================================================
    # No Budget Condition
    # ==================================================

    if not budget_max:

        return (
            candidates,
            budget_fallback
        )

    # ==================================================
    # Budget Fallback
    # ==================================================

    budget_fallback = True

    fallback_candidates = [

        product

        for product in candidates

        if match_device_type(
            product,
            need
        )

        and match_os(
            product,
            need
        )

        and match_negative(
            product,
            need
        )
    ]

    # ==================================================
    # Fallback Sorting
    # ==================================================

    fallback = sorted(

        fallback_candidates,

        key=lambda p: (

            _price(p) < budget_min,

            abs(
                _price(p) - budget_min
            )

        )
    )

    # ==================================================
    # Fallback Result
    # ==================================================

    return (
        fallback[:3],
        budget_fallback
    )