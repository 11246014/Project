# services/summary_service.py

from config.settings import SUMMARY_MODEL
from services.ai_service import ask_ai


DEBUG_SUMMARY = True


# ==================================================
# Persona Context
# ==================================================

def _build_persona_text(persona):
    """
    建立使用者背景文字。

    只使用已存在的 Persona 欄位。
    不自行推測其他資訊。
    """

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
    """
    建立使用者需求文字。
    """

    if not user_need:
        return ""

    lines = []

    # 裝置
    if getattr(user_need, "device_type", None):
        lines.append(
            f"裝置：{user_need.device_type}"
        )

    # 用途
    usage = getattr(
        user_need,
        "usage",
        None,
    )

    if usage:
        usage_text = "、".join(
            str(item)
            for item in usage
            if item
        )

        if usage_text:
            lines.append(
                f"用途：{usage_text}"
            )

    # 功能需求
    features = getattr(
        user_need,
        "features",
        None,
    )

    if features:
        feature_text = "、".join(
            str(item)
            for item in features
            if item
        )

        if feature_text:
            lines.append(
                f"需求功能：{feature_text}"
            )

    # Preferences
    preferences = getattr(
        user_need,
        "preferences",
        None,
    )

    if preferences:

        # 手機系統
        if getattr(
            preferences,
            "os",
            None,
        ):
            lines.append(
                f"手機系統：{preferences.os}"
            )

        # 品牌偏好
        if getattr(
            preferences,
            "brand",
            None,
        ):
            lines.append(
                f"偏好品牌：{preferences.brand}"
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
    """
    建立提供給 AI Summary 的商品資料。

    商品名稱：
        優先使用 name
        沒有 name 才使用 title

    不修改商品原始名稱。
    """

    print(
        "\n========== SUMMARY PRODUCT RAW =========="
    )

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

    print(
        "=========================================\n"
    )

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
你是 WearWise 的推薦助手。

系統已經完成商品搜尋、篩選與排序。
你的工作不是重新推薦商品，也不是重新評分，
而是把系統提供的推薦結果，整理成自然、簡潔、
像真人購物聊天一樣的繁體中文推薦說明。

【使用者需求】
{user_need_text}

【使用者背景】
{persona_text}

【推薦商品】
{product_text}

【重要規則】

一、資料限制
1. 只能使用本次提供的使用者需求、使用者背景與商品資料。
2. 不可自行搜尋、補充或推測商品的功能、規格、性能、品質、優缺點或品牌評價。
3. 不要因為知道品牌或型號，就自行推測它具有某項功能。
4. 使用者需求只能用來說明推薦方向，不能直接當成商品具有的功能。
5. 使用者背景只有在與商品資料存在直接關聯時才能提及，沒有關聯就不要使用。
6. 如果某項資訊沒有出現在商品資料中，就不要自行補充。

二、推薦內容
1. 優先使用商品的「推薦原因」、「已知標籤」以及價格來說明推薦理由。
2. 每個商品只挑 1～2 個最有用的資訊，不需要把所有欄位全部念出來。
3. 可以自然連結使用者需求與商品資料，但必須確實有資料支持。
4. 如果資料不足以支持某個特色，就不要硬寫。
5. 如果推薦原因本身很普通，就簡單自然地表達，不要為了增加內容而硬湊理由。
6. 價格可以和使用者預算直接比較，例如「價格落在你的預算範圍內」。
7. 不要自行把價格轉換成「很划算」、「CP 值高」、「值得購買」等主觀評價。
8. 已知標籤可以自然寫進句子，但不能從標籤延伸出資料中沒有的功能或效果。
9. 推薦度只是系統排序依據，不要把推薦度解讀成品質、性能、CP 值或「最值得購買」。

三、商品自述規則
1. 每個商品的推薦說明都要有一點「在介紹這個商品」的感覺，
   不要只是把推薦原因、價格和標籤逐項列出。
2. 可以使用較自然的說法，例如：
   「如果你在意……，這款目前的推薦原因是……」
   「這款比較明顯的特色是……」
   「從目前提供的資訊來看，這款主要是因為……」
   「如果你剛好重視……，這款可以留意……」
   但不要每個商品都使用相同句型。
3. 可以適度補充商品名稱中已經明確出現的資訊，
   但不能從商品名稱自行推測沒有明確寫出的功能。
4. 推薦說明應該像購物助手在幫使用者快速理解「為什麼它會出現在這裡」，
   而不是像資料庫欄位摘要。
5. 不需要刻意使用「推薦」、「符合」、「適合」等固定詞彙，
   可以依照商品資料自然改變表達方式。
6. 第 1 名可以稍微完整一點，讓使用者比較容易理解它被排在前面的原因。
7. 第 2、3 名可以簡潔一些，但仍要有完整的推薦說明。
8. 如果商品資料只有價格或單一推薦原因，就維持簡單，
   不要為了讓內容變長而自行創造新的理由。
9. 不要使用過度宣傳或廣告式語氣，例如：
   「超級推薦」、「絕對值得」、「必買」、「頂級」、「完美選擇」。
10. 不要使用「根據系統資料」、「系統推薦原因」、「系統提供」、
    「已知標籤」、「資料顯示」等後台用語。

四、避免制式感
1. 不要讓每個商品都使用完全相同的句型。
2. 不要每個商品都固定按照「品牌 → 價格 → 推薦原因 → 標籤」介紹。
3. 可以改變句子順序、開頭和長度，但不能因此加入不存在的資訊。
4. 有些商品可以先講特色，再補價格；
   有些商品可以先講價格，再說推薦原因。
5. 不需要每個商品都同時提到價格。
   只有價格對理解推薦結果有幫助時才提及。
6. 不要每個商品都使用「這款商品」開頭。
7. 避免連續使用相同的語句，例如：
   「這款……」、「這款……」、「這款……」。
8. 整體語氣要自然、直接、簡潔，像購物推薦助手，
   而不是報告、表格或 AI 生成的制式摘要。

五、商品順序
1. 商品順位已經由系統決定。
2. 必須完全按照提供的順序輸出，不可重新排序。
3. 商品名稱必須完整保留，不可縮寫、修改、刪除版本資訊或自行修正型號。
4. 系統提供幾個商品，就輸出幾個商品，不可自行合併或刪除。
5. 不可以因為自己認為某個商品比較好，就調整商品順序。

六、輸出長度
1. 每個商品的推薦說明控制在約 45～90 個中文字左右。
2. 第 1 名可以稍微詳細，通常約 60～90 字，可使用 2 句。
3. 第 2、3 名可以稍微精簡，通常約 45～75 字，可使用 1～2 句。
4. 不需要刻意填滿字數；如果資料較少，可以自然縮短。
5. 但不要只輸出一句非常短的「提供心率監測，價格 999 元」這類資料拼接句。
6. 優先增加「為什麼這項資訊對使用者有參考價值」的自然銜接，
   而不是增加新的商品資訊。
7. 不要重複相同資訊或同一個理由。
8. 整體不要寫成長篇商品介紹。

【輸出格式】

只輸出推薦結果，不要開場白、結尾總結或額外解釋。

【第1名】
完整商品名稱
推薦說明

【第2名】
完整商品名稱
推薦說明

【第3名】
完整商品名稱
推薦說明

實際商品數量：
{product_count}

依實際商品數量輸出，不要輸出不存在的名次。

輸出前確認：
- 順序沒有改變
- 商品名稱沒有修改
- 沒有加入商品資料以外的資訊
- 沒有把使用者需求直接當成商品功能
- 沒有自行推測商品優缺點
- 沒有把價格轉成 CP 值或品質評價
- 沒有把推薦度當成商品品質
- 每個商品只有最重要的 1～2 個資訊
- 每個商品有自然的推薦說明，而不是單純列資料
- 第 1 名可以比其他商品稍微詳細
- 每個推薦說明約 45～90 個中文字
- 沒有為了湊字數而加入不存在的資訊
- 沒有連續使用完全相同的句型
- 整體讀起來自然，不像制式資料表

現在開始。
"""

# ==================================================
# Fallback Summary
# ==================================================

def _build_fallback_summary(
    products,
    user_need=None,
):
    """
    AI 無回應時的本地 fallback。

    不依賴 Summary Validator。
    """

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

        content_parts = []

        # --------------------------------------------------
        # 用途 + 推薦原因
        # --------------------------------------------------

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

        # --------------------------------------------------
        # 預算 + 價格
        # --------------------------------------------------

        if (
            budget_max
            and price
        ):

            try:

                price_number = float(
                    str(price).replace(
                        ",",
                        "",
                    )
                )

                if price_number <= budget_max:

                    content_parts.append(
                        f"價格為 {price} 元，"
                        f"在你 {budget_max} 元的預算內。"
                    )

            except (
                ValueError,
                TypeError,
            ):
                pass

        # --------------------------------------------------
        # Tags
        # --------------------------------------------------

        if (
            tag_text
            and len(content_parts) < 2
        ):

            content_parts.append(
                f"這款也有 {tag_text} 相關資訊。"
            )

        content = " ".join(
            content_parts
        ).strip()

        # --------------------------------------------------
        # 最後保底
        # --------------------------------------------------

        if not content:

            if reason:

                content = (
                    f"這款會出現在推薦結果中，"
                    f"主要是因為{reason}。"
                )

            else:

                content = (
                    "這款商品是本次推薦結果中的選項。"
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
    """
    產生最終推薦 Summary。

    流程：

    Products
        ↓
    Build Persona Context
        ↓
    Build User Need Context
        ↓
    Build Product Context
        ↓
    Gemini / AI Summary
        ↓
    Empty Response Check
        ↓
    Fallback
        ↓
    Final Summary
    """

    print(
        "[Summary Service]"
    )

    # ==================================================
    # 沒有商品
    # ==================================================

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

    budget = getattr(
        user_need,
        "budget",
        None,
    )

    if (
        budget_fallback
        and budget
    ):

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

    try:

        summary = ask_ai(
            summary_prompt,
            model_name=SUMMARY_MODEL,
        )

    except Exception as e:

        print(
            f"[Summary AI Error] {e}"
        )

        summary = ""

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