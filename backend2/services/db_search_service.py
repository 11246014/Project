from services.backend1_client import get_db_products


async def search_db_products(keyword):

    try:

        products = await get_db_products()

        keyword = keyword.lower()

        matched = []

        for product in products:

            text = f"""
            {product.get("name", "")}
            {product.get("description", "")}
            """

            if keyword in text.lower():

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

                    "rating": 5,

                    "match": 100,

                    "reason": "來自資料庫商品",

                    "isTop": False,

                    "tags": [],

                    "image": "",

                    "link": ""
                })

        return matched

    except Exception as e:

        print(
            f"[DB Search Error] {e}"
        )

        return []