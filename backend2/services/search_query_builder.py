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

    "睡眠": "睡眠",
    "睡眠監測": "睡眠",

    "健康": "",
    "健康監測": "",

    "心率": "心率",
    "血氧": "血氧",
    "ECG": "ECG",
}

OS_MAPPING = {
    "iOS": "Apple Watch",
    "Android": "Samsung",
}


def build_search_query(keyword_result, user_message=""):

    message = user_message.lower()
    query_parts = []

    # ==========================================
    # 若 AI 沒抓到 OS，從原始訊息補
    # ==========================================

    if not keyword_result.get("os"):

        if "iphone" in message:
            keyword_result["os"] = "iOS"

        elif "android" in message:
            keyword_result["os"] = "Android"

    # ==========================================
    # Primary Search Query
    #
    # 優先順序：
    # Brand
    #   ↓
    # OS Mapping
    #   ↓
    # Product Type
    # ==========================================

    brand = keyword_result.get("brand")
    product_type = keyword_result.get("product_type")
    os_name = keyword_result.get("os")

    mapped_os = OS_MAPPING.get(os_name)

    if brand:
        query_parts.append(brand)

    elif mapped_os:
        query_parts.append(mapped_os)

    elif product_type:
        query_parts.append(product_type)

    # ==========================================
    # Usage
    # ==========================================

    usage = keyword_result.get("usage")

    mapped_usage = USAGE_MAPPING.get(usage)

    if mapped_usage:
        query_parts.append(mapped_usage)

    # ==========================================
    # Features
    # ==========================================

    for feature in keyword_result.get("features", []):

        mapped_feature = FEATURE_MAPPING.get(feature)

        if mapped_feature:
            query_parts.append(mapped_feature)

    # ==========================================
    # Remove Duplicate
    # ==========================================

    query_parts = list(dict.fromkeys(query_parts))

    query_parts = [
        q.strip()
        for q in query_parts
        if q and q.strip()
    ]

    search_query = " ".join(query_parts)

    return search_query