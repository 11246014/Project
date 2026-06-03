from services.web_search_service import (
    web_search_products
)

from services.product_analyzer_service import (
    analyze_product
)


# =========================
# 使用情境 Mapping
# =========================

USAGE_MAPPING = {

    "日常生活（看時間 / 通知）": [

        "通知",
        "生活",
        "輕薄",
        "續航"
    ],

    "運動健身": [

        "GPS",
        "運動",
        "心率",
        "防水"
    ],

    "健康管理": [

        "血氧",
        "睡眠",
        "ECG",
        "健康"
    ],

    "登山 / 戶外": [

        "GPS",
        "戶外",
        "軍規",
        "長續航"
    ]
}


# =========================
# 風格 Mapping
# =========================

STYLE_MAPPING = {

    "商務正式": [

        "商務",
        "金屬",
        "正式"
    ],

    "時尚 / 穿搭": [

        "時尚",
        "設計",
        "AMOLED"
    ],

    "運動風": [

        "運動",
        "防水",
        "GPS"
    ]
}


# =========================
# 電池 Mapping
# =========================

BATTERY_MAPPING = {

    "每天充電": [

        "高性能"
    ],

    "2 – 3 天一次": [

        "續航"
    ],

    "5 – 7 天一次": [

        "長續航"
    ]
}


# =========================
# iOS / Android 相容性
# =========================

IOS_ONLY_KEYWORDS = [

    "apple watch"
]

ANDROID_ONLY_KEYWORDS = [

    "galaxy watch",

    "wear os"
]


# =========================
# 建立搜尋關鍵字
# =========================

def build_search_keyword(filters):

    keywords = []

    # =========================
    # 裝置類型
    # =========================

    device_type = filters.get(
        "device_type",
        ""
    )

    if device_type:

        keywords.append(device_type)

    # =========================
    # 使用情境
    # =========================

    usage = filters.get(
        "usage",
        ""
    )

    usage_keywords = USAGE_MAPPING.get(
        usage,
        []
    )

    keywords.extend(
        usage_keywords
    )

    # =========================
    # 風格
    # =========================

    style = filters.get(
        "style",
        ""
    )

    style_keywords = STYLE_MAPPING.get(
        style,
        []
    )

    keywords.extend(
        style_keywords
    )

    # =========================
    # 電池需求
    # =========================

    battery = filters.get(
        "battery",
        ""
    )

    battery_keywords = BATTERY_MAPPING.get(
        battery,
        []
    )

    keywords.extend(
        battery_keywords
    )

    # =========================
    # 功能需求
    # =========================

    features = filters.get(
        "features",
        []
    )

    for feature in features:

        if "血氧" in feature:

            keywords.append("血氧")

        elif "GPS" in feature:

            keywords.append("GPS")

        elif "睡眠" in feature:

            keywords.append("睡眠監測")

        elif "ECG" in feature:

            keywords.append("ECG")

    # =========================
    # OS
    # =========================

    os_type = filters.get(
        "os",
        ""
    )

    if "iOS" in os_type:

        keywords.append("iPhone")

    elif "Android" in os_type:

        keywords.append("Android")

    # =========================
    # 去重
    # =========================

    keywords = list(
        dict.fromkeys(keywords)
    )

    # =========================
    # 最後 keyword
    # =========================

    keyword = " ".join(keywords)

    print(
        f"[Search Keyword] {keyword}"
    )

    return keyword


# =========================
# OS 相容性二次篩選
# =========================

def os_match(product, os_type):

    title = product.get(
        "title",
        ""
    ).lower()

    # =========================
    # iOS
    # =========================

    if "iOS" in os_type:

        for word in ANDROID_ONLY_KEYWORDS:

            if word in title:

                return False

    # =========================
    # Android
    # =========================

    elif "Android" in os_type:

        for word in IOS_ONLY_KEYWORDS:

            if word in title:

                return False

    return True


# =========================
# Feature Match
# =========================

def feature_match(product, features):

    title = product.get(
        "title",
        ""
    ).lower()

    desc = product.get(
        "desc",
        ""
    ).lower()

    text = f"{title} {desc}"

    score = 0

    # =========================
    # GPS
    # =========================

    for feature in features:

        if "GPS" in feature:

            if "gps" in text:

                score += 30

        # =========================
        # 睡眠
        # =========================

        elif "睡眠" in feature:

            if "睡眠" in text:

                score += 30

        # =========================
        # 血氧
        # =========================

        elif "血氧" in feature:

            if "血氧" in text:

                score += 30

        # =========================
        # ECG
        # =========================

        elif "ECG" in feature:

            if (
                "ecg" in text
                or "心電圖" in text
            ):

                score += 30

    product["feature_score"] = score

    return score > 0 or len(features) == 0


# =========================
# 商品篩選主流程
# =========================

def filter_products(filters):

    try:

        # =========================
        # 搜尋關鍵字
        # =========================

        keyword = build_search_keyword(
            filters
        )

        # =========================
        # Web Search
        # =========================

        products = web_search_products(
            keyword
        )

        # =========================
        # 價格區間
        # =========================

        min_price = filters.get(
            "min_price",
            0
        )

        max_price = filters.get(
            "max_price",
            999999
        )

        # =========================
        # 功能需求
        # =========================

        features = filters.get(
            "features",
            []
        )

        # =========================
        # OS
        # =========================

        os_type = filters.get(
            "os",
            ""
        )

        # =========================
        # 二次篩選
        # =========================

        filtered_products = []

        for product in products:

            price = product.get(
                "price",
                0
            )

            # =========================
            # 價格區間
            # =========================

            if not (
                min_price <= price <= max_price
            ):

                continue

            # =========================
            # OS 相容性
            # =========================

            if not os_match(
                product,
                os_type
            ):

                continue

            # =========================
            # 功能需求
            # =========================

            if not feature_match(
                product,
                features
            ):

                continue

            filtered_products.append(
                product
            )

        # =========================
        # Feature Score 排序
        # =========================

        filtered_products.sort(

            key=lambda x: x.get(
                "feature_score",
                0
            ),

            reverse=True
        )

        print(
            f"[Second Filter] "
            f"{len(filtered_products)}"
        )

        # =========================
        # AI 分析
        # =========================

        analyzed_products = []

        for product in filtered_products[:3]:

            analyzed = analyze_product(
                product
            )

            analyzed_products.append(
                analyzed
            )

        print(
            f"[Filter] 最終商品數量 "
            f"{len(analyzed_products)}"
        )

        return analyzed_products

    except Exception as e:

        print(
            f"[Filter Service Error] {e}"
        )

        return []