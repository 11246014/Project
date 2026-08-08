#db_search_service.py
from services.backend1_client import get_db_products


# ==================================================
# Search Config
# ==================================================

DEBUG_SEARCH = True

# DB 商品最低匹配分數
# 5  = 一般關鍵字
# 15 = 功能關鍵字
# 30 = 品牌 / 生態系關鍵字
MIN_DB_MATCH_SCORE = 15


# ==================================================
# Keyword Config
# ==================================================

BRAND_KEYWORDS = [
    "apple",
    "watch",
    "iphone",
    "garmin",
    "amazfit",
    "samsung",
    "galaxy",
    "huawei",
]

FEATURE_KEYWORDS = [
    "gps",
    "睡眠監測",
    "心率",
    "血氧",
    "ecg",
    "防水",
]


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

        keyword_text = str(
            keyword
        ).strip().lower()

        if not keyword_text:

            if DEBUG_SEARCH:
                print(
                    "[DB Search] Empty Keyword"
                )

            return []

        keywords = keyword_text.split()

        # ==================================================
        # Candidate Matching
        # ==================================================

        matched = []

        for product in products:

            # =========================
            # 商品文字
            # =========================

            name = product.get(
                "name",
                ""
            )

            description = product.get(
                "description",
                ""
            )

            text = (
                f"{name} "
                f"{description}"
            ).lower()

            score = 0
            matched_keywords = []

            # =========================
            # Keyword Matching
            # =========================

            for k in keywords:

                if not k:
                    continue

                if k not in text:
                    continue

                matched_keywords.append(
                    k
                )

                # =====================
                # 品牌 / 生態系
                # =====================

                if k in BRAND_KEYWORDS:

                    score += 30

                # =====================
                # 功能關鍵字
                # =====================

                elif k in FEATURE_KEYWORDS:

                    score += 15

                # =====================
                # 一般關鍵字
                # =====================

                else:

                    score += 5

            # ==================================================
            # Minimum Match Threshold
            # ==================================================

            if score < MIN_DB_MATCH_SCORE:

                continue

            # ==================================================
            # WearWise Product Format
            # ==================================================

            matched.append({

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