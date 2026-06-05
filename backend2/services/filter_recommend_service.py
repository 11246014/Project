import json

from services.ai_service import ask_ai


def generate_filter_recommendation(filters, products):

    prompt = f"""
    你是一位台灣智慧穿戴裝置導購專家。

    使用者需求：
    {json.dumps(filters, ensure_ascii=False)}

    符合需求的商品：
    {json.dumps(products, ensure_ascii=False)}

    請用繁體中文，
    用自然聊天方式，
    幫使用者推薦商品。

    不要太像廣告。

    回覆控制在 3 句內。
    """

    result = ask_ai(prompt)

    return result