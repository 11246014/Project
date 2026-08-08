import time

from config.settings import SUMMARY_MODEL
from services.ai_service import ask_ai

from services.summary_validator import (
    validate_summary,
)

DEBUG_SUMMARY = True


# ==================================================
# Persona Context
# ==================================================

def _build_persona_text(persona):

    if not persona:
        return ""

    parts = []

    if persona.age_range:
        parts.append(
            f"年齡層：{persona.age_range}"
        )

    if persona.occupation:
        parts.append(
            f"職業：{persona.occupation}"
        )

    if persona.usage_scope:

        scope_map = {
            "個人使用": "此次用途為個人使用",
            "家庭共用": "此次用途為家庭共用",
            "要送禮": "此次用途為送禮",
        }

        parts.append(
            scope_map.get(
                persona.usage_scope,
                persona.usage_scope,
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
            "用途："
            + "、".join(user_need.usage)
        )

    if user_need.features:
        lines.append(
            "需求功能："
            + "、".join(user_need.features)
        )

    if (
        user_need.preferences
        and user_need.preferences.os
    ):
        lines.append(
            f"手機系統："
            f"{user_need.preferences.os}"
        )

    if (
        user_need.preferences
        and user_need.preferences.brand
    ):
        lines.append(
            f"偏好品牌："
            f"{user_need.preferences.brand}"
        )

    if (
        user_need.budget
        and user_need.budget.max
        and user_need.budget.max > 0
    ):
        lines.append(
            f"預算：約 "
            f"{user_need.budget.max} 元"
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

    for idx, product in enumerate(
        products,
        start=1,
    ):

        tags = product.get(
            "tags",
            [],
        )

        if isinstance(tags, list):

            tag_text = "、".join(
                str(tag)
                for tag in tags
                if tag
            )

        else:

            tag_text = str(tags)

        result.append(
            f"""
【第 {idx} 名】

商品名稱：{product.get("name", "")}
品牌：{product.get("brand", "")}
價格：{product.get("price", "")} 元
推薦度：{product.get("match", 0)}%
推薦原因：{product.get("reason", "")}
已知標籤：{tag_text}
""".strip()
        )

    return (
        "\n\n"
        "-----------------------------"
        "\n\n"
    ).join(result)


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

你的任務是：
根據「使用者需求」以及「系統提供的商品資料」，
將推薦結果改寫成自然、簡短、容易閱讀的繁體中文介紹。

你不是商品搜尋引擎。
你不是商品資料庫。
你不能自行查詢或補充商品資訊。

{persona_text}

{user_need_text}

【系統提供的商品資料】

{product_text}


【最高優先級規則】

只能使用上方「系統提供的商品資料」。

系統沒有提供的商品資訊，一律視為不存在。

如果你不知道某項商品資訊，
就不要提及該資訊。


【允許使用的資訊】

你只能使用：

1. 商品名稱
2. 品牌
3. 價格
4. 推薦度
5. 推薦原因
6. 已知標籤
7. 使用者需求
8. 使用者背景

你可以重新組合以上資訊，
但不能增加新的商品事實。


【絕對禁止】

禁止：

1. 自行新增商品功能。
2. 自行新增商品規格。
3. 自行新增續航時間。
4. 自行新增感測器。
5. 自行新增 GPS、血氧、心率、ECG 等功能。
6. 自行新增防水能力。
7. 自行新增材質。
8. 自行新增尺寸。
9. 自行新增通訊功能。
10. 自行新增健康功能。
11. 自行新增運動功能。
12. 自行新增價格以外的數字。
13. 根據品牌推測商品功能。
14. 根據型號推測商品功能。
15. 根據你對產品的既有知識補充資訊。
16. 使用系統沒有提供的規格進行比較。
17. 宣稱「一定適合」、「最佳」、「最強」等系統沒有提供的結論。


【非常重要】

即使你知道某個品牌或型號通常具有某項功能，
也禁止使用該知識。

例如：

如果系統只提供：

商品名稱：Apple Watch Series 11
品牌：Apple
價格：13488 元
推薦原因：高評價商品、熱門品牌商品

你只能根據這些資訊介紹。

你不能因為知道 Apple Watch
就自行加入 GPS、心率、血氧、續航、
防水、運動模式或其他功能。


【推薦順位】

必須完全按照系統提供的順位介紹。

第 1 名 → 第一個介紹
第 2 名 → 第二個介紹
第 3 名 → 第三個介紹

不得重新排序。


【內容要求】

第 1 名：
2 句左右。
可以稍微完整。

第 2 名：
1～2 句。

第 3 名：
1 句。

如果商品少於 3 項，
只介紹實際提供的商品。


【推薦原因】

推薦原因是系統已經計算完成的結果。

你可以把推薦原因改寫成自然語句。

例如：

「高評價商品、熱門品牌商品」

可以改寫成：

「這款商品評價表現不錯，也是目前推薦結果中的熱門品牌選擇。」

但不能改寫成不存在的功能或規格。


【語氣】

使用自然、簡潔的繁體中文。

像台灣門市導購在介紹商品。

不要像商品規格表。

不要過度行銷。

不要誇大。

不要編造。


【格式】

不要 Markdown。

不要項目符號。

不要開場白。

不要結論。

不要額外解釋。

直接輸出：

【第1名】
商品名稱
介紹內容

【第2名】
商品名稱
介紹內容

【第3名】
商品名稱
介紹內容


【輸出前自我檢查】

在輸出之前，逐項檢查：

1. 每個商品名稱是否與系統提供的完全一致？
2. 是否按照推薦順位？
3. 是否只介紹系統提供的商品？
4. 是否加入任何系統沒有提供的功能？
5. 是否加入任何系統沒有提供的規格？
6. 是否根據品牌或型號自行推測？
7. 是否加入系統沒有提供的數字？
8. 是否加入系統沒有提供的比較？
9. 如果刪除所有你自己的產品知識，
   內容是否仍然可以完全由系統提供資料支持？

如果任何一句無法由系統提供的資料直接支持，
刪除該句。

現在開始撰寫推薦內容。
"""


# ==================================================
# Summary Generator
# ==================================================

def generate_summary(
    products,
    user_need,
    budget_fallback=False,
):

    print(
        "[Summary Service]"
    )

    if not products:

        return (
            "目前沒有找到符合條件的推薦商品。"
        )

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
        product_text,
    )

    # =========================
    # Debug
    # =========================

    if DEBUG_SUMMARY:

        print(
            "\n========== Summary Context =========="
        )

        print(persona_text)

        print(user_need_text)

        print(product_text)

        print(
            "=====================================\n"
        )

    # =========================
    # Budget Notice
    # =========================

    budget_notice = ""

    if (
        budget_fallback
        and user_need.budget
        and user_need.budget.max
    ):

        budget_notice = (
            f"未找到符合 "
            f"{user_need.budget.min} ~ "
            f"{user_need.budget.max} 元預算的商品，"
            f"以下推薦價格最接近需求的商品。\n\n"
        )

    # =========================
    # AI Summary
    # =========================

    try:

        print(
            "[Summary Start]"
        )

        start = time.time()

        ai_reply = ask_ai(
            summary_prompt,
            model_name=SUMMARY_MODEL,
        )

        elapsed = (
            time.time() - start
        )

        print(
            f"[Summary Time] "
            f"{elapsed:.2f}s"
        )

        # =========================
        # Budget Notice
        # =========================

        if budget_notice:

            ai_reply = (
                budget_notice
                + ai_reply
            )

        # =========================
        # Empty Response
        # =========================

        if (
            not ai_reply
            or not ai_reply.strip()
        ):

            ai_reply = (
                "已為您整理符合需求的商品，"
                "請參考以下推薦。"
            )

        # =========================
        # Debug Output
        # =========================

        if DEBUG_SUMMARY:

            print(
                "\n========== Summary =========="
            )

            print(
                ai_reply
            )

            print(
                "=============================\n"
            )

        print(
            "[Summary End]"
        )

        return ai_reply

    except Exception as e:

        print(
            f"[Summary Error] {e}"
        )

        return (
            "目前 AI 暫時無法產生推薦摘要，"
            "但已為您整理符合需求的商品。"
        )