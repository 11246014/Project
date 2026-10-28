#product_formatter.py

import re


def clean_product_title(title):
    """清除商品標題中的賣場前綴、促銷文字與尾端編號。"""

    if not title:
        return ""

    title = str(title).strip()

    # 1. 移除開頭的賣場名稱，例如『澄橘』或【某某賣場】
    title = re.sub(
        r"^\s*[『「【\[][^』」】\]]+[』」】\]]\s*",
        "",
        title,
    )

    # 2. 移除包含促銷或二手宣傳字樣的括號區塊
    promo_keywords = (
        "歡迎折抵",
        "折抵",
        "二手",
        "福利品",
        "限時優惠",
        "特價",
        "現貨",
    )

    bracket_pattern = r"[《〈（(【\[].*?[》〉）)】\]]"

    def remove_promo(match):
        text = match.group(0)

        if any(keyword in text for keyword in promo_keywords):
            return ""

        return text

    title = re.sub(
        bracket_pattern,
        remove_promo,
        title,
    )

    # 3. 移除尾端獨立的商品編號，例如 A87108
    title = re.sub(
        r"\s*[A-Z]{1,4}\d{4,}\s*$",
        "",
        title,
    )
    # 4. 整理多餘空白
    title = re.sub(
        r"\s+",
        " ",
        title,
    ).strip()

    return title


def format_product(product):

    # =========================
    # Features 轉 Tags
    # =========================

    features = product.get(
        "features",
        []
    )

    tags = []

    if features:

        tags = [
            f"#{feature}"
            for feature in features
        ]

    else:

        tags = product.get(
            "tags",
            []
        )

    # =========================
    # 圖片處理
    # =========================

    image = product.get(
        "image",
        ""
    )

    # 防止 None
    if not image:

        image = ""

    # =========================
    # 商品名稱過長處理
    # =========================

    name = clean_product_title(
        product.get(
            "title",
            ""
        )
    )
    # =========================
    # 回傳格式
    # =========================

    return {

        "id": product.get("id"),
        
        "name": name,

        "price": product.get(
            "price",
            0
        ),
        
        "product_type": product.get(
            "product_type",
            ""
        ),

        "brand": product.get(
            "brand",
            ""
        ),

        "usage": product.get(
            "usage",
            []
        ),

        "features": features,

        "tags": tags,

        "rating": product.get(
            "rating",
            0
        ),

        "match": product.get(
            "match",
            0
        ),

        "base_score": product.get(
            "base_score",
            product.get("match", 0)
        ),

        "final_score": product.get(
            "final_score",
            product.get("base_score", product.get("match", 0))
        ),

        "is_sponsored": product.get(
            "is_sponsored",
            False
        ),

        "reason": product.get(
            "reason",
            ""
        ),

        "isTop": product.get(
            "isTop",
            False
        ),

        "platform": product.get(
            "platform",
            ""
        ),

        "link": product.get(
            "link",
            ""
        ),

        "image": image
    }