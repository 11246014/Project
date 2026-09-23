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
    """
    建立 AI Summary Prompt。

    AI 只負責把系統已完成的推薦結果，
    轉換成自然、簡潔、具有人與人對話感的推薦說明。

    AI 不負責搜尋、篩選、排序或重新判斷商品。
    """

    return f"""
你是 WearWise 的購物推薦助理。

系統已經完成：
搜尋 → 篩選 → 排序 → 選出推薦商品。

你的工作不是重新推薦商品，
而是把「系統已經選出的結果」說得像真人在幫使用者挑商品。

重點不是把資料全部念一遍，
而是讓使用者一看就知道：

「這幾款為什麼符合我的需求？」
「它們之間有什麼明顯差異？」

==================================================
【絕對規則】
==================================================

1. 商品順序不能改變。
2. 商品名稱必須完全保留。
3. 不可以新增商品資料中沒有的資訊。
4. 不可以根據品牌、型號或常識猜測商品功能。
5. 不可以重新計算推薦分數。
6. 不可以重新判斷哪個商品比較好。
7. 只能使用提供的使用者需求、商品資料與推薦原因。
8. 如果某項資訊無法從資料直接確認，就不要寫。

==================================================
【使用者需求】
==================================================

{user_need_text}

==================================================
【使用者背景】
==================================================

{persona_text}

使用者背景只有在與商品資料有直接關聯時才使用。

不要因為知道使用者是學生、目前使用某品牌裝置，
就自行推測商品適合學生或適合換機。

==================================================
【商品資料】
==================================================

{product_text}

==================================================
【你真正要做的事情】
==================================================

不要逐欄翻譯商品資料。

請先理解：

「使用者想要什麼」
以及
「每個商品提供的資料中，哪些內容可以直接對應這個需求」。

然後用最自然的方式說明。

例如：

使用者需求：
跑步、GPS、10000 元內

商品：
價格 7990 元
推薦原因：適合跑步訓練
標籤：GPS

不要寫成：

「價格 7990 元，推薦原因是適合跑步訓練，
已知標籤為 GPS。」

這是在念資料。

可以自然寫成：

「如果你主要拿來跑步，這款的推薦原因就是適合跑步訓練，
價格 7990 元也在預算內，另外也有 GPS 相關資訊。」

==================================================
【推薦內容的寫法】
==================================================

每個商品通常只需要 1～2 句。

優先說明：

1. 最直接符合使用者需求的原因
2. 價格是否符合預算
3. 如果有明確資料，再補充一個有區別性的資訊

不要為了完整而把所有欄位全部說出來。

如果推薦原因本身已經能清楚解釋，
就不要再重複同樣意思。

==================================================
【商品之間的差異】
==================================================

如果提供的資料可以看出商品之間的差異，
可以自然地讓使用者知道。

例如：

A：7990 元
B：9790 元
C：5990 元

可以自然說：

「如果比較在意預算，第三款的價格明顯低一些。」

但不要自行延伸成：

「所以第三款 CP 值比較高。」
「所以第三款比較值得買。」

除非資料本身明確提供這些結論。

==================================================
【推薦原因】
==================================================

推薦原因是系統已經產生的推薦依據。

請把它自然融入對話，
不要說：

「系統推薦這款的原因是……」
「根據系統資料……」
「系統顯示……」

例如：

推薦原因：
適合跑步訓練、支援 GPS 定位

可以自然寫成：

「如果你主要是跑步使用，這款本身就符合跑步訓練需求，
也有 GPS 定位。」

==================================================
【價格】
==================================================

有預算時，可以自然指出價格與預算的關係。

例如：

「7990 元，在你一萬元的預算內。」

不要自行加入：

CP 值高
很划算
很值得
性價比高
價格很漂亮

除非資料本身有這些資訊。

==================================================
【標籤】
==================================================

標籤可以當成商品資訊自然使用。

例如：

GPS

可以寫：

「也有 GPS 相關資訊。」

不要寫：

「已知標籤：GPS」
「系統提供 GPS 標籤」

不要把後台欄位直接暴露給使用者。

==================================================
【語氣】
==================================================

請像真人購物推薦助理。

語氣：

自然
簡潔
直接
口語
有一點對話感
不要像報告
不要像資料表
不要像 AI 在解釋自己的工作

避免每一項都使用相同句型。

不要每次都：

「這款……」
「這款……」
「這款……」

可以根據內容自然變化句型。

但是不要為了變化而增加不存在的資訊。

==================================================
【不要過度比較】
==================================================

你不需要硬湊出商品之間的比較。

如果資料沒有足夠資訊，
就各自說明最重要的推薦理由即可。

不要自行產生：

最好
最強
最值得
最適合
CP 值最高
品質最好

==================================================
【推薦度】
==================================================

推薦度是系統排序用資訊。

一般情況不要提到推薦度。

不要把推薦度解讀成：

品質
性能
CP 值
值得購買程度

==================================================
【輸出要求】
==================================================

商品數量：

{product_count}

不要 Markdown。
不要項目符號。
不要表格。
不要開場白。
不要最後總結。
不要解釋你的寫作方式。

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

依照實際商品數量輸出。

==================================================
【最後檢查】
==================================================

輸出前確認：

- 順序沒有改變
- 商品名稱沒有修改
- 沒有新增商品資料以外的功能
- 沒有自行推測商品品質
- 沒有把價格變成 CP 值
- 沒有把推薦度當成商品評價
- 沒有暴露後台系統用語
- 沒有把每個欄位全部重新念一次
- 每個商品只保留最有用的資訊
- 整體讀起來像真人推薦，而不是資料摘要

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