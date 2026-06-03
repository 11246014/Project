def format_product(product):

    # ===== Features 轉 Tags =====

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

    return {

        "name": product.get(
            "title",
            ""
        ),

        "price": product.get(
            "price",
            0
        ),

        "product_type": product.get(
            "product_type",
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

        "image": product.get(
            "image",
            ""
        )
    }