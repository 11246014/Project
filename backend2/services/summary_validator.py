# summary_validator.py
"""
Summary Validator

目的：
1. 防止 AI 使用系統沒有提供的商品資訊
2. 防止不同商品之間的資訊混用
3. 防止 AI 自行新增功能 / 規格 / 數字
4. 確認推薦順位正確
5. 允許 AI 對商品名稱與句子做自然語言改寫
6. 不使用額外 LLM
"""

import re


# ==================================================
# Forbidden Product Terms
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
    "運動模式",
    "跑步模式",
]


# ==================================================
# Normalize
# ==================================================

def _normalize_text(text):
    """
    基本文字標準化。

    用途：
    - 大小寫統一
    - 移除前後空白
    - 合併連續空白
    """

    if text is None:
        return ""

    text = str(text).strip().lower()

    return re.sub(
        r"\s+",
        " ",
        text,
    )


def _normalize_compact(text):
    """
    更強的文字標準化。

    移除：
    - 空白
    - 標點
    - 特殊符號

    用於商品名稱比對。
    """

    text = _normalize_text(text)

    return re.sub(
        r"[\s\W_]+",
        "",
        text,
    )


# ==================================================
# Name Tokens
# ==================================================

def _extract_name_tokens(text):
    """
    從商品名稱抽取較有辨識度的 Token。

    主要保留：
    - 英文
    - 數字
    - 型號
    - 連續中文片段

    目的：
    允許：

        跑步運動腕錶 W100 黑色

    與：

        W100 黑色跑步運動腕錶

    被視為同一商品。

    """

    text = _normalize_text(text)

    tokens = re.findall(
        r"[a-z0-9]+|[\u4e00-\u9fff]{2,}",
        text,
    )

    return set(tokens)


# ==================================================
# Build Product Allowed Terms
# ==================================================

def _build_product_allowed_terms(product):
    """
    建立單一商品可以使用的資訊。

    每個商品獨立建立，
    避免第 1 名的資訊被第 2 名使用。
    """

    allowed_terms = set()

    fields = [
        product.get("name", ""),
        product.get("brand", ""),
        product.get("price", ""),
        product.get("match", ""),
        product.get("reason", ""),
    ]

    tags = product.get(
        "tags",
        [],
    )

    if isinstance(tags, list):
        fields.extend(tags)

    elif tags:
        fields.append(tags)

    for field in fields:

        if field is None:
            continue

        text = _normalize_text(field)

        if not text:
            continue

        allowed_terms.add(text)

        # #GPS → gps
        if text.startswith("#"):
            allowed_terms.add(
                text.lstrip("#")
            )

    return allowed_terms


# ==================================================
# Product Evidence Text
# ==================================================

def _build_product_evidence_text(product):
    """
    建立單一商品的可驗證資料。

    Summary 只能使用這些資料作為商品事實。
    """

    fields = [
        product.get("name", ""),
        product.get("brand", ""),
        product.get("price", ""),
        product.get("match", ""),
        product.get("reason", ""),
    ]

    tags = product.get(
        "tags",
        [],
    )

    if isinstance(tags, list):
        fields.extend(tags)

    elif tags:
        fields.append(tags)

    return " ".join(
        _normalize_text(field)
        for field in fields
        if field
    )


# ==================================================
# Product Name Validation
# ==================================================

def _validate_product_name(
    summary,
    product,
):
    """
    驗證商品名稱。

    不再要求 100% 完整字串一致。

    允許：
        跑步運動腕錶 W100 黑色

    改寫成：
        W100 黑色跑步運動腕錶

    但仍然要求具有足夠的商品名稱特徵，
    避免完全不同商品被誤判成相同。
    """

    name = product.get(
        "name",
        "",
    )

    if not name:
        return True

    normalized_name = _normalize_compact(
        name
    )

    summary_text = _normalize_compact(
        summary
    )

    # ------------------------------------------
    # Case 1
    # 完整名稱存在
    # ------------------------------------------

    if normalized_name in summary_text:
        return True

    # ------------------------------------------
    # Case 2
    # Token overlap
    # ------------------------------------------

    name_tokens = _extract_name_tokens(
        name
    )

    summary_tokens = _extract_name_tokens(
        summary
    )

    if not name_tokens:
        return False

    matched_tokens = (
        name_tokens
        & summary_tokens
    )

    overlap_ratio = (
        len(matched_tokens)
        / len(name_tokens)
    )

    # ------------------------------------------
    # Case 3
    # 型號 / 英數字 Token
    #
    # 如果商品有 W100、165、Bip5 等
    # 型號資訊，要求型號至少出現。
    # ------------------------------------------

    model_tokens = {
        token
        for token in name_tokens
        if re.search(
            r"[a-z]",
            token,
        )
        or re.search(
            r"\d",
            token,
        )
    }

    if model_tokens:

        model_match = (
            model_tokens
            & summary_tokens
        )

        if not model_match:
            return False

        # 有型號 + 至少部分名稱 Token
        return overlap_ratio >= 0.30

    # ------------------------------------------
    # 沒有型號時
    # 要求較高的名稱 Token 重疊
    # ------------------------------------------

    return overlap_ratio >= 0.60


