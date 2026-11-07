import re
from urllib.parse import urlparse

from services.backend1_client import get_db_products
from services.product_filter_service import detect_brand

# ==================================================
# DB 商品的「來源平台」
# ==================================================
#
# 注意：
# products 資料表的 platform 欄位，存的是商品當初從網路搜尋存入時的
# 真實來源平台（例如 momo購物網、蝦皮購物、Garmin 官網）。
# 以前這裡把 platform 寫死成 "MySQL"，導致：
#   1. 前端 / 購物車 / 歷史紀錄顯示的來源平台是資料庫名稱，不是電商
#   2. 後台儀表板「來源平台曝光次數」出現 MySQL
# 現在改成直接使用商品自己的 platform；欄位空白或舊資料殘留 "MySQL"
# 時，改由商品連結的網域推回平台名稱，再不行才用 shop，最後才留空字串。

# 內部資料來源標記，不是真實外部平台（比對時不分大小寫、忽略空白 _ -）
INTERNAL_PLATFORM_KEYS = {
    "mysql",
    "sql",
    "database",
    "db",
    "local",
    "internal",
    "資料庫",
}

# 網域關鍵字 → 平台顯示名稱（名稱需與網路搜尋流程產生的平台名稱一致，
# 儀表板才會把同一個平台算在同一條）
DOMAIN_PLATFORM_MAP = [
    ("momoshop.com.tw", "momo購物網"),
    ("momo.com.tw", "momo購物網"),
    ("shopee.tw", "蝦皮購物"),
    ("shopee.", "蝦皮購物"),
    ("coupang.com", "Coupang 酷澎"),
    ("pchome.com.tw", "PChome 24h購物"),
    ("books.com.tw", "博客來"),
    ("rakuten.com.tw", "樂天市場購物網"),
    ("fetnet.net", "friDay購物"),
    ("friday.tw", "friDay購物"),
    ("garmin.com", "Garmin"),
    ("amazfit.com", "Amazfit智慧穿戴品牌官方網站"),
    ("store.google.com", "Google Store"),
    ("apple.com", "Apple 官方網站"),
    ("samsung.com", "Samsung 官方網站"),
    ("decathlon.tw", "台灣迪卡儂"),
    ("ebay.com", "eBay"),
    ("etmall.com.tw", "東森網路購物"),
    ("landtop.com.tw", "地標網通 - 挑戰手機最低價"),
    ("bikeinn.com", "Bikeinn.com"),
    ("humehealth.com", "Hume Health"),
]


def is_internal_platform(name) -> bool:
    """判斷是否為內部資料來源標記（例如 MySQL），不是真實外部平台"""

    key = re.sub(r"[\s_\-]+", "", str(name or "").lower())

    return (not key) or key in INTERNAL_PLATFORM_KEYS or "mysql" in key


def platform_from_link(link: str) -> str:
    """從商品連結的網域推回平台名稱；對不到已知平台就回傳網域本身"""

    if not link:
        return ""

    host = (urlparse(link).netloc or "").lower()

    if not host:
        return ""

    for keyword, platform_name in DOMAIN_PLATFORM_MAP:
        if keyword in host:
            return platform_name

    # 未知網站：保留網域（去掉 www.），至少是真實的外部來源
    return host[4:] if host.startswith("www.") else host


def resolve_db_platform(product: dict) -> str:
    """決定 DB 商品要顯示 / 統計的來源平台（優先順序：商品 platform → 連結網域 → shop → 空字串）"""

    stored = str(product.get("platform") or "").strip()

    if not is_internal_platform(stored):
        return stored

    from_link = platform_from_link(str(product.get("link") or ""))

    if from_link:
        return from_link

    shop = str(product.get("shop") or "").strip()

    if not is_internal_platform(shop):
        return shop

    return ""


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
        text = text.replace(separator, " ")

    # 多個空白壓成一個
    text = " ".join(text.split())

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

    normalized = normalize_keyword_text(keyword_text)

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


