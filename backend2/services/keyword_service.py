# services/keyword_service.py

import json
import re

from services.ai_service import ask_ai
from config.settings import KEYWORD_MODEL

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

            return {

                "keyword": "Apple Watch",

                "budget_min": 0,

                "budget_max": 0
            }

        if msg == "garmin":

            return {

                "keyword": "Garmin",

                "budget_min": 0,

                "budget_max": 0
            }

        if msg == "amazfit":

            return {

                "keyword": "Amazfit",

                "budget_min": 0,

                "budget_max": 0
            }

        if msg == "galaxy watch":

            return {

                "keyword": "Galaxy Watch",

                "budget_min": 0,

                "budget_max": 0
            }
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

        product_type = data.get(
            "product_type",
            ""
        )

        if product_type:
            query_parts.append(
                product_type
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

        query_parts = []

        # =====================
        # Product Type
        # =====================

        product_type = data.get(
            "product_type",
            ""
        )

        if product_type:
            query_parts.append(
                product_type
            )

        # =====================
        # Usage
        # =====================

        usage = data.get(
            "usage",
            ""
        )

        usage_mapping = {

            "運動": "運動",

            "健康": "健康",

            "日常": "日常",

            "商務": "商務",

            "戶外": "戶外"
        }

        if usage in usage_mapping:

            query_parts.append(
                usage_mapping[usage]
            )

        # =====================
        # Features
        # =====================

        features = data.get(
            "features",
            []
        )

        for feature in features:

            if "GPS" in feature:

                query_parts.append(
                    "GPS"
                )

            elif "睡眠" in feature:

                query_parts.append(
                    "睡眠監測"
                )

            elif "血氧" in feature:

                query_parts.append(
                    "血氧"
                )

            elif "ECG" in feature:

                query_parts.append(
                    "ECG"
                )

            elif "心率" in feature:

                query_parts.append(
                    "心率"
                )

            elif "防水" in feature:

                query_parts.append(
                    "防水"
                )

        # =====================
        # OS
        # =====================

        os_type = data.get(
            "os",
            ""
        )

        if os_type == "iOS":

            query_parts.append(
                "iPhone"
            )

            if (
                "apple watch"
                not in user_message.lower()
            ):

                query_parts.append(
                    "Apple Watch"
                )

        elif os_type == "Android":

            ...

            if (
                "galaxy watch"
                not in user_message.lower()
            ):

                query_parts.append(
                    "Galaxy Watch"
                )

        # =====================
        # Style
        # =====================

        style = data.get(
            "style",
            ""
        )

        if style == "商務":

            query_parts.append(
                "商務手錶"
            )

        elif style == "運動":

            query_parts.append(
                "運動手錶"
            )

        elif style == "時尚":

            query_parts.append(
                "時尚手錶"
            )
        # =====================
        # 去重
        # =====================

        query_parts = list(
            dict.fromkeys(
                query_parts
            )
        )

        search_keyword = " ".join(
            query_parts
        )

        if search_keyword:

            print(
                f"[Keyword Extraction] {search_keyword}"
            )

            return {

                "keyword": search_keyword,

                "budget_min": data.get(
                    "budget_min",
                    0
                ),

                "budget_max": data.get(
                    "budget_max",
                    0
                )
            }

    except Exception as e:

        print(
            f"[Keyword Extraction Error] {e}"
        )

        return {

            "keyword": "",

            "budget_min": 0,

            "budget_max": 0
        }

    return {

        "keyword": "",

        "budget_min": 0,

        "budget_max": 0
    }