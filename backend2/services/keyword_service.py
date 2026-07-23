#keyword_service.py
import json
import re

from config.settings import KEYWORD_MODEL
from services.ai_service import ask_ai
from services.keyword_prompt import build_keyword_prompt
from services.search_query_builder import (
    build_search_query,
)

# ==================================================
# Constants
# ==================================================

# 品牌快速查詢
BRAND_KEYWORDS = {
    "apple watch": "Apple Watch",
    "garmin": "Garmin",
    "amazfit": "Amazfit",
    "galaxy watch": "Galaxy Watch",
}

# 裝置快速查詢
DEVICE_KEYWORDS = {
    "智慧手錶": "智慧手錶",
    "智慧手環": "智慧手環",
    "藍牙耳機": "藍牙耳機",
}

# AI 常見簡體修正
ZH_MAP = {
    "睡眠监测": "睡眠監測",
    "商务": "商務",
    "运动": "運動",
    "健康监测": "健康監測",
}

# 功能別名
FEATURE_ALIAS = {
    "睡眠": "睡眠監測",
    "睡眠品質": "睡眠監測",
    "記錄睡眠": "睡眠監測",
}

# AI 常見未知值
UNKNOWN_VALUES = {
    "未知",
    "unknown",
    "Unknown",
    "N/A",
    None,
}

# ==================================================
# Helpers
# ==================================================

def _as_list(value):
    """
    保證回傳 List。
    """

    if value is None or value == "":
        return []

    if isinstance(value, list):
        return value

    return [value]


def _none_if_empty(value):
    """
    空值統一轉成 None。
    """

    if value in ("", [], {}, 0):
        return None

    return value


def _convert_traditional(text):
    """
    將 AI 回傳的簡體轉為繁體。
    """

    if not isinstance(text, str):
        return text

    for old, new in ZH_MAP.items():
        text = text.replace(old, new)

    return text


def _keyword_result(
    keyword="",
    budget_min=0,
    budget_max=0,
    product_type=None,
    usage=None,
    features=None,
    os=None,
    style=None,
    battery=None,
    occupation=None,
    age_group=None,
):
    """
    Keyword Extraction 統一回傳格式。
    """

    return {
        "keyword": keyword or "",
        "budget_min": budget_min or 0,
        "budget_max": budget_max or 0,
        "product_type": _none_if_empty(product_type),
        "usage": _none_if_empty(usage),
        "features": _as_list(features),
        "os": _none_if_empty(os),
        "style": _none_if_empty(style),
        "battery": _none_if_empty(battery),
        "occupation": _none_if_empty(occupation),
        "age_group": _none_if_empty(age_group),
    }


# ==================================================
# Parser
# ==================================================

def _parse_ai_response(response):
    """
    解析 AI 回傳 JSON。
    """

    if not isinstance(response, str):
        raise ValueError(
            "AI response must be a string."
        )

    response = response.strip()

    response = response.replace(
        "```json",
        ""
    )

    response = response.replace(
        "```",
        ""
    )

    response = response.strip()

    data = json.loads(response)

    if not isinstance(data, dict):
        raise ValueError(
            "AI response must be a JSON object."
        )

    return data
# ==================================================
# Validation
# ==================================================

def _validate_keyword_result(data):
    """
    驗證並修正 AI 回傳資料格式。

    僅修正資料型別與缺少欄位，
    不推測、不修改使用者需求。
    """

    if not isinstance(data, dict):
        return {}

    defaults = {
        "product_type": "",
        "usage": "",
        "features": [],
        "os": "",
        "style": "",
        "battery": "",
        "occupation": "",
        "age_group": "",
        "budget_min": 0,
        "budget_max": 0,
    }

    # 補齊缺少欄位
    for key, default in defaults.items():
        data.setdefault(key, default)

    # features 一律轉 List
    if not isinstance(data["features"], list):
        if data["features"] in ("", None):
            data["features"] = []
        else:
            data["features"] = [data["features"]]

    # usage
    if data["usage"] is None:
        data["usage"] = ""

    # budget
    try:
        data["budget_min"] = int(data["budget_min"])
    except Exception:
        data["budget_min"] = 0

    try:
        data["budget_max"] = int(data["budget_max"])
    except Exception:
        data["budget_max"] = 0

    return data


# ==================================================
# Normalize
# ==================================================

