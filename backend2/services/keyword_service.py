# services/keyword_service.py

import json
import re

from config.settings import KEYWORD_MODEL
from services.ai_service import ask_ai
from services.keyword_prompt import build_keyword_prompt
from services.search_query_builder import build_search_query


# ==================================================
# Constants
# ==================================================

# 品牌快速查詢
BRAND_KEYWORDS = {

    # Apple
    "apple": "Apple",
    "apple watch": "Apple Watch",

    # Samsung
    "samsung": "Samsung",
    "galaxy": "Samsung",
    "galaxy watch": "Galaxy Watch",
    "galaxy buds": "Galaxy Buds",

    # Garmin
    "garmin": "Garmin",

    # Huawei
    "huawei": "Huawei",

    # Google
    "google": "Google",
    "pixel watch": "Google",

    # Amazfit
    "amazfit": "Amazfit",

    # Fitbit
    "fitbit": "Fitbit",

    # Xiaomi
    "xiaomi": "Xiaomi",
    "mi band": "Xiaomi",

    # COROS
    "coros": "COROS",

    # Polar
    "polar": "Polar",

    # Suunto
    "suunto": "Suunto",

    # Smart Ring
    "oura": "Oura",
    "ringconn": "RingConn",

    # Earbuds
    "airpods": "AirPods",
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
    brand=None,
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

        # Budget 由 Gemini / AI Prompt 負責解析。
        # Python 不重新判斷使用者預算。
        "budget_min": budget_min or 0,
        "budget_max": budget_max or 0,

        "product_type": _none_if_empty(product_type),
        "brand": _none_if_empty(brand),
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

    Gemini 應該直接回傳 JSON。
    Python 只負責：
    1. 移除 Markdown code fence
    2. JSON parsing
    3. 確認結果為 dict

    不在這裡重新判斷使用者需求。
    """

    if not isinstance(response, str):
        raise ValueError(
            "AI response must be a string."
        )

    response = response.strip()

    # 移除 Gemini 偶爾可能產生的 Markdown code fence
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
# Normalize
# ==================================================

def normalize_keyword_result(
    data,
    user_message
):
    """
    將 AI 回傳資料正規化。

    這裡只處理系統需要的資料表示方式：

    1. 繁簡轉換
    2. features 格式
    3. Feature Alias
    4. Battery unknown value
    5. Style 明確性
    6. OS 明確性
    7. Usage 格式
    8. 空值處理

    不重新猜測使用者需求。
    不重新解析 Budget。
    不使用 Regex 覆蓋 Gemini 的 Budget。
    """

    # ==================================================
    # Traditional Chinese
    # ==================================================

    for key in (
        "product_type",
        "brand",
        "usage",
        "os",
        "style",
        "battery",
        "occupation",
        "age_group",
    ):

        value = data.get(key)

        # AI 有時會回：
        # ["iOS"]
        #
        # 這裡只處理格式，不重新判斷內容。
        if isinstance(value, list):

            value = (
                value[0]
                if value
                else ""
            )

        data[key] = _convert_traditional(
            value
        )

    # ==================================================
    # Features
    # ==================================================

    features = []

    for item in data.get(
        "features",
        []
    ):

        item = _convert_traditional(
            item
        )

        item = FEATURE_ALIAS.get(
            item,
            item
        )

        if item not in features:

            features.append(
                item
            )

    data["features"] = features

    # ==================================================
    # Battery
    # ==================================================

    if data.get(
        "battery"
    ) in UNKNOWN_VALUES:

        data["battery"] = ""

    # ==================================================
    # Style
    # ==================================================

    # 如果使用者沒有明確提到風格，
    # 不保留 AI 自行猜測的 Style。
    if not re.search(
        r"(商務|商务|時尚|时尚|運動|运动)",
        user_message,
    ):

        data["style"] = ""

    # ==================================================
    # OS
    # ==================================================

    # 如果使用者沒有明確提到：
    # iPhone / iOS / Android
    #
    # 就不接受 AI 自行猜測 Cross。
    if not re.search(
        r"(iphone|ios|android|安卓)",
        user_message,
        re.IGNORECASE,
    ):

        if data.get("os") == "Cross":

            data["os"] = ""

    # ==================================================
    # Usage
    # ==================================================

    usage = data.get(
        "usage",
        ""
    )

    if isinstance(
        usage,
        str
    ):

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

            # 睡眠是一個特殊情況：
            #
            # 睡眠可以同時代表：
            # 1. 使用情境
            # 2. 睡眠監測功能
            #
            # 因此兩邊都保留。
            if item in FEATURE_ALIAS:

                feature = FEATURE_ALIAS[
                    item
                ]

                if feature not in data[
                    "features"
                ]:

                    data[
                        "features"
                    ].append(
                        feature
                    )

                if item not in new_usage:

                    new_usage.append(
                        item
                    )

            else:

                if item not in new_usage:

                    new_usage.append(
                        item
                    )

        data["usage"] = "、".join(
            new_usage
        )

    # ==================================================
    # Empty Value
    # ==================================================

    for key in (
        "product_type",
        "brand",
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
    使用 Gemini / AI 分析使用者需求，
    並產生搜尋關鍵字。

    流程：

    User Message
        ↓
    Brand Shortcut
        ↓
    Device Shortcut
        ↓
    AI Keyword Extraction
        ↓
    JSON Parse
        ↓
    Normalize
        ↓
    Build Search Query
        ↓
    Keyword Result

    Budget 由 Gemini / Keyword Prompt 負責理解。

    Python 不再：
    - 使用 Validator 重新判斷
    - 使用 Regex 重新解析 Budget
    - 覆蓋 Gemini 的 Budget 結果
    """

    try:

        # ==================================================
        # Brand Shortcut
        # ==================================================

        msg = user_message.lower().strip()

        if msg in BRAND_KEYWORDS:

            return _keyword_result(
                keyword=BRAND_KEYWORDS[msg],
                brand=BRAND_KEYWORDS[msg]
            )

        # ==================================================
        # Device Shortcut
        # ==================================================

        device = user_message.strip()

        if device in DEVICE_KEYWORDS:

            print(
                f"[Device Shortcut] matched: {device}"
            )

            return _keyword_result(
                keyword=DEVICE_KEYWORDS[
                    device
                ],
                product_type=DEVICE_KEYWORDS[
                    device
                ]
            )

        # ==================================================
        # Build Prompt
        # ==================================================

        prompt = build_keyword_prompt(
            user_message
        )

        # ==================================================
        # Ask AI
        # ==================================================

        response = ask_ai(
            prompt,
            model_name=KEYWORD_MODEL
        )

        print(
            "\n========== Keyword Raw =========="
        )

        print(response)

        print(
            "=================================\n"
        )

        # ==================================================
        # Parse
        # ==================================================

        data = _parse_ai_response(
            response
        )

        # ==================================================
        # Normalize
        # ==================================================

        data = normalize_keyword_result(
            data,
            user_message
        )

        print(
            "[Budget Debug - Normalize] "
            f"min={data.get('budget_min')} "
            f"max={data.get('budget_max')}"
        )

        # ==================================================
        # Budget Final Check
        # ==================================================
        #
        # 只印出 Gemini 最終結果。
        #
        # 不修改 Budget。
        # ==================================================

        print(
            "[FINAL BUDGET CHECK] "
            f"min={data.get('budget_min')} "
            f"max={data.get('budget_max')}"
        )

        # ==================================================
        # Parsed Debug
        # ==================================================

        print(
            "\n========== Parsed =========="
        )

        print(data)

        print(
            f"Budget: "
            f"{data.get('budget_min')} ~ "
            f"{data.get('budget_max')}"
        )

        print(
            "============================\n"
        )

        # ==================================================
        # Build Search Query
        # ==================================================

        search_keyword = build_search_query(
            data,
            user_message
        )

        if search_keyword:

            print(
                f"[Keyword Extraction] "
                f"{search_keyword}"
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

                brand=data.get(
                    "brand"
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