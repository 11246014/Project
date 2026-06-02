# services/keyword_service.py

import json
from services.ollama_service import ask_ollama


def extract_keyword(user_message):
    """
    使用 Ollama 分析使用者需求，
    組成較適合 Google Shopping 的搜尋關鍵字。

    回傳：
    str
    """

    try:
        prompt = f"""
你是一個智慧穿戴裝置商品分析助手。

請分析以下使用者需求：

{user_message}

請只回傳 JSON：

{{
  "product_type": "",
  "usage": ""
}}

範例：

使用者：
我想找適合跑步的智慧手錶

回傳：

{{
  "product_type":"智慧手錶",
  "usage":"跑步"
}}
"""

        response = ask_ollama(prompt)

        if "```" in response:
            response = response.replace("```json", "")
            response = response.replace("```", "")

        data = json.loads(response)

        query_parts = []

        if data.get("product_type"):
            query_parts.append(data["product_type"])

        if data.get("usage"):
            query_parts.append(data["usage"])

        search_keyword = " ".join(query_parts)

        if search_keyword:
            print(f"[Keyword Extraction] {search_keyword}")
            return search_keyword

    except Exception as e:
        print(f"[Keyword Extraction Error] {e}")

    return user_message.strip()