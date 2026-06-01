import json

from services.ollama_service import ask_ollama
from services.search_service import search_products
from services.keyword_service import extract_keyword
from services.product_formatter import format_product

# ===== 簡易聊天記憶 =====

chat_history = []


def recommend_products(user_message):

    global chat_history

    try:

        # ===== 記錄聊天 =====

        chat_history.append(f"使用者: {user_message}")

        # 只保留最近 6 句

        chat_history = chat_history[-6:]

        conversation = "\n".join(chat_history)

        # ===== 提取搜尋關鍵字 =====

        search_keyword = extract_keyword(user_message)

        print("======")
        print("User:", user_message)
        print("Keyword:", search_keyword)
        print("======")

        # ===== 搜尋商品 =====

        filtered_products = search_products(search_keyword)

        print("搜尋結果數量:", len(filtered_products))
        print(filtered_products)

        # ===== 商品格式統一 =====

        formatted_products = []

        for product in filtered_products:

            formatted_products.append(
                format_product(product)
            )

        print("格式化後商品數量:", len(formatted_products))
        print(formatted_products)

        # ===== 沒找到商品 =====

        if not formatted_products:

            final_prompt = f"""
            你是一位台灣智慧穿戴裝置專賣店店員。

            使用繁體中文與自然聊天口氣。

            使用者剛剛說：
            {user_message}

            最近對話：
            {conversation}

            請自然回應使用者，
            並進一步了解需求。

            不要急著推商品。
            """

            ai_reply = ask_ollama(final_prompt)

            # ===== 記錄 AI 回覆 =====

            chat_history.append(f"AI: {ai_reply}")

            return {
                "summary": ai_reply,
                "products": []
            }

        # ===== 有找到商品 =====

        final_prompt = f"""
        你是一位在台灣智慧穿戴專賣店工作的專業店員。

        你的任務不是直接推銷商品，
        而是像真人店員一樣理解客人需求，
        再慢慢推薦適合的產品。

        規則：

        1. 使用繁體中文
        2. 使用自然台灣口語
        3. 像朋友聊天
        4. 不要太像機器人
        5. 不要一次講太多規格
        6. 回覆控制在 2~4 句

        最近對話：
        {conversation}

        使用者最新訊息：
        {user_message}

        搜尋到的商品：
        {json.dumps(formatted_products, ensure_ascii=False)}

        請根據商品內容，
        生成一段自然推薦摘要。
        """

        ai_reply = ask_ollama(final_prompt)

        # ===== 記錄 AI 回覆 =====

        chat_history.append(f"AI: {ai_reply}")

        # ===== 回傳前端格式 =====

        return {
            "summary": ai_reply,
            "products": formatted_products
        }

    except Exception as e:

        return {
            "summary": "不好意思，目前推薦系統有點忙碌，請稍後再試～",
            "products": [],
            "error": str(e)
        }