# services/keyword_service.py

import json

from services.ollama_service import ask_ollama


def extract_keyword(user_message):

    """
    使用 Ollama 分析需求
    組成較適合 Google Shopping 的搜尋關鍵字
    """

    try:

        prompt = f"""
你是智慧穿戴商品需求分析助手。

請分析使用者需求：

{user_message}

請只回傳 JSON：

{{
    "product_type":"",
    "usage":"",
    "features":[],
    "os":"",
    "style":""
}}

規則：

product_type:
- 智慧手錶
- 智慧手環
- 藍牙耳機

usage:
- 運動
- 健康
- 日常
- 商務
- 戶外

features:
- GPS
- 睡眠監測
- 血氧
- ECG
- 心率
- 防水

os:
- iOS
- Android
- Cross

style:
- 商務
- 時尚
- 運動

重要規則：

1. 只能提取使用者明確提到的需求
2. 禁止根據品牌推測功能
3. 禁止根據常識補充功能
4. 未提及欄位請填空
5. features 只能包含使用者實際提到的功能
6. 若使用者只提到品牌名稱，不可自行補充功能
7. 若無法判斷 usage，請填 ""
8. 若無法判斷 style，請填 ""
9. 若無法判斷 os，請填 ""
10. 禁止猜測 GPS、ECG、血氧、防水等功能

範例1：

使用者：
推薦適合 iPhone 的 GPS 睡眠監測手錶

回傳：

{{
    "product_type":"智慧手錶",
    "usage":"日常",
    "features":["GPS","睡眠監測"],
    "os":"iOS",
    "style":""
}}

範例2：

使用者：
Apple Watch

回傳：

{{
    "product_type":"智慧手錶",
    "usage":"",
    "features":[],
    "os":"iOS",
    "style":""
}}

範例3：

使用者：
Garmin

回傳：

{{
    "product_type":"智慧手錶",
    "usage":"",
    "features":[],
    "os":"",
    "style":""
}}

範例4：

使用者：
我要 GPS

回傳：

{{
    "product_type":"",
    "usage":"",
    "features":["GPS"],
    "os":"",
    "style":""
}}

禁止輸出任何解釋文字。
禁止輸出 Markdown。
禁止輸出 ```json。
只允許輸出 JSON。
"""

        response = ask_ollama(prompt)

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

        print("\n========== Parsed ==========")
        print(data)
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

            query_parts.append(
                "Android"
            )

            if (
                "galaxy watch"
                not in user_message.lower()
            ):

                query_parts.append(
                    "Galaxy Watch"
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

            return search_keyword

    except Exception as e:

        print(
            f"[Keyword Extraction Error] {e}"
        )

        return ""

    return ""