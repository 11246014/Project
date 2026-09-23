# summary_service.py

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

    # 年齡層
    if getattr(persona, "age_range", None):
        parts.append(
            f"年齡層：{persona.age_range}"
        )

    # 職業
    if getattr(persona, "occupation", None):
        parts.append(
            f"職業：{persona.occupation}"
        )

    # 使用範圍
    if getattr(persona, "usage_scope", None):

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

    # 目前裝置
    if getattr(persona, "current_device", None):
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

    # 裝置
    if getattr(user_need, "device_type", None):
        lines.append(
            f"裝置：{user_need.device_type}"
        )

    # 用途
    if getattr(user_need, "usage", None):
        if user_need.usage:
            lines.append(
                "用途："
                + "、".join(
                    str(item)
                    for item in user_need.usage
                    if item
                )
            )

    # 功能需求
    if getattr(user_need, "features", None):
        if user_need.features:
            lines.append(
                "需求功能："
                + "、".join(
                    str(item)
                    for item in user_need.features
                    if item
                )
            )

    # Preferences
    preferences = getattr(
        user_need,
        "preferences",
        None,
    )

    if preferences:

        # 手機系統
        if getattr(preferences, "os", None):
            lines.append(
                f"手機系統："
                f"{preferences.os}"
            )

        # 品牌偏好
        if getattr(preferences, "brand", None):
            lines.append(
                f"偏好品牌："
                f"{preferences.brand}"
            )

    # 預算
    budget = getattr(
        user_need,
        "budget",
        None,
    )

    if budget:

        budget_max = getattr(
            budget,
            "max",
            None,
        )

        if (
            budget_max
            and budget_max > 0
            and budget_max < 999999
        ):
            lines.append(
                f"預算：約 {budget_max} 元"
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

    print("\n========== SUMMARY PRODUCT RAW ==========")

    for idx, product in enumerate(
        products,
        start=1,
    ):
        print(
            f"[{idx}] "
            f"name={product.get('name', '')} | "
            f"title={product.get('title', '')} | "
            f"brand={product.get('brand', '')} | "
            f"price={product.get('price', '')} | "
            f"match={product.get('match', '')}"
        )

    print("=========================================\n")

    result = []

    for idx, product in enumerate(
        products,
        start=1,
    ):

        # --------------------------------------------------
        # Product Name
        # --------------------------------------------------

        product_name = (
            product.get("name")
            or product.get("title")
            or ""
        )

        # --------------------------------------------------
        # Brand
        # --------------------------------------------------

        brand = (
            product.get("brand")
            or ""
        )

        # --------------------------------------------------
        # Price
        # --------------------------------------------------

        price = (
            product.get("price")
            or ""
        )

        # --------------------------------------------------
        # Match
        # --------------------------------------------------

        match = product.get(
            "match",
            0,
        )

        # --------------------------------------------------
        # Reason
        # --------------------------------------------------

        reason = (
            product.get("reason")
            or ""
        )

        # --------------------------------------------------
        # Tags
        # --------------------------------------------------

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

        # --------------------------------------------------
        # Context
        # --------------------------------------------------

        result.append(
            f"""
【第 {idx} 名】

商品名稱：{product_name}
品牌：{brand}
價格：{price} 元
推薦度：{match}%
推薦原因：{reason}
已知標籤：{tag_text}
""".strip()
        )

    return (
        "\n\n"
        "-----------------------------"
        "\n\n"
    ).join(result)


def _build_summary_prompt(
    persona_text,
    user_need_text,
    product_text,
    product_count,
):

    return f"""
你是 WearWise 的推薦結果整理助手。

系統已經完成商品搜尋、篩選與排序。
你的工作不是重新推薦商品，而是把系統已經選出的商品，
整理成自然、簡短、像真人聊天一樣的繁體中文推薦說明。

==================================================
【重要原則】
==================================================

1. 不要重新搜尋商品。
2. 不要重新排序商品。
3. 不要重新計算推薦分數。
4. 不要自行增加商品資訊。
5. 不要根據自己的知識補充商品功能、性能、品質或優缺點。
6. 商品順位完全按照提供的順序。
7. 商品名稱必須完全保留。
8. 只使用本次提供的資料。

你的目標不是「把所有資料都說完」，
而是讓使用者自然理解：

「為什麼這幾款會被推薦給我？」

==================================================
【使用者需求】
==================================================

{user_need_text}

==================================================
【使用者背景】
==================================================

{persona_text}

使用者背景只在與商品資料存在直接、明確的關聯時使用。

如果使用者背景與目前推薦商品沒有直接關聯，
就不要提及。

例如：

使用者職業：學生

不能自行說：
「這款很適合學生。」

目前使用者裝置：Apple Watch

也不能自行說：
「這款很適合從 Apple Watch 換過來。」

除非商品資料本身明確提供這些依據。

==================================================
【商品資料】
==================================================

{product_text}

==================================================
【資料使用規則】
==================================================

只能使用以下資料：

- 使用者需求
- 使用者背景
- 商品名稱
- 商品品牌
- 商品價格
- 商品推薦原因
- 商品已知標籤
- 商品推薦度

禁止加入資料中沒有出現的：

- 商品功能
- 商品規格
- 商品性能
- 商品品質
- 商品優缺點
- 適合族群
- 品牌評價
- 型號評價
- 價格以外的數字
- 網路上的產品知識

不要因為知道某個品牌或型號，
就自行推測它具有什麼功能。

==================================================
【自然連結使用者需求】
==================================================

可以把使用者需求與商品資料中明確存在的資訊自然連結。

例如：

使用者需求：
跑步
預算：10000 元

商品：
價格：9990 元
推薦原因：適合跑步訓練

可以寫：

「如果你主要是拿來跑步，這款的推薦原因就是適合跑步訓練，
價格 9990 元也符合你一萬元的預算。」

這是允許的，因為所有資訊都來自提供的資料。

但是不能自行延伸成：

「這款很適合長跑。」
「這款適合專業跑者。」
「這款的 GPS 很精準。」

除非這些資訊明確存在於商品資料中。

==================================================
【品牌】
==================================================

如果使用者有品牌偏好，
而商品品牌與偏好一致，可以自然提及。

例如：

使用者偏好：Garmin
商品品牌：Garmin

可以說：

「這款也是你偏好的 Garmin。」

但不要反覆對每個商品都說一次品牌。

也不能說：

「Garmin 品質比較好。」
「Garmin 更適合你。」
「Garmin 是比較好的選擇。」

==================================================
【價格與預算】
==================================================

如果使用者有預算，而且商品有價格，
可以直接比較。

例如：

使用者預算：10000 元
商品價格：7990 元

可以說：

「價格 7990 元，也符合你一萬元的預算。」

禁止把價格直接轉換成：

- 很划算
- CP 值高
- 性價比高
- 很值得買
- 預算有限很適合
- 比較值得選

除非這些內容本身存在於商品資料中。

==================================================
【商品標籤與功能】
==================================================

商品標籤可以自然融入推薦內容。

例如：

已知標籤：
GPS、心率

可以說：

「這款也有 GPS 和心率相關資訊。」

不要說：

「這款有系統提供的 GPS 標籤。」
「系統提供了 GPS 標籤。」
「已知標籤包含 GPS。」

不要讓使用者感覺你正在解釋後台資料。

同樣地：

不能因為有 GPS 標籤，
就自行說：

「GPS 可以精準記錄跑步路線。」

除非資料中明確提供這項資訊。

==================================================
【推薦原因】
==================================================

商品的推薦原因是系統已經產生的推薦依據，
可以自然地融入句子。

例如：

推薦原因：
適合跑步訓練

可以寫：

「如果你主要拿來跑步，這款的推薦原因就是適合跑步訓練。」

不要寫成：

「系統推薦這款的原因是……」

不要一直使用：

「系統推薦原因」
「系統資料顯示」
「根據系統」
「系統提供」

這些是內部用語，不需要告訴使用者。

==================================================
【資訊取捨】
==================================================

不要為了完整而把所有欄位全部念一遍。

每個商品通常只需要挑選 1～2 個最能說明推薦原因的資訊。

優先考慮：

1. 與使用者用途直接相關的推薦原因
2. 與使用者預算直接相關的價格
3. 與使用者品牌偏好直接相關的品牌
4. 商品資料中明確存在的功能或標籤

如果其中一項已經足以說明，
就不要為了湊內容再加入其他資訊。

例如：

使用者：
Garmin、跑步、10000 元

商品：
Garmin
9990 元
推薦原因：適合跑步訓練
標籤：GPS、心率

不需要全部講完。

可以自然寫成：

「如果你主要是拿來跑步，這款的推薦原因就是適合跑步訓練，
價格 9990 元也符合你一萬元的預算。」

也可以根據其他商品的資料，
選擇不同的重點。

==================================================
【避免模板感】
==================================================

不要讓每個商品都使用完全相同的句型。

避免每個商品都按照：

品牌 → 價格 → 推薦原因 → 標籤

的固定順序介紹。

也避免每個商品都使用：

「這款是……」
「這款符合……」
「這款價格為……」
「這款的推薦原因是……」

可以自然改變：

- 開頭
- 句子順序
- 強調資訊
- 句子長度

但不能為了讓句子變化，
而加入資料中不存在的內容。

如果某個商品沒有很多可以自然補充的資訊，
就簡短介紹，不需要硬湊內容。

==================================================
【商品之間的差異】
==================================================

如果商品之間存在可以直接從資料確認的差異，
可以自然提及。

例如：

商品 A：7990 元
商品 B：9990 元

可以說：

「這款價格比另一款低一些。」

但不能因此說：

「所以這款比較划算。」
「所以這款 CP 值比較高。」
「所以這款更值得購買。」

==================================================
【推薦度】
==================================================

推薦度主要是系統內部排序資訊。

一般情況不要主動提及推薦度。

不要把推薦度解讀成：

- 商品品質
- 商品性能
- CP 值
- 值得購買程度
- 最佳選擇

只有使用者明確詢問推薦度時，
才可以描述提供的數值。

==================================================
【最重要的語氣】
==================================================

請像一個真正的購物推薦助理在聊天。

語氣：

- 自然
- 簡潔
- 直接
- 像真人
- 不要過度正式
- 不要像報告
- 不要像在解釋後台系統
- 不要重複相同句型

不要使用：

「根據系統資料」
「系統推薦原因」
「系統提供」
「已知標籤」
「推薦度為」
「資料顯示」

除非使用者明確詢問這些資訊。

==================================================
【禁止自行推論】
==================================================

除非商品資料明確提供，
不要使用以下評價：

- 高品質
- 性能強
- 功能完整
- 功能豐富
- 精準
- 專業
- 很划算
- CP 值高
- 性價比高
- 值得購買
- 最值得購買
- 最佳
- 最強
- 非常適合

也不要根據：

品牌
型號
使用者年齡
使用者職業
目前裝置
使用者用途

自行推測商品功能或商品品質。

==================================================
【商品順位】
==================================================

商品順位已經由系統決定。

第一個商品就是第 1 名。
第二個商品就是第 2 名。
第三個商品就是第 3 名。

必須完全按照提供的順序輸出。

禁止重新排序。

==================================================
【輸出格式】
==================================================

商品數量：

{product_count}

不要 Markdown。
不要項目符號。
不要表格。
不要開場白。
不要最後總結。
不要解釋你的寫作方式。
不要說明系統如何進行推薦。

只輸出推薦結果。

格式：

【第1名】
商品名稱
自然、簡短的推薦說明

【第2名】
商品名稱
自然、簡短的推薦說明

【第3名】
商品名稱
自然、簡短的推薦說明

依照實際商品數量輸出，不存在的名次不要輸出。

==================================================
【輸出前檢查】
==================================================

輸出前確認：

1. 商品順序沒有改變。
2. 商品名稱完全按照提供資料。
3. 沒有新增商品資料以外的功能或規格。
4. 沒有把使用者需求直接當成商品功能。
5. 沒有根據品牌或型號猜測功能。
6. 沒有把價格變成 CP 值或品質評價。
7. 沒有把推薦度解讀成商品優劣。
8. 沒有把使用者背景直接當成商品適合族群。
9. 沒有使用「系統推薦原因」「已知標籤」等後台用語。
10. 每個商品只保留最有用的資訊，不需要把所有欄位念完。
11. 如果某句話無法由提供的資料直接支持，就刪除該句。
12. 整體讀起來要像真人在幫使用者挑商品，而不是在朗讀資料。

現在開始撰寫推薦內容。
"""


# ==================================================
# Fallback Summary
# ==================================================

def _build_fallback_summary(
    products,
    user_need=None,
):

    lines = []

    # --------------------------------------------------
    # 取得預算
    # --------------------------------------------------

    budget_max = None

    if user_need:

        budget = getattr(
            user_need,
            "budget",
            None,
        )

        if budget:

            value = getattr(
                budget,
                "max",
                None,
            )

            if (
                value
                and value > 0
                and value < 999999
            ):
                budget_max = value

    # --------------------------------------------------
    # 取得用途
    # --------------------------------------------------

    usages = []

    if user_need:

        raw_usage = getattr(
            user_need,
            "usage",
            None,
        )

        if raw_usage:
            usages = [
                str(item)
                for item in raw_usage
                if item
            ]

    usage_text = "、".join(usages)

    # --------------------------------------------------
    # Build
    # --------------------------------------------------

    for idx, product in enumerate(
        products,
        start=1,
    ):

        name = (
            product.get("name")
            or product.get("title")
            or ""
        )

        price = (
            product.get("price")
            or ""
        )

        reason = (
            product.get("reason")
            or ""
        )

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

        # --------------------------------------------------
        # 建立較自然的 fallback
        # --------------------------------------------------

        content_parts = []

        # 用途 + 推薦原因直接關聯
        if usage_text and reason:

            reason_lower = reason.lower()

            usage_match = any(
                usage.lower() in reason_lower
                for usage in usages
            )

            if usage_match:

                content_parts.append(
                    f"如果你主要是拿來{usage_text}，"
                    f"這款的推薦原因就是{reason}。"
                )

            else:

                content_parts.append(
                    f"這款會出現在推薦結果中，"
                    f"主要是因為{reason}。"
                )

        elif reason:

            content_parts.append(
                f"這款會出現在推薦結果中，"
                f"主要是因為{reason}。"
            )

        # 預算 + 價格直接關聯
        if (
            budget_max
            and price
        ):

            try:

                price_number = float(
                    str(price).replace(",", "")
                )

                if price_number <= budget_max:

                    content_parts.append(
                        f"價格為 {price} 元，"
                        f"在你一萬元預算內。"
                        if budget_max == 10000
                        else
                        f"價格為 {price} 元，"
                        f"在你 {budget_max} 元的預算內。"
                    )

            except (
                ValueError,
                TypeError,
            ):
                pass

        # Tag
        if (
            tag_text
            and len(content_parts) < 2
        ):

            content_parts.append(
                f"系統也提供了 {tag_text} 標籤。"
            )

        content = " ".join(
            content_parts
        ).strip()

        # 最後保底
        if not content:

            content = (
                f"這款會出現在推薦結果中，"
                f"主要推薦原因為{reason}。"
            )

        lines.append(
            f"【第{idx}名】\n"
            f"{name}\n"
            f"{content}"
        )

    return "\n\n".join(lines)


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

    # --------------------------------------------------
    # 沒有商品
    # --------------------------------------------------

    if not products:

        return (
            "目前沒有找到符合條件的推薦商品。"
        )

    # ==================================================
    # Build Context
    # ==================================================

    persona_text = _build_persona_text(
        getattr(
            user_need,
            "persona",
            None,
        )
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
        len(products),
    )

    # ==================================================
    # Debug
    # ==================================================

    if DEBUG_SUMMARY:

        print(
            "\n========== Summary Context =========="
        )

        if persona_text:

            print(persona_text)

        if user_need_text:

            print(user_need_text)

        print(product_text)

        print(
            "=====================================\n"
        )

    # ==================================================
    # Budget Notice
    # ==================================================

    budget_notice = ""

    if (
        budget_fallback
        and getattr(
            user_need,
            "budget",
            None,
        )
    ):

        budget_max = getattr(
            user_need.budget,
            "max",
            None,
        )

        if (
            budget_max
            and budget_max > 0
            and budget_max < 999999
        ):

            budget_notice = (
                f"未找到符合 {budget_max} 元以下預算的商品，"
                f"以下推薦價格最接近需求的商品。\n\n"
            )

    # ==================================================
    # AI Summary
    # ==================================================

    print(
        "[Summary Mode] AI"
    )

    summary = ask_ai(
        summary_prompt,
        model_name=SUMMARY_MODEL,
    )

    # ==================================================
    # AI Empty
    # ==================================================

    if (
        not summary
        or not summary.strip()
    ):

        print(
            "[Summary AI] "
            "Empty response -> fallback"
        )

        summary = _build_fallback_summary(
            products,
            user_need,
        )

    # ==================================================
    # Budget Notice
    # ==================================================

    if budget_notice:

        summary = (
            budget_notice
            + summary
        )

    # ==================================================
    # Debug Output
    # ==================================================

    if DEBUG_SUMMARY:

        print(
            "\n========== Summary =========="
        )

        print(summary)

        print(
            "=============================\n"
        )

    print(
        "[Summary End]"
    )

    return summary