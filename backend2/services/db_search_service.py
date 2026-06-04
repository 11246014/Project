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

            match_count = 0

            for k in keywords:

                if k in text:

                    match_count += 1

            # 至少命中一個關鍵字
            if match_count >= 1:

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

                    "match": 100 + (
                        match_count * 10
                    ),

                    "reason": (
                        f"資料庫命中 "
                        f"{match_count} 個條件"
                    ),

                    "isTop": False,

                    "tags": [],

                    "image": product.get(
                        "image",
                        ""
                    ),

                    "link": ""
                })

        print(
            f"[DB Match] {len(matched)} 筆"
        )

        return matched

    except Exception as e:

        print(
            f"[DB Search Error] {e}"
        )

        return []