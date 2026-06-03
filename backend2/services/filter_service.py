from services.web_search_service import (
    web_search_products
)

from services.product_analyzer_service import (
    analyze_product
)


def build_search_keyword(filters):

    keywords = []

    # =========================
    # 裝置類型
    # =========================

    device_type = filters.get(
        "device_type",
        ""
    )

    if device_type:

        keywords.append(device_type)

    # =========================
    # 使用情境
    # =========================

    usage = filters.get(
        "usage",
        ""
    )

    if usage:

        if "運動" in usage:
            keywords.append("運動")

        elif "日常" in usage:
            keywords.append("日常")

        elif "健康" in usage:
            keywords.append("健康")

    # =========================
    # 風格
    # =========================

    style = filters.get(
        "style",
        ""
    )

    if style:

        if "商務" in style:
            keywords.append("商務")

        elif "時尚" in style:
            keywords.append("時尚")

    # =========================
    # 功能
    # =========================

    features = filters.get(
        "features",
        []
    )

    for feature in features:

        if "血氧" in feature:
            keywords.append("血氧")

        elif "GPS" in feature:
            keywords.append("GPS")

        elif "睡眠" in feature:
            keywords.append("睡眠監測")

    # =========================
    # OS
    # =========================

    os_type = filters.get(
        "os",
        ""
    )

    if os_type:

        keywords.append(os_type)

    # =========================
    # 最後組字串
    # =========================

    keyword = " ".join(keywords)

    print(f"[Search Keyword] {keyword}")

    return keyword


def filter_products(filters):

    try:

        # =========================
        # 取得搜尋關鍵字
        # =========================

        keyword = build_search_keyword(
            filters
        )

        # =========================
        # Web Search
        # =========================

        products = web_search_products(
            keyword
        )

        # =========================
        # 價格篩選
        # =========================

        max_price = filters.get(
            "max_price",
            999999
        )

        filtered_products = []

        for product in products:

            if (
                product.get(
                    "price",
                    0
                ) <= max_price
            ):

                filtered_products.append(
                    product
                )

        # =========================
        # AI 商品分析
        # =========================

        analyzed_products = []

        for product in filtered_products[:3]:

            analyzed = analyze_product(
                product
            )

            analyzed_products.append(
                analyzed
            )

        print(
            f"[Filter] 最終商品數量 {len(analyzed_products)}"
        )

        return analyzed_products

    except Exception as e:

        print(
            f"[Filter Service Error] {e}"
        )

        return []