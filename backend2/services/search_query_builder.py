# services/search_query_builder.py

# =========================
# Search Query Mapping
# =========================

USAGE_MAPPING = {
    "運動": "運動",
    "跑步": "跑步",
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
    # Search Query 只使用：
    # Brand
    # Product Type
    # Usage
    #
    # OS 不再轉換成品牌
    # Feature 暫時不加入 Query
    # ==========================================

    brand = keyword_result.get("brand")
    product_type = keyword_result.get("product_type")
    usage = keyword_result.get("usage")

    # ==========================================
    # Brand
    # ==========================================

    if brand:
        query_parts.append(brand)

    # ==========================================
    # Product Type
    # ==========================================

    if product_type:
        query_parts.append(product_type)

    # ==========================================
    # Usage
    # ==========================================

    mapped_usage = USAGE_MAPPING.get(usage)

    if mapped_usage:
        query_parts.append(mapped_usage)

    # ==========================================
    # Features
    #
    # 暫時不要加入 Search Query。
    # Features 留給後面的 Filter / Ranking 處理。
    # ==========================================

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