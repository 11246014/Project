import json

from services.ollama_service import ask_ollama


def analyze_product(product):

    try:

        prompt = f"""
你是一個智慧穿戴商品分析助手。

請分析以下商品：

商品名稱：
{product.get("title", "")}

商品描述：
{product.get("desc", "")}

請只回傳 JSON：

{{
    "product_type": "",
    "usage": [],
    "features": []
}}

範例：

{{
    "product_type": "智慧手環",
    "usage": ["運動", "健康管理"],
    "features": ["睡眠監測", "心率監測"]
}}
"""

        response = ask_ollama(prompt)

        if "```json" in response:
            response = response.replace("```json", "")

        if "```" in response:
            response = response.replace("```", "")

        data = json.loads(response)

        product["product_type"] = data.get(
            "product_type",
            ""
        )

        product["usage"] = data.get(
            "usage",
            []
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

        product["product_type"] = ""
        product["usage"] = []
        product["features"] = []

        return product