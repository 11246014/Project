from data.mock_products import mock_products


def web_search_products(keyword):

    results = []

    keyword = keyword.lower()

    for product in mock_products:

        text = f"""
        {product.get("title", "")}
        {product.get("desc", "")}
        {product.get("category", "")}
        {product.get("platform", "")}
        """

        if keyword in text.lower():

            results.append(product)

    return results