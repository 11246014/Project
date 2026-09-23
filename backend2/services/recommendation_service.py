# recommendation_service.py

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


# =========================
# Need Completeness Check
# =========================

def is_need_complete(user_need):
    """
    判斷目前使用者需求是否足夠開始商品推薦。

    目前採用簡單規則：

    1. 必須知道商品類型
    2. 至少要有一項實際需求：
       - 用途
       - 功能
       - 預算

    需求不足時，不進入 Search / Ranking。
    """

    if not user_need:
        return False

    # =========================
    # Product Type
    # =========================

    has_device_type = bool(
        user_need.device_type
    )

    # =========================
    # Usage
    # =========================

    has_usage = bool(
        user_need.usage
    )

    # =========================
    # Features
    # =========================

    has_features = bool(
        user_need.features
    )

    # =========================
    # Budget
    # =========================

    has_budget = (
        user_need.budget.min is not None
        or
        user_need.budget.max is not None
    )

    # =========================
    # Final Check
    # =========================

    has_actual_requirement = (
        has_usage
        or
        has_features
        or
        has_budget
    )

    return (
        has_device_type
        and
        has_actual_requirement
    )

def wants_recommendation_guidance(user_message):
    """
    判斷使用者是否表示自己不確定需求，
    並希望系統協助決定。
    """

    text = user_message.lower()

    guidance_keywords = [
        "不知道",
        "不確定",
        "沒想法",
        "你推薦",
        "你幫我選",
        "幫我挑",
        "你覺得哪種",
        "都可以",
    ]

    return any(
        keyword in text
        for keyword in guidance_keywords
    )

# =========================
# Follow-up Question
# =========================

def generate_follow_up(
    user_need,
    user_message=None
):

    # =========================
    # 0. 使用者希望系統協助決定
    # =========================

    if (
        user_message
        and
        wants_recommendation_guidance(
            user_message
        )
    ):

        if (
            user_need.budget.min is None
            and
            user_need.budget.max is None
        ):

            return (
                "可以～那我可以依照一般使用需求幫你挑。"
                "先確認一下，你大概希望控制在多少預算內呢？"
            )

    # =========================
    # 1. 用途
    # =========================

    if not user_need.usage:

        return (
            "想先了解一下，你主要會把這支智慧手錶拿來做什麼呢？"
            "例如運動、睡眠監測，還是日常使用？"
        )
    # =========================
    # 2. 功能
    # =========================

    if not user_need.features:

        return (
            "了解～那你有沒有特別想要的功能呢？"
            "例如心率監測、睡眠追蹤、GPS 或血氧監測？"
        )

    # =========================
    # 3. 預算
    # =========================

    if (
        user_need.budget.min is None
        and
        user_need.budget.max is None
    ):

        return (
            "了解～那你的預算大概落在哪個範圍呢？"
        )

    # =========================
    # 4. 其他偏好
    # =========================

    if not user_need.preferences.os:

        return (
            "另外，你平常使用 iPhone 還是 Android 手機呢？"
        )

    # =========================
    # 5. 已經足夠
    # =========================

    return None

# =========================
# Main Recommendation
# =========================

def recommend_products(
    user_message,
    persona=None
):

    total_start = time.time()

    global user_history

    try:

        # =========================
        # Intent Detection
        # =========================

        intent = detect_intent(
            user_message,
            in_recommendation=bool(user_history)
        )

        print(
            f"[Intent] {intent}"
        )

        # =========================
        # Normal Chat
        # =========================

        if intent == "chat":

            chat_prompt = f"""
請使用繁體中文回答使用者。

使用者：
{user_message}

要求：

1. 使用自然、親切的繁體中文。
2. 不要使用簡體中文。
3. 不需要推薦商品，除非使用者明確提出商品需求。
4. 回答要像自然聊天，不要像制式客服。
"""

            reply = ask_ai(
                chat_prompt
            )

            return {

                "summary": reply.strip(),

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

        print(
            "\n========== Conversation =========="
        )

        print(
            conversation
        )

        print(
            "==================================\n"
        )

        # =========================
        # Chat Parser
        # =========================

        keyword_start = time.time()

        recommendation_request = parse_chat_message(
            conversation
        )

        user_need = recommendation_request.need

        # =========================
        # Structured Persona Override
        # =========================
        #
        # 前端已將：
        # - 年齡層
        # - 職業
        # - 目前裝置
        #
        # 結構化傳入。
        #
        # 若有值則優先採用。
        # =========================

        if persona:

            if persona.get("age_range"):

                user_need.persona.age_range = (
                    persona["age_range"]
                )

            if persona.get("occupation"):

                user_need.persona.occupation = (
                    persona["occupation"]
                )

            if persona.get("current_device"):

                user_need.persona.current_device = (
                    persona["current_device"]
                )

        print(
            f"[Persona Merged] "
            f"{user_need.persona}"
        )

        print(
            f"[Keyword Time] "
            f"{time.time() - keyword_start:.2f}s"
        )

        # =========================
        # Need Completeness Check
        # =========================

        print(
            "\n========== Need Check =========="
        )

        print(
            f"Device Type: "
            f"{user_need.device_type}"
        )

        print(
            f"Usage: "
            f"{user_need.usage}"
        )

        print(
            f"Features: "
            f"{user_need.features}"
        )

        print(
            f"Budget: "
            f"{user_need.budget}"
        )

        need_complete = is_need_complete(
            user_need
        )

        print(
            f"[Need Complete] "
            f"{need_complete}"
        )

        print(
            "================================\n"
        )

        # =========================
        # Need Not Complete
        # =========================

        if not need_complete:

            print(
                "[Recommendation] "
                "Need incomplete -> Follow-up"
            )

            follow_up = generate_follow_up(
                user_need
            )

            print(
                f"[Follow-up] "
                f"{follow_up}"
            )

            return {

                "summary": follow_up,

                "products": [],

                "user_need": user_need.to_dict(),
            }

        # =========================
        # Recommendation Pipeline
        # =========================

        pipeline_start = time.time()

        result = recommend_from_need(
            user_need
        )

        formatted_products = (
            result["products"]
        )

        budget_fallback = (
            result["budget_fallback"]
        )

        search_query = (
            result["search_query"]
        )

        print(
            f"[Pipeline Time] "
            f"{time.time() - pipeline_start:.2f}s"
        )

        print(
            "\n====== Recommend Start ======"
        )

        print(
            f"User: "
            f"{user_message}"
        )

        print(
            f"Search Query: "
            f"{search_query}"
        )

        print(
            f"Budget Fallback: "
            f"{budget_fallback}"
        )

        print(
            f"Products: "
            f"{len(formatted_products)}"
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

        print(
            "====== Recommend End ======\n"
        )

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
            f"[Recommendation Error] "
            f"{e}"
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