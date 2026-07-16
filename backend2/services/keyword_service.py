# services/keyword_service.py

import json
import re

from services.ai_service import ask_ai
from config.settings import KEYWORD_MODEL
from services.search_query_builder import (
    build_search_query
)

def _as_list(value):
    if value is None or value == "":
        return []

    if isinstance(value, list):
        return value

    return [value]


def _none_if_empty(value):
    if value in ("", [], {}, 0):
        return None

    return value


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
    age_group=None
):
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
        "age_group": _none_if_empty(age_group)
    }


def extract_keyword(user_message):

    """
    使用 Ollama 分析需求
    組成較適合 Google Shopping 的搜尋關鍵字
    """

    try:

        # =====================
        # 品牌直通
        # =====================

        msg = user_message.lower().strip()

        if msg == "apple watch":

            return _keyword_result(
                keyword="Apple Watch"
            )

        if msg == "garmin":

            return _keyword_result(
                keyword="Garmin"
            )

        if msg == "amazfit":

            return _keyword_result(
                keyword="Amazfit"
            )

        if msg == "galaxy watch":

            return _keyword_result(
                keyword="Galaxy Watch"
            )
        if msg == "智慧手錶":

            return {
                "keyword": "智慧手錶",
                "budget_min": 0,
                "budget_max": 0
            }

        if msg == "智慧手環":

            return {
                "keyword": "智慧手環",
                "budget_min": 0,
                "budget_max": 0
            }

        if msg == "藍牙耳機":

            return {
                "keyword": "藍牙耳機",
                "budget_min": 0,
                "budget_max": 0
            }
        
        ...
        prompt = f"""
你是智慧穿戴商品需求分析助手。

請分析使用者需求：

{user_message}

只回傳 JSON：

{{
    "product_type":"",
    "usage":"",
    "features":[],
    "os":"",
    "style":"",
    "battery":"",
    "occupation":"",
    "age_group":"",
    "budget_min":0,
    "budget_max":0
}}

product_type：

常見類型：

- 智慧手錶
- 智慧手環
- 藍牙耳機

若使用者提到其他商品類型，
請保留原始名稱，
不要自行修改。

usage：

常見類型：

- 運動
- 健康
- 日常
- 商務
- 戶外

若使用者描述更具體需求，
可直接保留原始描述。

features：

可包含：

- GPS
- 睡眠監測
- 血氧
- ECG
- 心率
- 防水

os：

- iOS
- Android
- Cross

style：

- 商務
- 時尚
- 運動

budget_min：
最低預算

budget_max：
最高預算

若使用者提到：

1000以下
5000內
10000~20000
1萬到2萬
預算15000

請轉換為：

budget_min
budget_max

規則：

1. 只能提取使用者明確提到的需求

2. 禁止根據品牌推測功能

3. 禁止根據常識補充功能

4. 未提及欄位請填：

- ""
- []
- 0

5. features 只能包含使用者實際提到的功能

6. 若使用者只提到品牌名稱，不可補充功能

7. 若無法判斷 usage，填 ""

8. 若無法判斷 style，填 ""

9. 若無法判斷 os，填 ""

10. 禁止猜測 GPS、ECG、血氧、防水等功能

11. 禁止輸出解釋文字

12. 禁止輸出 Markdown

13. 禁止輸出 ```json

14. 只允許輸出合法 JSON

15. 回傳格式必須可直接被 json.loads() 解析
"""

        response = ask_ai(
            prompt,
            model_name=KEYWORD_MODEL
        )

        print("\n========== Keyword Raw ==========")
        print(response)
        print("=================================\n")

        if "```json" in response:
            response = response.replace(
                "```json",
                ""
            )

        if "```" in response:
            response = response.replace(
                "```",
                ""
            )

        data = json.loads(
            response.strip()
        )
        # =====================
        # Budget Validation
        # =====================

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
