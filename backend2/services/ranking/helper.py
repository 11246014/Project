# services/ranking/helper.py

def extract_product_features(product):
    """
    取得商品 Feature 清單
    """

    found = []

    features = _list(product.get("features"))

    for feature in features:

        feature = str(feature).strip()

        if feature and feature not in found:
            found.append(feature)

    return found


def _list(value):
    """
    確保資料一定回傳 list
    """

    if not value:
        return []

    if isinstance(value, list):
        return value

    return [value]


def _text(product):
    """
    將商品所有可搜尋文字合併
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
    安全取得商品價格
    """

    try:
        return int(product.get("price", 0) or 0)
    except Exception:
        return 0