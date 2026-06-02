def format_product(product):

    return {

        "name": product.get("title", ""),

        "price": product.get("price", 0),

        "tags": product.get("tags", []),

        "rating": product.get("rating", 0),

        "match": product.get("match", 0),

        "reason": product.get("reason", ""),

        "isTop": product.get("isTop", False),

        "platform": product.get("platform", ""),

        "link": product.get("link", ""),

        "image": product.get("image", "")
    }