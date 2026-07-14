import time

from services.intent_service import detect_intent
from services.ai_service import ask_ai
from services.chat_parser import parse_chat_message
from services.recommendation_pipeline import recommend_from_need
from services.summary_service import generate_summary

# =========================
# 簡易聊天記憶
# =========================

chat_history = []

# Keyword 專用記憶
user_history = []

# =========================
# 判斷是否為商品需求
# =========================

def is_product_request(message):

    keywords = [

        "手錶",
        "手環",
        "耳機",
        "穿戴",

        "推薦",
        "想找",

        "運動",
        "睡眠",
        "GPS",

        "健康",
        "智慧",

        "apple",
        "watch",

        "garmin",
        "amazfit",

        "galaxy",
        "huawei",

        "fitbit"
    ]
    for keyword in keywords:

        if keyword in message:

            return True

    return True


def recommend_products(user_message):

    total_start = time.time()
    global chat_history
    global user_history

    try:

        # =========================
        # Intent Detection
        # =========================

        intent = detect_intent(
            user_message
        )

        print(
            f"[Intent] {intent}"
        )

        if intent == "chat":

            reply = ask_ai(
                user_message
            )

            return {

                "summary": reply,

                "products": []
            }


        # =========================
        # 記錄聊天
        # =========================

        chat_history.append(
            f"使用者: {user_message}"
        )

        user_history.append(
            user_message
        )

        # AI摘要用
        chat_history = chat_history[-6:]

        # Keyword Extraction用
        user_history = user_history[-3:]

        conversation = "\n".join(
            user_history
        )

        # =========================
        # Keyword Extraction
        # =========================

        print("\n========== Conversation ==========")
        print(conversation)
        print("==================================\n")

        start = time.time()

        conversation_for_keyword = "\n".join(
            conversation.split("\n")[-5:]
        )

        recommendation_request = parse_chat_message(
            conversation_for_keyword
        )

        user_need = recommendation_request.need
        print(
            f"[Keyword Time] "
            f"{time.time() - start:.2f}s"
        )

        result = recommend_from_need(user_need)

        formatted_products = result["products"]
        budget_fallback = result["budget_fallback"]
        search_query = result["search_query"]

        print("\n====== Recommend Start ======")
        print(f"User: {user_message}")
        print(f"Search Query: {search_query}")
        print(f"[Products] 共 {len(formatted_products)} 筆")
        # =========================
        # 沒找到商品
        # =========================

        if not formatted_products:

            ai_reply = (
                "目前尚未找到符合需求的商品，"
                "可以再試試其他關鍵字。"
            )

            return {

                "summary": ai_reply,

                "products": [],

                "user_need": user_need.to_dict()
            }
        summary = generate_summary(
            formatted_products,
            user_need,
            budget_fallback
        )

        # =========================
        # AI 回覆記錄
        # =========================

        chat_history.append(
            f"AI: {summary}"
        )
        chat_history = chat_history[-6:]

        print(
            f"[Total Time] "
            f"{time.time() - total_start:.2f}s"
        )

        print("====== Recommend End ======\n")

        # =========================
        # 回傳前端
        # =========================

        return {

            "summary": summary,

            "products": formatted_products,

            "user_need": user_need.to_dict()
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