def calculate_keyword_score(keyword, text):
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

    keyword = str(keyword).strip().lower()

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

            print("\n===== DB Products =====")

            for product in products:

                print(product.get("name", ""))

            print(f"\n[DB Keyword] {keyword}")

        # ==================================================
        # Keyword Normalize
        # ==================================================

        if not keyword:

            if DEBUG_SEARCH:

                print("[DB Search] Empty Keyword")

            return []

        keyword_text = normalize_keyword_text(keyword)

        if not keyword_text:

            if DEBUG_SEARCH:

                print("[DB Search] Empty Keyword")

            return []

        # ==================================================
        # Build Search Keywords
        # ==================================================

        keywords = build_search_keywords(keyword_text)

        if DEBUG_SEARCH:

            print("[DB Keywords]", keywords)

        if not keywords:

            if DEBUG_SEARCH:

                print("[DB Search] No Keywords")

            return []

        # ==================================================
        # Candidate Matching
        # ==================================================

        matched = []

        for product in products:

            # =========================
            # 商品名稱
            # =========================

            name = product.get("name", "")

            # =========================
            # 商品描述
            # =========================

            description = product.get("description", "")

            # =========================
            # 統一搜尋文字
            # =========================

            text = (f"{name} " f"{description}").lower()

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

                result = calculate_keyword_score(k, text)

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
                    already_category = "category" in matched_types

                    if already_category:
                        continue

                # --------------------------------------------------
                # 加分
                # --------------------------------------------------

                score += result["score"]

                matched_keywords.append(k)

                if keyword_type not in matched_types:

                    matched_types.append(keyword_type)

            # ==================================================
            # Minimum Match Threshold
            # ==================================================

            if score < MIN_DB_MATCH_SCORE:

                # Debug：
                # 只在有命中但分數不足時顯示，
                # 方便確認為什麼被排除。

                if DEBUG_SEARCH and matched_keywords:

                    print(
                        "[DB Candidate Rejected]",
                        name,
                        "| Score:",
                        score,
                        "| Keywords:",
                        matched_keywords,
                    )

                continue

            # ==================================================
            # WearWise Product Format
            # ==================================================

            matched.append(
                {
                    "id": product.get("id"),
                    "title": product.get("name", ""),
                    "price": product.get("price", 0),
                    "desc": product.get("description", ""),
                    "platform": resolve_db_platform(product),  # 真實來源平台，不再寫死 MySQL
                    "rating": product.get("rating", 5),
                    # 注意：
                    # 這裡的 match 是 DB Keyword Match Score，
                    # 不是最終推薦百分比。
                    "match": score,
                    "reason": (f"DB 關鍵字匹配分數 {score}"),
                    "isTop": False,
                    "tags": [],
                    "image": product.get("image", ""),
                    # =========================
                    # Product Source
                    # =========================
                    "source": "db",
                    # =========================
                    # Shop
                    # =========================
                    "shop": product.get("shop", ""),
                    # =========================
                    # Link
                    # =========================
                    "link": product.get("link", ""),
                    # =========================
                    # Debug / Matching Info
                    # =========================
                    "matched_keywords": matched_keywords,
                    "matched_types": matched_types,
                    "brand": detect_brand(
                        product.get("name", "")
                    ),  # DB 來源商品標出品牌
                }
            )

        # ==================================================
        # Sort
        # ==================================================

        matched.sort(key=lambda x: x.get("match", 0), reverse=True)

        # ==================================================
        # Debug
        # ==================================================

        if DEBUG_SEARCH:

            print(f"[DB Match] " f"{len(matched)} 筆")

            for product in matched:

                print(
                    "[DB Candidate]",
                    product.get("title", ""),
                    "| Score:",
                    product.get("match", 0),
                    "| Keywords:",
                    product.get("matched_keywords", []),
                    "| Types:",
                    product.get("matched_types", []),
                )

        return matched

    # ==================================================
    # Error Handling
    # ==================================================

    except Exception as e:

        print(f"[DB Search Error] {e}")

        return []
