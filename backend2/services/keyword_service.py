def extract_keyword(user_message):

    """
    目前先直接使用使用者輸入作為搜尋關鍵字

    未來：
    - Ollama 關鍵字提取
    - 關鍵字清洗
    - 關鍵字排序
    - 模糊搜尋

    再加回來
    """

    return user_message.strip()