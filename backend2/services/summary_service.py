#summary_service.py
import time

from config.settings import SUMMARY_MODEL
from services.ai_service import ask_ai

DEBUG_SUMMARY = True

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

你的工作是根據系統提供的推薦結果，
以自然、專業、容易閱讀的方式向使用者介紹商品。

========================
使用者背景
========================

{persona_text}

========================
使用者需求
========================

{user_need_text}

========================
推薦商品
========================

{product_text}

========================
輸出規則（必須遵守）
========================

【商品規則】

1. 只能介紹系統提供的商品。
2. 不得新增任何商品。
3. 商品名稱必須完全一致。
4. 不得省略任何商品。
5. 若有三項商品，必須介紹三項。
6. 若只有一項商品，只介紹該商品。
7. 不得改變推薦順位。

【內容規則】

8. 第一順位介紹較完整（2~3句）。
9. 第二順位簡短介紹（1~2句）。
10. 第三順位一句即可。
11. 優先根據「推薦原因」介紹。
12. 可以參考標籤(Tag)自然帶入。
13. 可以呼應使用者需求。
14. 可以呼應使用者背景(Persona)。

【禁止事項】

15. 不得虛構商品功能。
16. 不得根據品牌猜測規格。
17. 不得自行補充不存在的資訊。
18. 不得比較商品優劣。
19. 不得推薦未提供商品。
20. 不得加入自己的意見。

【語氣】

21. 使用自然繁體中文。
22. 像門市導購，而不是商品規格表。
23. 每項商品都像是在向使用者介紹。
24. 不要流水帳。
25. 不要照抄推薦原因。

【格式】

26. 不要使用 Markdown。
27. 不要使用項目符號。
28. 不要寫開場白。
29. 不要寫結論。
30. 直接輸出推薦內容。

格式如下：

【第1名】
商品名稱
介紹內容

【第2名】
商品名稱
介紹內容

【第3名】
商品名稱
介紹內容

開始撰寫推薦內容。

========================
開始撰寫
========================
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

    if DEBUG_SUMMARY:

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