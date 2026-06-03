import json

from services.ollama_service import ask_ollama
from services.keyword_service import extract_keyword
from services.web_search_service import web_search_products
from services.product_formatter import format_product
from services.product_analyzer_service import analyze_product


# ===== 簡易聊天記憶 =====

chat_history = []


def recommend_products(user_message):

    global chat_history

    try:

        # ===== 記錄聊天 =====

        chat_history.append(
            f"使用者: {user_message}"
        )

        chat_history = chat_history[-6:]

        conversation = "\n".join(
            chat_history
        )

        # ===== Keyword =====

        search_keyword = extract_keyword(
            user_message
        )

        print("======")
        print("User:", user_message)
        print("Keyword:", search_keyword)
        print("======")

        # ===== Web Search =====

        filtered_products = web_search_products(
            search_keyword
        )

        print(
            f"搜尋結果數量: {len(filtered_products)}"
        )

        # ===== Product Analyzer =====

        analyzed_products = []

        for product in filtered_products:

            analyzed_products.append(
                analyze_product(product)
            )

        filtered_products = analyzed_products

        print("===== Analyze Result =====")

        for p in filtered_products:
            print(p)

        # ===== 沒找到商品 =====

        if not filtered_products:

            final_prompt = f"""
你是一位台灣智慧穿戴裝置專賣店店員。

使用繁體中文與自然聊天口氣。

最近對話：
{conversation}

使用者最新訊息：
{user_message}

目前尚未找到符合條件的商品。

請：
1. 自然回覆使用者
2. 詢問需求
3. 不要推薦不存在的商品
4. 控制在3句內
"""

            ai_reply = ask_ollama(
                final_prompt
            )

            chat_history.append(
                f"AI: {ai_reply}"
            )

            return {

                "summary": ai_reply,

                "products": []
            }

        # ===== 商品格式統一 =====

        formatted_products = []

        for product in filtered_products:

            formatted_products.append(
                format_product(product)
            )

        # ===== 建立商品摘要 =====

        product_text = ""

        for idx, product in enumerate(
            formatted_products[:3],
            start=1
        ):

            product_text += f"""
商品{idx}

名稱：
{product.get('name', '')}

價格：
{product.get('price', 0)}

評分：
{product.get('rating', 0)}

推薦理由：
{product.get('reason', '')}

"""

        print("===== Product Summary =====")
        print(product_text)

        # ===== AI 推薦 =====

        final_prompt = f"""
你是一位台灣智慧穿戴裝置專業導購員。

請根據使用者需求與商品資料進行推薦。

使用者需求：
{user_message}

最近對話：
{conversation}

商品資料：
{product_text}

規則：

1. 必須提到商品名稱
2. 必須說明推薦原因
3. 優先推薦最符合需求的商品
4. 可提到價格或評分
5. 使用繁體中文
6. 不要反問問題
7. 不要要求補充資訊
8. 不要說自己是AI
9. 控制在150字內

輸出範例：

根據您的需求，Garmin Forerunner 570 是最推薦的選擇，具備完整跑步功能且評價優異。若希望兼顧價格與健康監測功能，Samsung Galaxy Watch8 也是不錯的選擇。

請直接輸出推薦內容。
"""

        ai_reply = ask_ollama(
            final_prompt
        )

        # ===== AI回覆記錄 =====

        chat_history.append(
            f"AI: {ai_reply}"
        )

        chat_history = chat_history[-6:]

        # ===== 回傳前端 =====

        return {

            "summary": ai_reply,

            "products": formatted_products
        }

    except Exception as e:

        print(
            f"[Recommendation Error] {e}"
        )

        return {

            "summary": "不好意思，目前推薦系統有點忙碌，請稍後再試～",

            "products": [],

            "error": str(e)
        }