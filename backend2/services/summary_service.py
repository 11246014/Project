import time

from config.settings import SUMMARY_MODEL
from services.ai_service import ask_ai


# ==================================================
# Persona Context
# ==================================================

def _build_persona_text(persona):

    if not persona:
        return ""

    parts = []

    if persona.age_range:
        parts.append(f"年齡層：{persona.age_range}")

    if persona.occupation:
        parts.append(f"職業：{persona.occupation}")

    if persona.usage_scope:

        scope_map = {
            "個人使用": "此次用途為個人使用",
            "家庭共用": "此次用途為家庭共用",
            "要送禮": "此次用途為送禮",
        }

        parts.append(
            scope_map.get(
                persona.usage_scope,
                persona.usage_scope
            )
        )

    if persona.current_device:
        parts.append(
            f"目前使用裝置：{persona.current_device}"
        )

    if not parts:
        return ""

    return (
        "【使用者背景】\n"
        + "\n".join(parts)
        + "\n\n"
    )


# ==================================================
# User Need Context
# ==================================================

def _build_user_need_context(user_need):

    if not user_need:
        return ""

    lines = []

    if user_need.device_type:
        lines.append(
            f"裝置：{user_need.device_type}"
        )

    if user_need.usage:
        lines.append(
            "用途：" +
            "、".join(user_need.usage)
        )

    if user_need.features:
        lines.append(
            "需求功能：" +
            "、".join(user_need.features)
        )

    if user_need.preferences.os:
        lines.append(
            f"手機系統：{user_need.preferences.os}"
        )

    if user_need.preferences.brand:
        lines.append(
            f"偏好品牌：{user_need.preferences.brand}"
        )

    if (
        user_need.budget.max
        and user_need.budget.max > 0
    ):
        lines.append(
            f"預算：約 {user_need.budget.max} 元"
        )

    if not lines:
        return ""

    return (
        "【使用者需求】\n"
        + "\n".join(lines)
        + "\n\n"
    )


# ==================================================
# Product Context
# ==================================================

def _build_product_context(products):

    result = []

    for idx, product in enumerate(products, start=1):

        tags = product.get("tags", [])

        if isinstance(tags, list):
            tag_text = "、".join(tags)
        else:
            tag_text = str(tags)

        result.append(
            f"""
【第 {idx} 名】

商品：{product.get("name", "")}
品牌：{product.get("brand", "")}
價格：{product.get("price", "")} 元
推薦度：{product.get("match", 0)}%
推薦原因：{product.get("reason", "")}
標籤：{tag_text}
""".strip()
        )

    return "\n\n-----------------------------\n\n".join(result)


# ==================================================
# Prompt Builder
# ==================================================

def _build_summary_prompt(
    persona_text,
    user_need_text,
    product_text,
):

    return f"""
你是 WearWise AI 智慧穿戴導購顧問。

你的工作不是列出商品資料，
而是向使用者介紹推薦商品。

{persona_text}

{user_need_text}

請遵守以下規則：

1. 必須依照推薦順位介紹商品。
2. 第一順位介紹較完整。
3. 第二順位簡短介紹。
4. 第三順位一句即可。
5. 每個商品都要提到價格。
6. 優先依照推薦原因改寫成自然介紹。
7. 可呼應使用者背景。
8. 不得虛構商品功能。
9. 不得自行補充不存在的規格。
10. 不得根據品牌或型號推測功能。
11. 不要比較商品優劣。
12. 不要寫開場白。
13. 不要寫結論。
14. 使用繁體中文。
15. 控制在150~220字。
16. 不要使用 Markdown。
17. 直接輸出純文字。

以下為推薦商品資訊：

{product_text}
"""
# ==================================================
# Summary Generator
# ==================================================

def generate_summary(
    products,
    user_need,
    budget_fallback=False
):

    print("[Summary Service]")

    if not products:
        return "目前沒有找到符合條件的推薦商品。"

    # =========================
    # Build Context
    # =========================

    persona_text = _build_persona_text(
        user_need.persona
    )

    user_need_text = _build_user_need_context(
        user_need
    )

    product_text = _build_product_context(
        products
    )

    summary_prompt = _build_summary_prompt(
        persona_text,
        user_need_text,
        product_text
    )

    # =========================
    # Debug
    # =========================

    print("\n========== Summary Context ==========")

    print(persona_text)

    print(user_need_text)

    print(product_text)

    print("=====================================\n")

    budget_notice = ""

    if (
        budget_fallback
        and user_need.budget.max
    ):

        budget_notice = (
            f"未找到符合 "
            f"{user_need.budget.min} ~ "
            f"{user_need.budget.max} 元預算的商品，"
            f"以下推薦價格最接近需求的商品。\n\n"
        )

    try:

        print("[Summary Start]")

        start = time.time()

        ai_reply = ask_ai(
            summary_prompt,
            model_name=SUMMARY_MODEL
        )

        elapsed = (
            time.time() - start
        )

        print(
            f"[Summary Time] {elapsed:.2f}s"
        )

        if budget_notice:
            ai_reply = (
                budget_notice
                + ai_reply
            )

        if (
            not ai_reply
            or
            not ai_reply.strip()
        ):

            ai_reply = (
                "已為您整理符合需求的商品，"
                "請參考以下推薦。"
            )

        print(
            "\n========== Summary =========="
        )

        print(ai_reply)

        print("=============================\n")

        print("[Summary End]")

        return ai_reply

    except Exception as e:

        print(
            f"[Summary Error] {e}"
        )

        return (
            "目前 AI 暫時無法產生推薦摘要，"
            "但已為您整理符合需求的商品。"
        )