# ==================================================
# Forbidden Claim Detection
# ==================================================

def _find_forbidden_terms(
    summary,
    product,
):
    """
    檢查單一商品 Summary 是否
    使用商品資料沒有提供的功能 / 規格。

    例如：

        Summary:
        這款支援 GPS

        Product:
        沒有 GPS 證據

    → violation
    """

    summary_text = _normalize_text(
        summary
    )

    evidence_text = _build_product_evidence_text(
        product
    )

    violations = []

    for term in FORBIDDEN_PRODUCT_TERMS:

        normalized_term = _normalize_text(
            term
        )

        if normalized_term not in summary_text:
            continue

        # 商品自己的資料有提供
        if normalized_term in evidence_text:
            continue

        violations.append(term)

    return violations


# ==================================================
# Numeric Claim Detection
# ==================================================

def _extract_numbers(text):
    """
    擷取 Summary 中的阿拉伯數字。

    目的：
    防止 AI 自己產生：
        14 天
        100%
        5ATM
        1000 元

    等系統沒有提供的數字。
    """

    if not text:
        return set()

    return set(
        re.findall(
            r"\d+(?:\.\d+)?",
            str(text),
        )
    )


def _find_unsupported_numbers(
    summary,
    product,
):
    """
    確認 Summary 中的數字
    是否至少存在於該商品自己的資料。
    """

    summary_numbers = _extract_numbers(
        summary
    )

    if not summary_numbers:
        return []

    evidence_text = _build_product_evidence_text(
        product
    )

    evidence_numbers = _extract_numbers(
        evidence_text
    )

    unsupported = (
        summary_numbers
        - evidence_numbers
    )

    return sorted(
        unsupported
    )


# ==================================================
# Parse Ranked Sections
# ==================================================

def _parse_ranked_sections(summary):
    """
    將 Summary 拆成：

        第1名
        第2名
        第3名

    回傳：

        {
            1: "...",
            2: "...",
            3: "..."
        }
    """

    pattern = re.compile(
        r"【第\s*(\d+)\s*名】"
        r"\s*(.*?)"
        r"(?=【第\s*\d+\s*名】|$)",
        re.S,
    )

    matches = pattern.findall(
        summary
    )

    sections = {}

    for rank, content in matches:

        try:
            rank_number = int(rank)

        except ValueError:
            continue

        sections[rank_number] = (
            content.strip()
        )

    return sections


# ==================================================
# Validate Ranked Products
# ==================================================

def _validate_ranked_products(
    summary,
    products,
):
    """
    逐一驗證：

        第1名 → products[0]
        第2名 → products[1]
        第3名 → products[2]

    每個商品只驗證自己的 section。
    """

    sections = _parse_ranked_sections(
        summary
    )

    violations = []

    for index, product in enumerate(
        products,
        start=1,
    ):

        if index > 3:
            break

        section = sections.get(
            index
        )

        # --------------------------------------
        # 缺少商品段落
        # --------------------------------------

        if not section:

            violations.append(
                f"缺少第{index}名商品內容"
            )

            continue

        # --------------------------------------
        # Product Name
        # --------------------------------------

        if not _validate_product_name(
            section,
            product,
        ):

            violations.append(
                f"第{index}名商品名稱錯誤"
            )

        # --------------------------------------
        # Forbidden Claims
        # --------------------------------------

        forbidden_terms = (
            _find_forbidden_terms(
                section,
                product,
            )
        )

        for term in forbidden_terms:

            violations.append(
                f"第{index}名使用未提供資訊：{term}"
            )

        # --------------------------------------
        # Unsupported Numbers
        # --------------------------------------

        unsupported_numbers = (
            _find_unsupported_numbers(
                section,
                product,
            )
        )

        for number in unsupported_numbers:

            violations.append(
                f"第{index}名使用未提供數字：{number}"
            )

    return violations


# ==================================================
# Validate Summary
# ==================================================

def validate_summary(
    summary,
    products,
):
    """
    驗證 AI Summary。

    主要目的：
        防止 AI 幻覺。

    不要求 AI 必須逐字複製商品名稱，
    但要求：

        1. 商品順位正確
        2. 商品名稱具有足夠辨識度
        3. 商品功能必須有自身資料支持
        4. 數字必須有自身資料支持
        5. 不允許跨商品使用資訊
    """

    if not summary:

        return {
            "valid": False,
            "violations": [
                "empty_summary"
            ],
        }

    violations = _validate_ranked_products(
        summary,
        products,
    )

    return {
        "valid": len(violations) == 0,
        "violations": violations,
    }