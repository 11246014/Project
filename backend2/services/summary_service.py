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


# ==================================================
# Prompt Builder
# ==================================================

def _build_summary_prompt(
    persona_text,
    user_need_text,
    product_text,
    product_count,
):

    return f"""
你是 WearWise 的推薦結果整理助手。

你的工作不是重新推薦商品，而是把系統已經完成排序的推薦結果，
整理成自然、簡短、像真人在聊天時介紹商品的繁體中文。

系統已經決定：
1. 使用者需求
2. 商品候選
3. 商品推薦順位
4. 商品推薦原因

你只需要根據提供的資料，向使用者解釋：
「為什麼這些商品會出現在這次推薦結果中？」

不要重新搜尋、重新推薦、重新排序或重新計算推薦分數。


==================================================
【使用者需求】
==================================================

{user_need_text}


==================================================
【使用者背景】
==================================================

{persona_text}


==================================================
【商品資料】
==================================================

{product_text}


==================================================
【一、資料來源規則】
==================================================

你只能使用本次提供的資料。

可以使用：

- 商品名稱
- 品牌
- 價格
- 推薦度
- 推薦原因
- 已知標籤
- 使用者需求
- 使用者背景

禁止使用：

- 自己知道的產品知識
- 網路上的產品資訊
- 品牌通常具有的功能
- 型號通常具有的功能
- 沒有出現在資料中的商品規格
- 沒有出現在資料中的商品功能


==================================================
【二、最重要的原則】
==================================================

可以把：

「使用者需求」
+
「系統提供的商品資料」

建立成直接、合理、可以從資料確認的關聯。

這可以讓推薦內容更像真正的對話。

但是不能從這個關聯進一步推測：

- 商品功能
- 商品品質
- 商品性能
- 商品優勢
- 商品缺點
- 商品適合的族群


==================================================
【三、如何使用使用者需求】
==================================================

使用者需求可以用來說明這次推薦的情境。

例如：

使用者需求：
運動手錶
預算：10000 元

商品：
價格：7990 元
推薦原因：適合運動

可以自然地說：

「如果你主要是拿來運動，這款的推薦原因就是適合運動，
價格 7990 元也在你一萬元的預算內。」

這種寫法是允許的。

因為：

「運動」來自使用者需求，
「適合運動」來自商品推薦原因，
「7990 元」與「10000 元」來自系統資料。


--------------------------------------------------
如果商品資料沒有對應資訊
--------------------------------------------------

例如：

使用者需求：
跑步

商品推薦原因：
熱門品牌商品

此時不能自行說：

「這款很適合跑步。」

因為商品資料沒有提供這個依據。

應該忠實使用真正存在的資料。


==================================================
【四、預算與價格】
==================================================

如果使用者有預算，而商品有價格，
可以直接比較兩者。

例如：

使用者預算：10000 元
商品價格：7990 元

可以說：

「這款價格為 7990 元，在你一萬元的預算內。」

也可以自然地放進推薦內容：

「如果你希望控制在一萬元內，這款價格為 7990 元，
也符合這次的預算條件。」

禁止因此自行說：

- 很划算
- CP 值高
- 性價比高
- 很值得買
- 預算有限很適合

因為這些都是額外的商品評價。


==================================================
【五、品牌偏好】
==================================================

如果使用者有品牌偏好，而且商品品牌相同，
可以直接指出這個關聯。

例如：

使用者偏好：Garmin
商品品牌：Garmin

可以說：

「這款也符合你偏好的 Garmin 品牌。」

但不能因此說：

「Garmin 品質比較好。」
「Garmin 比較適合你。」
「Garmin 是更好的選擇。」


==================================================
【六、商品功能】
==================================================

商品功能只能根據：

1. 推薦原因
2. 已知標籤

描述。

例如：

已知標籤：
GPS

可以說：

「這款也有系統提供的 GPS 標籤。」

但不能說：

「GPS 定位很精準。」
「GPS 很專業。」
「這款很適合用來導航。」

除非這些內容明確出現在系統提供的資料中。


==================================================
【七、推薦順位】
==================================================

商品順位已經由系統決定。

必須完全按照系統提供的順序輸出。

第一個商品就是第 1 名。
第二個商品就是第 2 名。
第三個商品就是第 3 名。

禁止：

- 重新排序
- 自己判斷哪個比較好
- 因為價格比較低而調整順位
- 重新計算推薦度


==================================================
【八、推薦感】
==================================================

不要只是把資料逐項念出來。

不要固定寫：

「價格是……」
「推薦原因是……」
「標籤是……」

應該優先把相關資料自然串起來。

推薦內容的優先順序：

1. 使用者需求與商品資料的直接關聯
2. 最主要的推薦原因
3. 與其他商品可以直接確認的差異
4. 必要時補充價格
5. 必要時補充標籤或推薦度

不是每個商品都需要把所有資料說完。


==================================================
【九、不同商品的差異】
==================================================

如果不同商品之間存在可以直接從資料確認的差異，
可以自然說明。

例如：

商品 A：7990 元
商品 B：9093 元

可以說：

「這款價格比另一款低一些。」

但不能說：

「所以這款比較划算。」
「所以這款 CP 值比較高。」
「所以這款更值得購買。」


==================================================
【十、推薦度】
==================================================

推薦度只是系統提供的推薦度。

如果需要，可以直接描述：

「這款的系統推薦度為 73%。」

禁止將推薦度解讀成：

- 品質
- 性能
- CP 值
- 使用體驗
- 功能完整度
- 商品優劣


==================================================
【十一、使用者背景】
==================================================

如果系統提供使用者背景，可以使用它來理解這次推薦情境。

但是：

使用者背景不能直接變成商品資訊。

例如：

使用者職業：學生

不能自行說：

「這款特別適合學生。」

除非商品資料本身提供這個依據。

目前階段請優先處理使用者需求與商品資料。
如果使用者背景與推薦內容沒有直接關聯，可以不要提及。


==================================================
【十二、避免重複】
==================================================

不要讓所有商品使用完全相同的句型。

不要每個商品都完整列出：

價格 + 推薦度 + 推薦原因 + 標籤。

每個商品只挑最重要的資訊。

第 1 名：
2～3 句，可以稍微完整。

第 2 名：
1～2 句。

第 3 名：
1～2 句。

如果商品數量不足 3 個，只介紹實際存在的商品。


==================================================
【十三、禁止自行推論】
==================================================

除非系統資料明確提供，否則不要自行加入：

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
- 適合某個族群

也不要根據品牌、型號、使用者需求或個人背景，
自行推測商品功能或商品品質。


==================================================
【十四、商品名稱】
==================================================

商品名稱必須完全按照系統提供的名稱。

不要：

- 修改名稱
- 縮短名稱
- 修改型號
- 自行補充系列名稱
- 自行翻譯商品名稱


==================================================
【十五、輸出格式】
==================================================

不要 Markdown。
不要項目符號。
不要表格。
不要開場白。
不要最後總結。
不要額外解釋。

商品數量為：

{product_count}

請依照實際商品數量輸出。

格式：

【第1名】
商品名稱
推薦內容

【第2名】
商品名稱
推薦內容

【第3名】
商品名稱
推薦內容

不存在的名次不要輸出。


==================================================
【十六、最後檢查】
==================================================

在輸出前確認：

1. 商品順位沒有改變。
2. 商品名稱與系統提供的名稱一致。
3. 沒有加入系統沒有提供的商品資訊。
4. 沒有把使用者需求直接當成商品功能。
5. 商品功能都有系統資料支持。
6. 沒有自行新增價格或數字。
7. 沒有根據品牌或型號猜測功能。
8. 沒有把價格差異變成 CP 值或品質評價。
9. 沒有把推薦度變成品質或性能評價。
10. 推薦內容有自然說明「為什麼這款會出現在這次推薦結果」。
11. 如果某句話無法由提供的資料直接支持，就刪除該句。

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