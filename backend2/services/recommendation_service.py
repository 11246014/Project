import time

from services.ai_service import ask_ai
from services.chat_parser import parse_chat_message
from services.intent_service import detect_intent
from services.recommendation_pipeline import (
    recommend_from_need,
)
from services.summary_service import (
    generate_summary,
)

# =========================
# Keyword Conversation Memory
# =========================

user_history = []


def recommend_products(user_message):

    total_start = time.time()

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

        # =========================
        # Normal Chat
        # =========================

        if intent == "chat":

            reply = ask_ai(
                user_message
            )

            return {

                "summary": reply,

                "products": [],

                "user_need": None,
            }

        # =========================
        # Conversation Memory
        # =========================

        user_history.append(
            user_message
        )

        user_history = user_history[-3:]

        conversation = "\n".join(
            user_history
        )

        print("\n========== Conversation ==========")

        print(conversation)

        print("==================================\n")

        # =========================
        # Chat Parser
        # =========================

        keyword_start = time.time()

        recommendation_request = parse_chat_message(
            conversation
        )

        user_need = recommendation_request.need

        print(
            f"[Keyword Time] "
            f"{time.time() - keyword_start:.2f}s"
        )

        # =========================
        # Recommendation Pipeline
        # =========================

        pipeline_start = time.time()

        result = recommend_from_need(
            user_need
        )

        formatted_products = result["products"]

        budget_fallback = result["budget_fallback"]

        search_query = result["search_query"]

        print(
            f"[Pipeline Time] "
            f"{time.time() - pipeline_start:.2f}s"
        )

        print("\n====== Recommend Start ======")

        print(
            f"User: {user_message}"
        )

        print(
            f"Search Query: {search_query}"
        )

        print(
            f"Budget Fallback: {budget_fallback}"
        )

        print(
            f"Products: {len(formatted_products)}"
        )

        # =========================
        # No Product
        # =========================

        if not formatted_products:

            return {

                "summary": (
                    "目前尚未找到符合需求的商品，"
                    "可以再試試其他關鍵字。"
                ),

                "products": [],

                "user_need": user_need.to_dict(),
            }
        # =========================
        # Summary
        # =========================

        summary_start = time.time()

        summary = generate_summary(
            formatted_products,
            user_need,
            budget_fallback
        )

        print(
            f"[Summary Time] "
            f"{time.time() - summary_start:.2f}s"
        )

        print("====== Recommend End ======\n")

        print(
            f"[Total Time] "
            f"{time.time() - total_start:.2f}s"
        )

        # =========================
        # Return
        # =========================

        return {

            "summary": summary,

            "products": formatted_products,

            "user_need": user_need.to_dict(),
        }

    except Exception as e:

        import traceback

        print(
            f"[Recommendation Error] {e}"
        )

        traceback.print_exc()

        return {

            "summary": (
                "不好意思，目前推薦系統有點忙碌，"
                "請稍後再試～"
            ),

            "products": [],

            "user_need": None,

            "error": str(e),
        }