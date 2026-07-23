# services/search_query_builder.py

# =========================
# Search Query Mapping
# =========================

USAGE_MAPPING = {
    "運動": "運動",
    "健康": "健康",

    # 這些對 Google Shopping 幾乎沒有搜尋價值
    "日常": "",
    "商務": "",
    "戶外": "",
}

FEATURE_MAPPING = {
    "GPS": "GPS",
    "睡眠": "睡眠監測",
    "心率": "心率",
    "血氧": "血氧",
    "ECG": "ECG",
}

OS_MAPPING = {
    "iOS": "Apple Watch",
    "Android": "Galaxy Watch",
}


def build_search_query(keyword_result):

    query_parts = []

    # =========================
    # Brand
    # =========================

    brand = keyword_result.get("brand")

    if brand:
        query_parts.append(brand)

    # =========================
    # Product Type
    # =========================

    product_type = keyword_result.get("product_type")

    if product_type:
        query_parts.append(product_type)

    # =========================
    # OS
    # =========================

    os_name = keyword_result.get("os")

    mapped_os = OS_MAPPING.get(os_name)

    if mapped_os:
        query_parts.append(mapped_os)

    # =========================
    # Usage
    # =========================

    usage = keyword_result.get("usage")

    mapped_usage = USAGE_MAPPING.get(usage)

    if mapped_usage:
        query_parts.append(mapped_usage)

    # =========================
    # Features
    # =========================

    for feature in keyword_result.get("features", []):

        for key, value in FEATURE_MAPPING.items():

            if key in feature:
                query_parts.append(value)

    # =========================
    # Remove Duplicate
    # =========================

    query_parts = list(dict.fromkeys(query_parts))

    # 移除空字串
    query_parts = [
        q.strip()
        for q in query_parts
        if q and q.strip()
    ]

    search_query = " ".join(query_parts)

    return search_query