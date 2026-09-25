from services.backend1_client import get_db_products
from services.product_filter_service import detect_brand


# ==================================================
# Search Config
# ==================================================

DEBUG_SEARCH = True

# DB 商品最低匹配分數
#
# 5  = 一般關鍵字
# 15 = 商品類型 / 功能關鍵字
# 30 = 品牌 / 生態系關鍵字
#
# 保持 15，不直接降低門檻。
MIN_DB_MATCH_SCORE = 15


# ==================================================
# Keyword Config
# ==================================================

# --------------------------------------------------
# 商品類型 / 類別關鍵字
# --------------------------------------------------
#
# 這一類不是品牌，也不是功能，
# 而是用來判斷「使用者正在找什麼商品」。
#
# 例如：
# smartwatch
# 智慧手錶
# 手錶
#
# 如果使用者搜尋 smartwatch，
# 商品名稱為：
#
# Smartwatch fitness band
#
# 就應該被視為有效候選。
#
CATEGORY_KEYWORDS = [
    "smartwatch",
    "smart watch",
    "智慧手錶",
    "智慧手表",
    "手錶",
    "手表",
    "smart_band",
    "smart band",
    "智慧手環",
    "智慧手环",
    "手環",
    "手环",
    "運動手環",
    "運動手环",
    "fitness band",
    "fitness watch",
    "fitness tracker",
    "運動手錶",
    "運動手表",
]

# --------------------------------------------------
# 品牌 / 生態系關鍵字
# --------------------------------------------------

BRAND_KEYWORDS = [
    "apple",
    "iphone",
    "garmin",
    "amazfit",
    "samsung",
    "galaxy",
    "huawei",
    "xiaomi",
    "redmi",
    "fitbit",
    "polar",
    "suunto",
    "coros",
]


# --------------------------------------------------
# 功能關鍵字
# --------------------------------------------------

FEATURE_KEYWORDS = [
    "gps",
    "睡眠監測",
    "睡眠追蹤",
    "心率",
    "心率監測",
    "血氧",
    "血氧監測",
    "ecg",
    "防水",
    "血壓",
    "步數",
    "運動追蹤",
    "活動追蹤",
    "通知",
    "行事曆",
    "通話",
    "音樂",
    "nfc",
    "支付",
]


# ==================================================
# Keyword Normalize
# ==================================================

def normalize_keyword_text(text):
    """
    將搜尋關鍵字做基本正規化。

    目的：
    1. 統一大小寫
    2. 移除多餘空白
    3. 避免 '/'、'|'、',' 等符號影響搜尋
    """

    if text is None:
        return ""

    text = str(text).strip().lower()

    if not text:
        return ""

    # 常見分隔符號轉成空白
    separators = [
        "/",
        "|",
        ",",
        "，",
        "、",
        ";",
        "；",
        "(",
        ")",
        "（",
        "）",
        "[",
        "]",
        "【",
        "】",
    ]

    for separator in separators:
        text = text.replace(
            separator,
            " "
        )

    # 多個空白壓成一個
    text = " ".join(
        text.split()
    )

    return text


# ==================================================
# Build Search Keywords
# ==================================================

def build_search_keywords(keyword_text):
    """
    將使用者搜尋文字轉成搜尋關鍵字。

    例如：

    smartwatch 工作 / 商務（訊息 / 行事曆）

    會轉成：

    [
        "smartwatch",
        "工作",
        "商務",
        "訊息",
        "行事曆"
    ]

    同時會自動加入一些中文商品類型詞，
    避免 DB 商品只有「智慧手錶」而搜尋詞是
    「smartwatch」時完全匹配不到。
    """

    normalized = normalize_keyword_text(
        keyword_text
    )

    if not normalized:
        return []

    # 基本 token
    raw_keywords = normalized.split()

    keywords = []

    for item in raw_keywords:

        item = item.strip()

        if not item:
            continue

        # 避免單獨符號
        if item in {
            "-",
            "_",
            ":",
            "：",
            ".",
        }:
            continue

        if item not in keywords:
            keywords.append(item)

    # --------------------------------------------------
    # 商品類型同義詞
    # --------------------------------------------------

    smart_band_aliases = [
        "smart_band",
        "smart band",
        "智慧手環",
        "智慧手环",
        "手環",
        "手环",
        "運動手環",
        "運動手环",
        "fitness band",
        "fitness tracker",
    ]
    
    category_aliases = {
        "smartwatch": [
            "smartwatch",
            "smart watch",
            "智慧手錶",
            "智慧手表",
            "手錶",
            "手表",
        ],
        "smart watch": [
            "smartwatch",
            "smart watch",
            "智慧手錶",
            "智慧手表",
            "手錶",
            "手表",
        ],
        "智慧手錶": [
            "smartwatch",
            "smart watch",
            "智慧手錶",
            "智慧手表",
            "手錶",
            "手表",
        ],
        "智慧手表": [
            "smartwatch",
            "smart watch",
            "智慧手錶",
            "智慧手表",
            "手錶",
            "手表",
        ],
    }
    for alias in smart_band_aliases:
        category_aliases[alias] = smart_band_aliases

    expanded_keywords = []

    for item in keywords:

        if item in category_aliases:

            for alias in category_aliases[item]:

                if alias not in expanded_keywords:
                    expanded_keywords.append(alias)

        else:

            if item not in expanded_keywords:
                expanded_keywords.append(item)

    return expanded_keywords


