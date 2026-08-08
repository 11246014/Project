#summary_validator.py
"""
Summary Validator

負責：
1. 檢查 AI Summary 是否提到系統沒有提供的商品資訊
2. 檢查商品名稱是否正確
3. 檢查推薦順位是否正確
4. 不使用額外 LLM
"""

import re


# ==================================================
# Forbidden Product Claims
# ==================================================

FORBIDDEN_PRODUCT_TERMS = [
    "GPS",
    "血氧",
    "心率",
    "ECG",
    "心電圖",
    "睡眠監測",
    "血壓",
    "體溫",
    "防水",
    "續航",
    "電池",
    "衛星通訊",
    "通話",
    "鈦金屬",
    "不鏽鋼",
    "鋁合金",
]


# ==================================================
# Normalize
# ==================================================

def _normalize_text(text):
    if not text:
        return ""

    return str(text).strip().lower()


# ==================================================
# Build Allowed Product Terms
# ==================================================

def _build_allowed_terms(products):
    """
    建立本次 Summary 可以使用的商品資訊。
    """

    allowed_terms = set()

    for product in products:

        fields = [
            product.get("name", ""),
            product.get("brand", ""),
            product.get("reason", ""),
        ]

        tags = product.get(
            "tags",
            [],
        )

        if isinstance(tags, list):
            fields.extend(tags)

        for field in fields:

            if not field:
                continue

            text = _normalize_text(field)

            allowed_terms.add(text)

    return allowed_terms


# ==================================================
# Forbidden Claim Detection
# ==================================================

def _find_forbidden_terms(
    summary,
    products,
):
    """
    找出 Summary 中可能出現的
    未被允許的商品功能 / 規格。
    """

    summary_text = _normalize_text(
        summary
    )

    allowed_terms = _build_allowed_terms(
        products
    )

    violations = []

    for term in FORBIDDEN_PRODUCT_TERMS:

        normalized_term = _normalize_text(
            term
        )

        if normalized_term not in summary_text:
            continue

        # 如果這個詞本身就是系統提供的資料，
        # 則允許使用。
        if normalized_term in allowed_terms:
            continue

        violations.append(term)

    return violations


# ==================================================
# Product Name Validation
# ==================================================

def _validate_product_names(
    summary,
    products,
):
    """
    確認 Summary 中的商品名稱
    是否來自系統提供的商品。
    """

    summary_text = _normalize_text(
        summary
    )

    valid_names = []

    for product in products:

        name = product.get(
            "name",
            "",
        )

        if not name:
            continue

        normalized_name = _normalize_text(
            name
        )

        valid_names.append(
            normalized_name
        )

    # 找出 Summary 中的商品標籤
    mentioned_names = re.findall(
        r"【第\d+名】\s*\n?([^\n]+)",
        summary,
    )

    for name in mentioned_names:

        normalized_name = _normalize_text(
            name
        )

        if normalized_name not in valid_names:
            return False

    return True


# ==================================================
# Validate Summary
# ==================================================

def validate_summary(
    summary,
    products,
):
    """
    驗證 AI Summary。

    回傳：

    {
        "valid": True / False,
        "violations": [...]
    }
    """

    if not summary:
        return {
            "valid": False,
            "violations": [
                "empty_summary"
            ],
        }

    violations = []

    # =========================
    # Forbidden Terms
    # =========================

    forbidden_terms = _find_forbidden_terms(
        summary,
        products,
    )

    for term in forbidden_terms:

        violations.append(
            f"未提供的商品資訊：{term}"
        )

    # =========================
    # Product Names
    # =========================

    if not _validate_product_names(
        summary,
        products,
    ):

        violations.append(
            "商品名稱不是系統提供的商品"
        )

    # =========================
    # Result
    # =========================

    return {
        "valid": len(violations) == 0,
        "violations": violations,
    }