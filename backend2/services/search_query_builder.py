# services/search_query_builder.py

# =========================
# Search Query Mapping
# =========================

USAGE_MAPPING = {

    "運動": "運動",

    "健康": "健康",

    "日常": "日常",

    "商務": "商務",

    "戶外": "戶外",
}

FEATURE_MAPPING = {

    "GPS": "GPS",

    "睡眠": "睡眠監測",

    "心率": "心率",

    "血氧": "血氧",

    "ECG": "ECG",

}

def build_search_query(keyword_result):

    query_parts = []

    # =========================
    # Product Type
    # =========================

    product_type = keyword_result.get(
        "product_type"
    )

    if product_type:

        query_parts.append(
            product_type
        )

    # =========================
    # Usage
    # =========================

    usage = keyword_result.get("usage")

    if usage in USAGE_MAPPING:

        query_parts.append(
            USAGE_MAPPING[usage]
        )

    # =========================
    # Features
    # =========================

    for feature in keyword_result.get(
        "features",
        []
    ):

        for key, value in FEATURE_MAPPING.items():

            if key in feature:

                query_parts.append(
                    value
                )

    # =========================
    # Remove Duplicate
    # =========================

    query_parts = list(
        dict.fromkeys(query_parts)
    )

    return " ".join(
        query_parts
    )