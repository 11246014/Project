from services.web_search_service import (
    web_search_products
)

from services.product_analyzer_service import (
    analyze_product
)

from services.ai_rerank_service import (
    ai_rerank
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
# Feature Keyword Mapping
# =========================

FEATURE_KEYWORDS = {

    "GPS": [

        "gps",
        "定位",
        "導航",
        "衛星"
    ],

    "睡眠": [

        "睡眠",
        "sleep"
    ],

    "血氧": [

        "血氧",
        "spo2"
    ],

    "ECG": [

        "ecg",
        "心電圖"
    ],

    "防水": [

        "防水",
        "ip68",
        "5atm"
    ],

    "心率": [

        "心率",
        "heart rate"
    ]
}


# =========================
# Core Factor Mapping
# =========================

CORE_FACTOR_KEYWORDS = {

    "電池續航": [

        "續航",
        "長續航",
        "電池"
    ],

    "耐用性": [

        "軍規",
        "防摔",
        "耐用"
    ],

    "感測器精準": [

        "雙頻gps",
        "高精度",
        "精準"
    ],

    "價格": [

        "cp值",
        "超值"
    ]
}


# =========================
# Feature Weight Config
# =========================

WEIGHT_CONFIG = {

    "GPS": 30,

    "睡眠": 30,

    "血氧": 35,

    "ECG": 40,

    "防水": 20,

    "心率": 25,

    "電池續航": 50,

    "耐用性": 50,

    "感測器精準": 45,

    "價格": 35
}


# =========================
# 負面關鍵字
# =========================

NEGATIVE_STYLE_KEYWORDS = {

    "商務正式": [

        "兒童",
        "卡通",
        "玩具"
    ],

    "時尚 / 穿搭": [

        "軍規",
        "粗獷"
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

    # 裝置類型

    device_type = filters.get(
        "device_type",
        ""
    )
    if device_type == "手環":

        keywords.append("智慧手環")

    elif device_type == "手錶":

        keywords.append("智慧手錶")

    else:

        keywords.append(device_type)

    # 使用情境

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

    # 風格

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

    # 電池需求

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

    # 功能需求

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

    # OS

    os_type = filters.get(
        "os",
        ""
    )

    if "iOS" in os_type:

        keywords.append("iPhone")

    elif "Android" in os_type:

        keywords.append("Android")

    # 去重

    keywords = list(
        dict.fromkeys(keywords)
    )

    # keyword

    keyword = " ".join(keywords)

    print(
        f"[Search Keyword] {keyword}"
    )

    return keyword


# =========================
# OS 相容性
# =========================

def os_match(product, os_type):

    title = product.get(
        "title",
        ""
    ).lower()

    if "iOS" in os_type:

        for word in ANDROID_ONLY_KEYWORDS:

            if word in title:

                return False

    elif "Android" in os_type:

        for word in IOS_ONLY_KEYWORDS:

            if word in title:

                return False

    return True


# =========================
# 負面商品過濾
# =========================

def negative_match(product, style):

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

    for word in bad_keywords:

        if word.lower() in text:

            return False

    return True


# =========================
# Feature Score
# =========================

def calculate_feature_score(
    product,
    filters
):

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

    matched_features = []

    # Feature Score

    features = filters.get(
        "features",
        []
    )

    for feature in features:

        # GPS

        if "GPS" in feature:

            for keyword in FEATURE_KEYWORDS["GPS"]:

                if keyword in text:

                    score += WEIGHT_CONFIG["GPS"]

                    matched_features.append(
                        "GPS"
                    )

                    break

        # 睡眠

        elif "睡眠" in feature:

            for keyword in FEATURE_KEYWORDS["睡眠"]:

                if keyword in text:

                    score += WEIGHT_CONFIG["睡眠"]

                    matched_features.append(
                        "睡眠"
                    )

                    break

        # 血氧

        elif "血氧" in feature:

            for keyword in FEATURE_KEYWORDS["血氧"]:

                if keyword in text:

                    score += WEIGHT_CONFIG["血氧"]

                    matched_features.append(
                        "血氧"
                    )

                    break

        # ECG

        elif "ECG" in feature:

            for keyword in FEATURE_KEYWORDS["ECG"]:

                if keyword in text:

                    score += WEIGHT_CONFIG["ECG"]

                    matched_features.append(
                        "ECG"
                    )

                    break

    # Core Factors

    core_factors = filters.get(
        "core_factors",
        []
    )

    for factor in core_factors:

        keywords = CORE_FACTOR_KEYWORDS.get(
            factor,
            []
        )

        for keyword in keywords:

            if keyword.lower() in text:

                score += WEIGHT_CONFIG.get(
                    factor,
                    20
                )

                matched_features.append(
                    factor
                )

                break

    # Apple 生態

    os_type = filters.get(
        "os",
        ""
    )

    if "iOS" in os_type:

        if (
            "apple watch" in text
            or "iphone" in text
        ):

            score += 40

            matched_features.append(
                "Apple生態"
            )

    # Android 生態

    elif "Android" in os_type:

        if (
            "galaxy watch" in text
            or "wear os" in text
        ):

            score += 35

            matched_features.append(
                "Android生態"
            )

    # AMOLED

    style = filters.get(
        "style",
        ""
    )

    if "時尚" in style:

        if "amoled" in text:

            score += 25

            matched_features.append(
                "AMOLED"
            )

    # 長續航

    battery = filters.get(
        "battery",
        ""
    )

    if "5" in battery or "7" in battery:

        if (
            "長續航" in text
            or "14天" in text
            or "21天" in text
        ):

            score += 45

            matched_features.append(
                "長續航"
            )

    # 商品評價

    rating = product.get(
        "rating",
        0
    )

    try:

        rating = float(rating)

    except:

        rating = 0

    score += int(rating * 5)

    # 儲存資訊

    product[
        "feature_score"
    ] = score

    product[
        "matched_features"
    ] = matched_features

    return score


# =========================
# 商品篩選主流程
# =========================

def filter_products(filters):

    try:

        # 搜尋關鍵字

        keyword = build_search_keyword(
            filters
        )

        # Web Search

        products = web_search_products(
            keyword
        )

        # 價格區間

        min_price = filters.get(
            "min_price",
            0
        )

        max_price = filters.get(
            "max_price",
            999999
        )

        # OS

        os_type = filters.get(
            "os",
            ""
        )

        # Style

        style = filters.get(
            "style",
            ""
        )

        # 二次篩選

        filtered_products = []

        original_products = products.copy()

        budget_fallback = False

        for product in products:

            price = product.get(
                "price",
                0
            )

            # 價格

            if not (
                min_price <= price <= max_price
            ):

                continue

            # OS

            if not os_match(
                product,
                os_type
            ):

                continue

            # 負面過濾

            if not negative_match(
                product,
                style
            ):

                continue

            # Feature Score

            score = calculate_feature_score(

                product,

                filters
            )

            product[
                "feature_score"
            ] = score

            filtered_products.append(
                product
            )

        # =========================
        # Budget Fallback
        # =========================

        if len(filtered_products) == 0:

            budget_fallback = True

            print(
                "[Budget Fallback]"
            )

            # =========================
            # 先過 OS / Style
            # =========================

            fallback_products = []

            for product in original_products:

                if not os_match(
                    product,
                    os_type
                ):
                    continue

                if not negative_match(
                    product,
                    style
                ):
                    continue

                fallback_products.append(
                    product
                )

            original_products = (
                fallback_products
            )

            # =========================
            # 先排除太離譜便宜的商品
            # =========================

            near_budget = [

                p for p in original_products

                if p.get(
                    "price",
                    0
                ) >= min_price * 0.7
            ]

            if near_budget:

                original_products = near_budget

            print(
                f"[Near Budget] {len(original_products)}"
            )

            # =========================
            # 找最接近預算
            # =========================

            original_products.sort(
                key=lambda p: (

                    p.get("price", 0) < min_price,

                    min(
                        abs(
                            p.get("price", 0)
                            - min_price
                        ),
                        abs(
                            p.get("price", 0)
                            - max_price
                        )
                    )
                )
            )

            filtered_products = (
                original_products[:3]
            )

            # =========================
            # 補算 feature score
            # =========================

            for product in filtered_products:

                score = calculate_feature_score(
                    product,
                    filters
                )

                product["feature_score"] = score

        # =========================
        # AI Rerank
        # =========================

        for product in filtered_products:

            try:

                ai_result = ai_rerank(

                    filters,

                    product
                )

                product[
                    "ai_score"
                ] = ai_result.get(
                    "score",
                    50
                )

                product[
                    "ai_reason"
                ] = ai_result.get(
                    "reason",
                    ""
                )

            except Exception as e:

                print(
                    f"[AI Rerank Error] {e}"
                )

                product[
                    "ai_score"
                ] = 50

        # =========================
        # 排序
        # =========================

        filtered_products.sort(

            key=lambda x: (

                x.get(
                    "ai_score",
                    0
                ),

                x.get(
                    "feature_score",
                    0
                ),

                x.get(
                    "rating",
                    0
                )

            ),

            reverse=True
        )

        print(
            f"[Second Filter] "
            f"{len(filtered_products)}"
        )

        # 印出分數

        for product in filtered_products:

            print(

                product["title"],

                "| ai =",

                product.get(
                    "ai_score",
                    0
                ),

                "| feature =",

                product.get(
                    "feature_score",
                    0
                ),

                "| matched =",

                product.get(
                    "matched_features",
                    []
                )
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