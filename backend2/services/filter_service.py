from data.mock_products import mock_products


def filter_products(filters):

    results = []

    usage = filters.get("usage", "")
    max_price = filters.get("max_price", 999999)

    for product in mock_products:

        # ===== 使用情境篩選 =====

        usage_match = (
            usage == ""
            or usage in product.get("usage", [])
        )

        # ===== 價格篩選 =====

        price_match = (
            product["price"] <= max_price
        )

        # ===== 全部符合 =====

        if usage_match and price_match:

            results.append(product)

    return results