#product_formatter.py
def format_product(product):

    # =========================
    # Features 轉 Tags
    # =========================

    features = product.get(
        "features",
        []
    )

    tags = []

    if features:

        tags = [
            f"#{feature}"
            for feature in features
        ]

    else:

        tags = product.get(
            "tags",
            []
        )

    # =========================
    # 圖片處理
    # =========================

    image = product.get(
        "image",
        ""
    )

    # 防止 None
    if not image:

        image = ""

    # =========================
    # 商品名稱過長處理
    # =========================

    name = product.get(
        "title",
        ""
    )

    # =========================
    # 回傳格式
    # =========================

    return {

        "name": name,

        "price": product.get(
            "price",
            0
        ),
        
        "product_type": product.get(
            "product_type",
            ""
        ),

        "brand": product.get(
            "brand",
            ""
        ),

        "usage": product.get(
            "usage",
            []
        ),

        "features": features,

        "tags": tags,

        "rating": product.get(
            "rating",
            0
        ),

        "match": product.get(
            "match",
            0
        ),

        "base_score": product.get(
            "base_score",
            product.get("match", 0)
        ),

        "final_score": product.get(
            "final_score",
            product.get("base_score", product.get("match", 0))
        ),

        "is_sponsored": product.get(
            "is_sponsored",
            False
        ),

        "reason": product.get(
            "reason",
            ""
        ),

        "isTop": product.get(
            "isTop",
            False
        ),

        "platform": product.get(
            "platform",
            ""
        ),

        "link": product.get(
            "link",
            ""
        ),

        "image": image
    }