# ==================================================
# Keyword Score
# ==================================================

def calculate_keyword_score(
    keyword,
    text
):
    """
    計算單一 keyword 的匹配分數。

    分數：

    品牌 / 生態系 = 30
    商品類型      = 15
    功能          = 15
    一般關鍵字    = 5

    回傳：

    {
        "matched": True / False,
        "score": 15,
        "type": "category"
    }
    """

    if not keyword:
        return {
            "matched": False,
            "score": 0,
            "type": None,
        }

    if not text:
        return {
            "matched": False,
            "score": 0,
            "type": None,
        }

    keyword = str(
        keyword
    ).strip().lower()

    if not keyword:
        return {
            "matched": False,
            "score": 0,
            "type": None,
        }

    # --------------------------------------------------
    # 是否命中
    # --------------------------------------------------

    if keyword not in text:

        return {
            "matched": False,
            "score": 0,
            "type": None,
        }

    # --------------------------------------------------
    # 品牌 / 生態系
    # --------------------------------------------------

    if keyword in BRAND_KEYWORDS:

        return {
            "matched": True,
            "score": 30,
            "type": "brand",
        }

    # --------------------------------------------------
    # 商品類型
    # --------------------------------------------------

    if keyword in CATEGORY_KEYWORDS:

        return {
            "matched": True,
            "score": 15,
            "type": "category",
        }

    # --------------------------------------------------
    # 功能
    # --------------------------------------------------

    if keyword in FEATURE_KEYWORDS:

        return {
            "matched": True,
            "score": 15,
            "type": "feature",
        }

    # --------------------------------------------------
    # 一般關鍵字
    # --------------------------------------------------

    return {
        "matched": True,
        "score": 5,
        "type": "general",
    }


# ==================================================
# DB Search
# ==================================================

