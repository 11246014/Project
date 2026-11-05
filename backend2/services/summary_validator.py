# summary_validator.py
from typing import Any

# 摘要基本設定
MIN_SUMMARY_LENGTH = 10
MAX_SUMMARY_LENGTH = 500


def validate_summary(summary: Any) -> bool:
    """
    檢查 AI 摘要是否符合基本格式要求。

    Args:
        summary: AI 產生的摘要內容

    Returns:
        bool: 摘要是否通過基本檢查
    """

    # 必須為字串
    if not isinstance(summary, str):
        return False

    # 移除前後空白
    summary = summary.strip()

    # 不可為空
    if not summary:
        return False

    # 長度檢查
    if len(summary) < MIN_SUMMARY_LENGTH:
        return False

    if len(summary) > MAX_SUMMARY_LENGTH:
        return False

    return True


def normalize_summary(summary: Any) -> str:
    """
    整理摘要文字格式。

    Args:
        summary: 原始摘要內容

    Returns:
        str: 整理後的摘要
    """

    if not isinstance(summary, str):
        return ""

    # 移除前後空白
    summary = summary.strip()

    # 合併多餘空白行
    lines = [line.strip() for line in summary.splitlines() if line.strip()]

    return "\n".join(lines)


def validate_and_normalize(summary: Any) -> str:
    """
    進行摘要整理與基本驗證。

    Args:
        summary: 原始摘要內容

    Returns:
        str: 通過基本檢查後的摘要；
             若未通過則回傳空字串。
    """

    normalized = normalize_summary(summary)

    if not validate_summary(normalized):
        return ""

    return normalized
