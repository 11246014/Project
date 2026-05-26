from services.ollama_service import ask_ollama


def extract_keyword(user_message):

    prompt = f"""
    你是一個商品搜尋關鍵字助手。

    請根據使用者需求，
    提取最適合搜尋智慧穿戴商品的關鍵字。

    只能回傳：
    1~3 個繁體中文關鍵字

    不要解釋。
    不要句子。
    不要標點符號。

    使用者需求：
    {user_message}
    """

    result = ask_ollama(prompt)

    return result.strip()