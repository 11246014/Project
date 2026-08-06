# services/ranking/helper.py

"""
Helper Service

負責：
1. 商品資料格式轉換
2. 共用工具函式
3. 商品文字與價格解析
"""


def extract_product_features(product):
    """
    取得商品 Feature 清單（去除重複值）
    """

    found = []

    for feature in _list(product.get("features")):

        feature = str(feature).strip()

        if feature and feature not in found:
            found.append(feature)

    return found


def _list(value):
    """
    將資料統一轉為 list 型別
    """

    if not value:
        return []

    if isinstance(value, list):
        return value

    return [value]


def _text(product):
    """
    合併商品所有可搜尋欄位
    """

    return " ".join(
        str(product.get(key, ""))
        for key in (
            "title",
            "raw_title",
            "name",
            "desc",
            "description",
        )
    ).lower()


def _price(product):
    """
    安全取得商品價格（int）
    """

    try:
        return int(product.get("price", 0) or 0)
    except Exception:
        return 0