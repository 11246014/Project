import json

from services.ollama_service import ask_ollama
from services.search_service import search_products
from services.keyword_service import extract_keyword

# 簡易聊天記憶
chat_history = []


def recommend_products(user_message):

    global chat_history

    try:

        # ===== 記錄聊天 =====

        chat_history.append(f"使用者: {user_message}")

        # 只保留最近 6 句
        chat_history = chat_history[-6:]

        conversation = "\n".join(chat_history)

        # ===== 搜尋商品 =====

        search_keyword = extract_keyword(user_message)

        filtered_products = search_products(search_keyword)

        # ===== 如果沒有找到商品 =====

        if not filtered_products:

            final_prompt = f"""
            你是一位台灣智慧穿戴裝置專賣店的店員。

            使用繁體中文與自然聊天口氣。

            使用者剛剛說：
            {user_message}

            最近對話：
            {conversation}

            請像真人一樣自然回應他，
            並試著進一步了解需求。

            不要急著推商品。
            """

            ai_reply = ask_ollama(final_prompt)

            # 記錄 AI 回覆
            chat_history.append(f"AI: {ai_reply}")

            return {
                "reply": ai_reply,
                "products": []
            }

        # ===== 有找到商品 =====

        final_prompt = f"""
        你是一位在台灣智慧穿戴專賣店工作的專業店員。

        你的任務不是直接推銷商品，
        而是像真人店員一樣先理解客人的需求，
        再慢慢推薦適合的產品。

        你要：
        1. 使用繁體中文
        2. 使用自然台灣口語
        3. 像朋友聊天，不要太機器人
        4. 不要一次講太多規格
        5. 如果資訊不足，要主動提問
        6. 推薦時要像真人店員，不要像商品介紹頁
        7. 回覆控制在 2~4 句

        最近對話：
        {conversation}

        使用者最新訊息：
        {user_message}

        搜尋到的商品：
        {json.dumps(filtered_products, ensure_ascii=False)}

        請參考商品的平台、價格與功能特色。

        請根據商品內容，
        用自然聊天方式推薦適合的商品。

        不要像商品頁介紹，
        要像真人店員。
        """

        ai_reply = ask_ollama(final_prompt)

        # 記錄 AI 回覆
        chat_history.append(f"AI: {ai_reply}")

        return {
            "reply": ai_reply,
            "products": filtered_products
        }

    except Exception as e:

        return {
            "reply": "不好意思，目前推薦系統有點忙碌，請稍後再試～",
            "products": [],
            "error": str(e)
        }