async def search_db_products(keyword):
    """
    從 Backend1 / MySQL 搜尋商品。

    本函式負責：

    1. 取得 Backend1 商品
    2. 根據搜尋關鍵字進行初步匹配
    3. 計算 DB Keyword Match Score
    4. 轉換成統一的 WearWise 商品格式
    5. 依匹配分數排序

    注意：

    本函式只負責「候選商品搜尋」，
    不負責最終推薦判斷。
    """

    try:

        # ==================================================
        # 取得 DB 商品
        # ==================================================

        products = await get_db_products()

        if products is None:
            products = []

        if DEBUG_SEARCH:

            print(
                "\n===== DB Products ====="
            )

            for product in products:

                print(
                    product.get(
                        "name",
                        ""
                    )
                )

            print(
                f"\n[DB Keyword] {keyword}"
            )

        # ==================================================
        # Keyword Normalize
        # ==================================================

        if not keyword:

            if DEBUG_SEARCH:

                print(
                    "[DB Search] Empty Keyword"
                )

            return []

        keyword_text = normalize_keyword_text(
            keyword
        )

        if not keyword_text:

            if DEBUG_SEARCH:

                print(
                    "[DB Search] Empty Keyword"
                )

            return []

        # ==================================================
        # Build Search Keywords
        # ==================================================

        keywords = build_search_keywords(
            keyword_text
        )

        if DEBUG_SEARCH:

            print(
                "[DB Keywords]",
                keywords
            )

        if not keywords:

            if DEBUG_SEARCH:

                print(
                    "[DB Search] No Keywords"
                )

            return []

        # ==================================================
        # Candidate Matching
        # ==================================================

        matched = []

        for product in products:

            # =========================
            # 商品名稱
            # =========================

            name = product.get(
                "name",
                ""
            )

            # =========================
            # 商品描述
            # =========================

            description = product.get(
                "description",
                ""
            )

            # =========================
            # 統一搜尋文字
            # =========================

            text = (
                f"{name} "
                f"{description}"
            ).lower()

            # =========================
            # Score
            # =========================

            score = 0

            matched_keywords = []

            matched_types = []

            # ==================================================
            # Keyword Matching
            # ==================================================

            for k in keywords:

                result = calculate_keyword_score(
                    k,
                    text
                )

                if not result["matched"]:
                    continue

                # --------------------------------------------------
                # 避免同義詞重複加分
                #
                # 例如：
                #
                # smartwatch
                # smart watch
                # 智慧手錶
                #
                # 同一商品可能同時命中多個同義詞。
                #
                # 不應該因為同一個商品類型就 +15 三次。
                # --------------------------------------------------

                keyword_type = result["type"]

                if keyword_type == "category":

                    # 同一商品類型只算一次
                    already_category = (
                        "category"
                        in matched_types
                    )

                    if already_category:
                        continue

                # --------------------------------------------------
                # 加分
                # --------------------------------------------------

                score += result["score"]

                matched_keywords.append(
                    k
                )

                if keyword_type not in matched_types:

                    matched_types.append(
                        keyword_type
                    )

            # ==================================================
            # Minimum Match Threshold
            # ==================================================

            if score < MIN_DB_MATCH_SCORE:

                # Debug：
                # 只在有命中但分數不足時顯示，
                # 方便確認為什麼被排除。

                if (
                    DEBUG_SEARCH
                    and matched_keywords
                ):

                    print(
                        "[DB Candidate Rejected]",
                        name,
                        "| Score:",
                        score,
                        "| Keywords:",
                        matched_keywords
                    )

                continue

            # ==================================================
            # WearWise Product Format
            # ==================================================

            matched.append({

                "id": product.get("id"),

                "title": product.get(
                    "name",
                    ""
                ),

                "price": product.get(
                    "price",
                    0
                ),

                "desc": product.get(
                    "description",
                    ""
                ),

                "platform": "MySQL",

                "rating": product.get(
                    "rating",
                    5
                ),

                # 注意：
                # 這裡的 match 是 DB Keyword Match Score，
                # 不是最終推薦百分比。
                "match": score,

                "reason": (
                    f"DB 關鍵字匹配分數 {score}"
                ),

                "isTop": False,

                "tags": [],

                "image": product.get(
                    "image",
                    ""
                ),

                # =========================
                # Product Source
                # =========================

                "source": "db",

                # =========================
                # Shop
                # =========================

                "shop": product.get(
                    "shop",
                    ""
                ),

                # =========================
                # Link
                # =========================

                "link": product.get(
                    "link",
                    ""
                ),

                # =========================
                # Debug / Matching Info
                # =========================

                "matched_keywords": matched_keywords,

                "matched_types": matched_types,
                
                
                "brand": detect_brand(product.get("name", "")),  # DB 來源商品標出品牌

            })

        # ==================================================
        # Sort
        # ==================================================

        matched.sort(

            key=lambda x: x.get(
                "match",
                0
            ),

            reverse=True
        )

        # ==================================================
        # Debug
        # ==================================================

        if DEBUG_SEARCH:

            print(
                f"[DB Match] "
                f"{len(matched)} 筆"
            )

            for product in matched:

                print(
                    "[DB Candidate]",
                    product.get(
                        "title",
                        ""
                    ),
                    "| Score:",
                    product.get(
                        "match",
                        0
                    ),
                    "| Keywords:",
                    product.get(
                        "matched_keywords",
                        []
                    ),
                    "| Types:",
                    product.get(
                        "matched_types",
                        []
                    )
                )

        return matched

    # ==================================================
    # Error Handling
    # ==================================================

    except Exception as e:

        print(
            f"[DB Search Error] {e}"
        )

        return []