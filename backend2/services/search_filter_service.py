#search_filter_service.py
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
# Usage Filter
# ==================================================

USAGE_KEYWORDS = {
    "running": [
        "跑步",
        "跑錶",
        "forerunner",
        "runner",
    ],

    "運動": [
        "運動",
        "跑步",
        "跑錶",
        "forerunner",
        "runner",
    ],

    "跑步": [
        "跑步",
        "跑錶",
        "forerunner",
        "runner",
    ],
}


def match_usage(product, need):
    """
    檢查商品是否符合使用者指定的用途。

    目前只在 Budget Fallback 使用，
    避免預算不足時推薦完全不符合用途的商品。
    """

    usages = getattr(
        need,
        "usage",
        []
    ) or []

    # 使用者沒有指定用途
    if not usages:
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

    for usage in usages:

        keywords = USAGE_KEYWORDS.get(
            usage,
            [str(usage)]
        )

        if any(
            keyword.lower() in text
            for keyword in keywords
        ):
            return True

    return False


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

    Feature 不在這裡做 Hard Filter。
    Feature 由 Ranking 的 Feature Evidence
    統一處理。

    如果所有商品都因預算被排除，
    則啟用 Budget Fallback。
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
        # Usage
        # ==================================================

        # Usage 不在 Hard Filter 淘汰
        # 交給 Ranking 判斷符合程度

        # ==================================================
        # Budget
        # ==================================================

        currency = str(
            product.get(
                "currency",
                ""
            )
        ).upper()

        if (
            (budget_min or budget_max)
            and currency
            and currency != "TWD"
        ):

            if DEBUG_SEARCH_FILTER:

                print(
                    f"[Budget Currency Filter] "
                    f"{product.get('title')} "
                    f"(currency={currency})"
                )

            continue

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

        # --------------------------------------------------
        # 如果使用者有指定用途
        # 優先保留符合用途的商品
        # --------------------------------------------------

        if getattr(need, "usage", None):

            usage_filtered = [
                product
                for product in filtered
                if match_usage(product, need)
            ]

            # 有符合用途 + 預算內商品
            if usage_filtered:

                return (
                    usage_filtered,
                    budget_fallback
                )

            # 沒有符合用途的預算內商品
            # 不直接 return
            # 讓後面的 Budget Fallback 尋找
            # 「符合用途但超出預算」的商品

        else:

            return (
                filtered,
                budget_fallback
            )

    # ==================================================
    # No Budget Condition
    # ==================================================

    if not budget_max:

        return (
            filtered,
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

        and match_usage(
            product,
            need
        )

        and (
            not product.get("currency")
            or str(
                product.get("currency")
            ).upper() == "TWD"
        )
    ]

    # ==================================================
    # Fallback Sorting
    # ==================================================

    fallback = sorted(
        fallback_candidates,

        key=lambda p: (
            _price(p) > budget_max,
            abs(
                _price(p) - budget_max
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