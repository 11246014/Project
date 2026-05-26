from data.mock_products import mock_products


def search_products(keyword):

    results = []

    # ===== 拆解關鍵字 =====

    keywords = keyword.split()

    for product in mock_products:

        product_text = (
            product["title"]
            + product["desc"]
            + product["category"]
        )

        # ===== 任一關鍵字符合就加入 =====

        for word in keywords:

            if word in product_text:

                results.append(product)

                break

    return results