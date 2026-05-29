from services.web_search_service import web_search_products


def search_products(keyword):

    results = []

    # ===== 拆解關鍵字 =====

    keywords = keyword.split()

    # ===== 呼叫 web search =====

    products = web_search_products(keyword)

    for product in products:

        product_text = (
            product.get("title", "")
            + product.get("desc", "")
            + product.get("category", "")
        )

        # ===== 任一關鍵字符合 =====

        for word in keywords:

            if word in product_text:

                results.append(product)

                break

    return results