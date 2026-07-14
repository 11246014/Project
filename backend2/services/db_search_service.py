from services.backend1_client import get_db_products


async def search_db_products(keyword):

    try:

        products = await get_db_products()

        print("\n===== DB Products =====")

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

        keywords = keyword.lower().split()

        matched = []

        for product in products:

            text = f"""
            {product.get("name", "")}
            {product.get("description", "")}
            """.lower()

            score = 0

            for k in keywords:

                if k not in text:
                    continue

                # =====================
                # 品牌 / 生態系
                # =====================

                if k in [
                    "apple",
                    "watch",
                    "iphone",
                    "garmin",
                    "amazfit",
                    "samsung",
                    "galaxy",
                    "huawei"
                ]:

                    score += 30

                # =====================
                # 功能關鍵字
                # =====================

                elif k in [
                    "gps",
                    "睡眠監測",
                    "心率",
                    "血氧",
                    "ecg",
                    "防水"
                ]:

                    score += 15

                # =====================
                # 一般關鍵字
                # =====================

                else:

                    score += 5

            # =====================
            # 至少命中一個條件
            # =====================

            if score > 0:

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

                    "match": score,

                    "reason": (
                        f"資料庫匹配分數 {score}"
                    ),

                    "isTop": False,

                    "tags": [],

                    "image": product.get(
                        "image",
                        ""
                    ),

                    "link": ""
                })

        # =====================
        # 依 match 排序
        # =====================

        matched.sort(

            key=lambda x: x.get(
                "match",
                0
            ),

            reverse=True
        )

        print(
            f"[DB Match] {len(matched)} 筆"
        )

        return matched

    except Exception as e:

        print(
            f"[DB Search Error] {e}"
        )

        return []