def normalize_keyword_result(data, user_message):
    """
    將 AI 回傳資料正規化。

    只修正格式，
    不猜測需求。
    """

    # --------------------------
    # Traditional Chinese
    # --------------------------

    for key in (
        "product_type",
        "usage",
        "os",
        "style",
        "battery",
        "occupation",
        "age_group",
    ):

        data[key] = _convert_traditional(
            data.get(key)
        )

    # --------------------------
    # Features
    # --------------------------

    features = []

    for item in data.get("features", []):

        item = _convert_traditional(item)

        item = FEATURE_ALIAS.get(
            item,
            item
        )

        if item not in features:
            features.append(item)

    data["features"] = features

    # --------------------------
    # Battery
    # --------------------------

    if data.get("battery") in UNKNOWN_VALUES:
        data["battery"] = ""

    # --------------------------
    # Style
    # --------------------------

    if not re.search(
        r"(商務|商务|時尚|时尚|運動|运动)",
        user_message,
    ):
        data["style"] = ""

    # --------------------------
    # OS
    # --------------------------

    if not re.search(
        r"(iphone|ios|android|安卓)",
        user_message,
        re.IGNORECASE,
    ):

        if data.get("os") == "Cross":
            data["os"] = ""

    # --------------------------
    # Usage
    # --------------------------

    usage = data.get("usage", "")

    if isinstance(usage, str):

        usage = _convert_traditional(
            usage
        )

        parts = re.split(
            r"[、,，/ ]+",
            usage
        )

        new_usage = []

        for item in parts:

            item = item.strip()

            if not item:
                continue

            if item in FEATURE_ALIAS:

                feature = FEATURE_ALIAS[item]

                if feature not in data["features"]:
                    data["features"].append(
                        feature
                    )

            else:

                if item not in new_usage:
                    new_usage.append(item)

        data["usage"] = "、".join(
            new_usage
        )

    # --------------------------
    # Empty Value
    # --------------------------

    for key in (
        "product_type",
        "usage",
        "os",
        "style",
        "battery",
        "occupation",
        "age_group",
    ):

        if data.get(key) in (
            None,
            "None",
            "null",
        ):
            data[key] = ""

    return data
# ==================================================
# Extract Flow
# ==================================================

def extract_keyword(user_message):
    """
    使用 AI 分析使用者需求，
    並產生搜尋關鍵字。
    """

    try:

        # --------------------------
        # Brand Shortcut
        # --------------------------

        msg = user_message.lower().strip()

        if msg in BRAND_KEYWORDS:

            return _keyword_result(
                keyword=BRAND_KEYWORDS[msg]
            )

        # --------------------------
        # Device Shortcut
        # --------------------------

        device = user_message.strip()

        if device in DEVICE_KEYWORDS:

            return _keyword_result(
                keyword=DEVICE_KEYWORDS[device]
            )

        # --------------------------
        # Build Prompt
        # --------------------------

        prompt = build_keyword_prompt(
            user_message
        )

        # --------------------------
        # Ask AI
        # --------------------------

        response = ask_ai(
            prompt,
            model_name=KEYWORD_MODEL
        )

        print("\n========== Keyword Raw ==========")
        print(response)
        print("=================================\n")

        # --------------------------
        # Parse
        # --------------------------

        data = _parse_ai_response(
            response
        )

        # --------------------------
        # Validation
        # --------------------------

        data = _validate_keyword_result(data)

        # --------------------------
        # Normalize
        # --------------------------

        data = normalize_keyword_result(
            data,
            user_message
        )

        # --------------------------
        # Budget Validation
        # --------------------------

        has_budget = bool(

            re.search(

                r"(預算|\d+)",

                user_message

            )

        )

        if not has_budget:

            data["budget_min"] = 0

            data["budget_max"] = 0

        print("\n========== Parsed ==========")
        print(data)

        print(
            f"Budget: "
            f"{data.get('budget_min')} ~ "
            f"{data.get('budget_max')}"
        )

        print("============================\n")

        # --------------------------
        # Build Search Query
        # --------------------------

        search_keyword = build_search_query(
            data
        )

        if search_keyword:

            print(
                f"[Keyword Extraction] {search_keyword}"
            )

            return _keyword_result(

                keyword=search_keyword,

                budget_min=data.get(
                    "budget_min",
                    0
                ),

                budget_max=data.get(
                    "budget_max",
                    0
                ),

                product_type=data.get(
                    "product_type"
                ),

                usage=data.get(
                    "usage"
                ),

                features=data.get(
                    "features"
                ),

                os=data.get(
                    "os"
                ),

                style=data.get(
                    "style"
                ),

                battery=data.get(
                    "battery"
                ),

                occupation=data.get(
                    "occupation"
                ),

                age_group=data.get(
                    "age_group"
                )

            )

    except Exception as e:

        print(
            f"[Keyword Extraction Error] {e}"
        )

        return _keyword_result()

    return _keyword_result()