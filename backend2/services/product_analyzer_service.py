import json

from services.ollama_service import ask_ollama
from config.settings import KEYWORD_MODEL

def analyze_product(product):

    try:

        prompt = f"""
你是一個智慧穿戴商品分析助手。

請根據商品名稱與商品描述分析商品資訊。

商品名稱：
{product.get("title", "")}

商品描述：
{product.get("desc", "")}

請推測：

1. 商品類型
2. 使用情境
3. 核心功能

只允許回傳 JSON。

格式如下：

{{
    "product_type": "",
    "usage": [],
    "features": []
}}

範例：

{{
    "product_type": "智慧手環",
    "usage": [
        "運動",
        "健康管理"
    ],
    "features": [
        "睡眠監測",
        "心率監測",
        "GPS"
    ]
}}

禁止輸出任何解釋文字。
禁止輸出 Markdown。
禁止輸出 ```json。
"""

        response = ask_ollama(
            prompt,
            model_name=KEYWORD_MODEL
        )
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

        product["product_type"] = data.get(
            "product_type",
            "未知商品"
        )

        product["usage"] = data.get(
            "usage",
            ["一般使用"]
        )

        product["features"] = data.get(
            "features",
            []
        )

        return product

    except Exception as e:

        print(
            f"[Product Analyzer Error] {e}"
        )

        product["product_type"] = "未知商品"

        product["usage"] = [
            "一般使用"
        ]

        product["features"] = []

        return product