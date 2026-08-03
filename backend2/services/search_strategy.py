# services/search_strategy.py

OS_SEARCH_TERMS = {
    "iOS": ["Apple Watch"],
    "Android": ["Samsung"],
}


def build_search_strategy(need):

    strategy = {
        "search_terms": []
    }

    # 已指定品牌，不補搜尋策略
    if need.preferences.brand:
        return strategy

    os_name = need.preferences.os

    if os_name in OS_SEARCH_TERMS:
        strategy["search_terms"].extend(
            OS_SEARCH_TERMS[os_name]
        )

    return strategy