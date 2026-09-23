#summary_service.py
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
        and user_need.budget.max < 999999
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

        # ==================================================
        # Product Name
        #
        # Summary 優先使用 name。
        # 若 name 不存在，使用 title。
        # ==================================================

        product_name = (
            product.get("name")
            or product.get("title")
            or ""
        )

        # ==================================================
        # Brand
        # ==================================================

        brand = (
            product.get("brand")
            or ""
        )

        # ==================================================
        # Price
        # ==================================================

        price = (
            product.get("price")
            or ""
        )

        # ==================================================
        # Match
        # ==================================================

        match = product.get(
            "match",
            0,
        )

        # ==================================================
        # Reason
        # ==================================================

        reason = (
            product.get("reason")
            or ""
        )

        # ==================================================
        # Tags
        # ==================================================

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

        # ==================================================
        # Build Context
        # ==================================================

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
你是 WearWise AI 的推薦結果文字整理助手。

你的任務是：
根據「系統已經計算完成的商品推薦結果」，
將推薦結果整理成自然、簡短、容易理解，
並且具有推薦參考價值的繁體中文。

你的工作不是重新計算推薦結果，
而是幫助使用者理解：

1. 為什麼這些商品會被推薦
2. 每個商品主要符合使用者哪些需求
3. 不同商品之間有哪些系統資料已經提供的差異

你不需要重新計算推薦分數。
你不需要重新排序商品。
你不得改變系統提供的推薦順位。

你只能使用系統提供的資料。
你不是商品搜尋引擎。
你不是商品資料庫。
你不能自行查詢或補充商品資訊。

{persona_text}

{user_need_text}

【系統提供的商品資料】

{product_text}

【最高優先級規則】

只能使用「系統提供的商品資料」。

其中：

「推薦原因」與「已知標籤」
是判斷商品功能與推薦理由的主要依據。

如果「推薦原因」與「已知標籤」
沒有提到某項商品功能，
就禁止在介紹中提及該功能。

系統沒有提供的商品資訊，
一律視為不存在。

如果你不知道某項商品資訊，
就不要提及該資訊。

即使你認為某個品牌、型號或產品通常具有某項功能，
也禁止自行補充。

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
讓內容更自然、更容易理解，
但不能增加新的商品事實。

【使用者需求的使用限制】

使用者需求只能用來理解推薦情境。

使用者需求不能用來證明商品具有任何功能。

例如：

如果使用者需求是「運動」，
不能因此認定商品具有運動模式。

如果使用者需求是「跑步」，
不能因此認定商品具有跑步功能。

如果使用者需求是「需要 GPS」，
不能因此認定商品具有 GPS。

如果使用者需求是「需要防水」，
不能因此認定商品具有防水能力。

商品是否具有某項功能，
只能根據「推薦原因」與「已知標籤」判斷。

【推薦結果的解讀方式】

系統已經完成商品排序。

你的工作是「解釋推薦結果」，
不是重新做推薦。

必須完全按照系統提供的順位介紹：

第 1 名 → 第一個介紹
第 2 名 → 第二個介紹
第 3 名 → 第三個介紹

不得重新排序。

不得因為你自己的判斷，
認為其他商品比較好而改變順位。

不得重新計算推薦分數。

【推薦內容要求】

推薦內容必須有「推薦感」，
不能只是把商品名稱、標籤或推薦原因重新排列。

重點是讓使用者快速理解：

「為什麼這些商品會出現在推薦結果中？」

請依照推薦順位，
讓不同名次的介紹長度與資訊量自然遞減。

【第 1 名】

2～3 句。

第 1 名是主要推薦結果，
可以稍微完整一點。

優先說明：

- 這款商品主要符合哪些使用者需求
- 系統提供的主要推薦原因
- 如果系統資料有提供，可以自然帶入價格、推薦度、標籤或其他推薦依據

第 1 名可以比其他商品多一點資訊，
但不要為了增加長度而重複相同內容。

【第 2 名】

1～2 句。

比第 1 名簡短一些。

說明這款商品主要為什麼被推薦即可。

如果有與第 1 名不同的推薦原因、
價格、推薦度或標籤，
可以自然指出系統已經提供的差異。

不要刻意重複第 1 名已經說過的內容。

【第 3 名】

1 句。

簡單說明這款商品的主要推薦理由即可。

如果系統資料沒有足夠的額外資訊，
不要為了湊內容而重複前面商品的描述。

【避免重複】

不要讓每個商品都使用完全相同的句型。

例如不要連續出現：

「這款商品主要符合跑步訓練需求，並具有 GPS。」
「這款商品主要符合跑步訓練需求，並具有 GPS。」
「這款商品主要符合跑步訓練需求，並具有 GPS。」

如果多個商品具有相同的推薦原因，
可以自然簡化描述。

例如：

第 1 名：
「如果你主要是拿來跑步，這款的推薦原因就是適合跑步訓練，另外系統也標示了 GPS 和心率相關標籤。」

第 2 名：
「這款同樣以跑步訓練為主要推薦原因，並有 GPS 標籤。」

第 3 名：
「這款同樣符合跑步訓練需求，並標示 GPS。」

以上只是表達方式範例，
實際內容必須以系統提供的資料為準。

如果系統資料提供不同資訊，
應優先描述實際存在的差異。

【推薦感的定義】

「推薦感」不是自行評價商品，
也不是自行判斷哪個商品比較適合。

推薦感是：

讓使用者知道這款商品
「為什麼出現在這次推薦結果中」。

可以透過：

- 使用者需求
- 推薦原因
- 已知標籤
- 價格
- 推薦度

將系統已經提供的資訊自然串接起來。

不得因此新增：

- 商品優點
- 商品缺點
- 功能評價
- 品質評價
- 使用者族群
- 商品規格

【價格】

如果系統提供價格，
可以自然提及實際價格。

例如：

「價格為 9990 元。」

如果系統提供多個商品的價格，
可以描述明確存在的價格差異。

例如：

「這款價格比前兩款低 2000 元。」

但是不得自行延伸成：

「適合預算有限的使用者。」
「適合精打細算的使用者。」
「CP 值較高。」
「價格很划算。」

除非系統資料明確提供相關資訊。

不得自行換算價格。

不得自行新增折扣、優惠或其他金額。

【推薦度】

如果系統提供推薦度，
可以自然提及實際推薦度。

例如：

「推薦度為 74%。」

不得自行解釋推薦度代表：

- 品質
- 性能
- CP 值
- 使用體驗
- 功能完整度

除非系統資料明確提供相關說明。

【標籤】

標籤可以作為系統提供的資訊使用。

例如：

系統提供：
已知標籤：#GPS、#心率

可以寫：

「系統也標示了 GPS 和心率相關標籤。」

但禁止把標籤自行延伸成品質或性能評價。

例如：

GPS
不能自行寫成：
「高品質 GPS」
「精準 GPS」
「專業 GPS」
「GPS 導航能力」

心率
不能自行寫成：
「精準心率」
「專業心率監測」

【禁止自行推論】

不要因為商品有某個標籤，
就自行推論該功能的品質、程度或用途。

不要使用：

「高品質」
「精準」
「專業」
「基本功能」
「功能完整」
「表現出色」

除非這些內容是系統提供的推薦原因或商品資料。

不要自行推論：

「適合某種族群」
「適合某種程度的使用者」
「適合預算有限的人」
「適合專業使用者」

除非系統資料明確提供相關資訊。

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
17. 改變系統提供的推薦順位。
18. 重新計算推薦分數。
19. 宣稱「一定適合」。
20. 宣稱「最佳」。
21. 宣稱「最強」。
22. 宣稱「最值得購買」。
23. 宣稱「一定要買」。
24. 自行創造商品優缺點。
25. 自行創造商品品質評價。
26. 自行創造商品使用者族群。
27. 自行把標籤轉換成品質或性能評價。

【品牌與型號】

商品名稱必須以系統提供的商品名稱為準。

不要自行修改商品名稱。

不要自行補充系列名稱。

不要自行修正型號。

不要根據品牌或型號補充產品功能。

【語氣】
請用自然、像人在聊天時介紹商品的方式撰寫。

不要像報表。
不要像商品規格表。
不要逐項朗讀系統資料。

把自己想像成：
使用者問「這幾款為什麼推薦給我？」
你正在用很簡短的方式回答他。

文字可以有一點口語感，
但仍然必須保持客觀，
不能自行增加商品資訊。

【最重要】

不要把所有系統資料全部塞進介紹。

不要每個商品都同時寫：
價格 + 推薦度 + 標籤 + 推薦原因。

每個商品只挑最有代表性的資訊來說。

優先選擇：

1. 最主要的推薦原因
2. 與使用者需求最直接相關的資訊
3. 如果不同商品之間有明確差異，再補充該差異

其他資訊可以省略。

例如系統提供：

推薦原因：適合跑步訓練
已知標籤：GPS、心率
價格：9990 元
推薦度：74%

不要寫成：

「適合跑步訓練，系統標示 GPS 和心率監測功能，價格為 9990 元，推薦度 74%。」

這種寫法太像資料整理。

可以改成較自然的：

「如果你主要是拿來跑步，這款就是這次推薦中的主要選項，系統也標示了 GPS 和心率相關標籤。」

如果價格或推薦度沒有必要，
可以不要提。

【不同商品要有不同寫法】

不要讓每個商品都使用：

「這款……」
「這款……」
「這款……」

也不要讓每個商品都使用：

「適合……」
「同樣符合……」
「同樣符合……」

可以依照實際資料自然變化。

例如：

第 1 名：
「如果你主要是拿來跑步，這款就是這次推薦中的主要選項，系統也標示了 GPS 和心率相關標籤。」

第 2 名：
「同樣是以跑步訓練為主要推薦原因，這款另外有 GPS 標籤。」

第 3 名：
「如果比較在意價格，這款在目前三款中價格較低，同樣是以跑步訓練為推薦原因。」

以上只是語氣範例，
不能照抄，
實際內容必須依照系統提供的資料生成。

【價格的使用】

價格不是每個商品都必須提及。

只有在：

- 價格本身具有比較意義
- 價格是商品之間明顯的差異
- 或價格與使用者明確提供的預算有關

時，才優先考慮提及。

不要為了湊內容而報價格。

【推薦度的使用】

推薦度不是每個商品都必須提及。

如果沒有必要，
可以完全省略推薦度。

不要把推薦度自行解讀成：
品質、性能、CP值或功能完整度。

【禁止機械化表達】

盡量避免：

「系統推薦原因為……」
「系統標示……」
「符合本次推薦條件……」
「整體與目前需求較為吻合……」
「也是本次推薦結果中的選項……」
「推薦度為……」

除非這樣寫是為了表達必要資訊。

優先使用自然的句子，
不要像在念系統欄位。

【禁止自行推論】

自然不代表可以自由發揮。

禁止自行加入：

「高品質」
「精準」
「專業」
「強大」
「功能完整」
「表現出色」
「值得購買」
「適合預算有限的使用者」
「適合專業使用者」

除非系統資料明確提供這些資訊。

不要根據品牌、型號或自己的產品知識補充內容。

【最終目標】

使用者看完後，
應該感覺自己「看懂了這幾款為什麼被推薦」，

而不是感覺自己「看了一份商品資料表」。

自然、簡短、有推薦感，
但所有商品資訊都必須來自系統提供的資料。

【內容長度】

整體內容保持簡短。

第 1 名：
2～3 句。

第 2 名：
1～2 句。

第 3 名：
1 句。

避免重複相同句子。

避免對同一個商品重複描述相同推薦原因。

如果系統資料不足，
寧可簡短，
也不要自行補充資訊。

【格式】

不要 Markdown。

不要項目符號。

不要表格。

不要開場白。

不要額外解釋。

不要在最後加入額外結論。

【輸出格式】

根據實際商品數量輸出。

如果只有 1 項：

【第1名】
商品名稱
推薦內容

如果有 2 項：

【第1名】
商品名稱
推薦內容

【第2名】
商品名稱
推薦內容

如果有 3 項：

【第1名】
商品名稱
推薦內容

【第2名】
商品名稱
推薦內容

【第3名】
商品名稱
推薦內容

禁止輸出不存在的名次。

如果商品少於 3 項，
只介紹實際提供的商品。

【輸出前自我檢查】

在輸出之前，逐項檢查：

1. 每個商品名稱是否與系統提供的完全一致？
2. 是否按照推薦順位？
3. 是否只介紹系統提供的商品？
4. 是否說明了商品為什麼被推薦？
5. 是否有把使用者需求與系統提供的推薦原因自然連結？
6. 是否加入任何系統沒有提供的功能？
7. 是否加入任何系統沒有提供的規格？
8. 是否根據品牌或型號自行推測？
9. 是否加入系統沒有提供的數字？
10. 是否加入系統沒有提供的比較？
11. 是否重新排序商品？
12. 是否重新計算推薦結果？
13. 是否做出系統沒有支持的商品優劣結論？
14. 是否自行推論商品品質？
15. 是否自行推論使用者族群？
16. 是否把標籤延伸成品質或性能評價？
17. 如果刪除所有你自己的產品知識，
    內容是否仍然可以完全由系統提供資料支持？

如果任何一句無法由系統提供的資料直接支持，
刪除該句。

最後確認：

你的任務是「解釋系統已經完成的推薦結果」，
不是重新進行商品推薦。

你的文字應該自然、簡潔、有推薦感，
但不能自行創造任何商品資訊。

現在開始撰寫推薦內容。
"""

# ==================================================
# Strict Summary Check
# ==================================================

def _strict_summary_check(ai_reply, products):
    """
    本地檢查 AI Summary 是否只使用系統提供的商品資料。

    這一層不相信 AI Validator 的判斷，
    直接使用 products 作為唯一真實來源。
    """

    if not ai_reply or not ai_reply.strip():
        print("[Strict Summary Check] FAIL: empty response")
        return False

    # --------------------------------------------------
    # 建立系統允許的商品名稱集合
    # --------------------------------------------------

    allowed_names = []

    for product in products:

        name = (
            product.get("name")
            or product.get("title")
            or ""
        )

        name = str(name).strip()

        if name:
            allowed_names.append(name)

    # --------------------------------------------------
    # 檢查 AI 是否提到不存在的商品
    # --------------------------------------------------

    found_names = []

    for name in allowed_names:

        if name in ai_reply:
            found_names.append(name)

    print(
        f"[Strict Summary Check] "
        f"allowed_products={len(allowed_names)}"
    )

    print(
        f"[Strict Summary Check] "
        f"found_products={len(found_names)}"
    )

    # --------------------------------------------------
    # AI 必須至少正確引用商品
    # --------------------------------------------------

    if not found_names:

        print(
            "[Strict Summary Check] FAIL: "
            "no valid product name found"
        )

        return False

    # --------------------------------------------------
    # 商品名稱完整性檢查
    #
    # 如果 AI 出現商品名稱的明顯縮短版本，
    # 例如：
    #
    # 系統：
    # Amazfit Active 3 Premium 45mm 智慧跑錶
    #
    # AI：
    # Amazfit Active 3 Premium 45mm
    #
    # 就視為不可信。
    # --------------------------------------------------

    for product in products:

        full_name = (
            product.get("name")
            or product.get("title")
            or ""
        )

        full_name = str(full_name).strip()

        if not full_name:
            continue

        # 找到名稱中的品牌/型號主要部分
        words = full_name.split()

        if len(words) >= 2:

            # 如果 AI 出現前兩個以上的主要名稱，
            # 卻沒有完整名稱，視為可能被截短。
            prefix = " ".join(words[:2])

            if prefix in ai_reply and full_name not in ai_reply:

                print(
                    "[Strict Summary Check] FAIL: "
                    f"product name truncated -> {full_name}"
                )

                return False

    # --------------------------------------------------
    # 檢查價格
    # --------------------------------------------------

    allowed_prices = set()

    for product in products:

        price = product.get("price")

        if price is not None:
            allowed_prices.add(str(price))

    # --------------------------------------------------
    # 檢查推薦原因
    # --------------------------------------------------

    allowed_reasons = set()

    for product in products:

        reason = product.get("reason")

        if reason:
            allowed_reasons.add(str(reason).strip())

    # --------------------------------------------------
    # 檢查明顯的虛構推薦詞
    #
    # 這不是禁止所有自然語言，
    # 而是先擋掉已經知道會出現的
    # 「系統沒有提供的產品結論」。
    # --------------------------------------------------

    forbidden_phrases = [
        "專業跑者的好選擇",
        "最佳選擇",
        "最強",
        "頂級",
        "性能強大",
        "續航力強",
        "功能完整",
        "功能豐富",
        "非常適合",
    ]

    for phrase in forbidden_phrases:

        if phrase in ai_reply:

            print(
                "[Strict Summary Check] FAIL: "
                f"unsupported phrase -> {phrase}"
            )

            return False

    print("[Strict Summary Check] PASS")

    return True

# ==================================================
# Strict Summary Check
# ==================================================

def _build_fallback_summary(products):
    lines = []

    for idx, product in enumerate(products, start=1):

        name = (
            product.get("name")
            or product.get("title")
            or ""
        )

        price = product.get("price") or ""
        reason = product.get("reason") or ""

        tags = product.get("tags") or []

        if isinstance(tags, list):
            tags = [
                str(tag)
                for tag in tags
                if tag
            ]
            tag_text = "、".join(tags)
        else:
            tag_text = str(tags)

        lines.append(
            f"【第{idx}名】\n"
            f"商品名稱：{name}\n"
            f"價格：{price} 元\n"
            f"推薦原因：{reason}"
        )

        if tag_text:
            lines[-1] += f"\n已知標籤：{tag_text}"

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
        len(products),
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
        and user_need.budget.max < 999999
    ):
        budget_notice = (
            f"未找到符合 {user_need.budget.max} 元以下預算的商品，"
            f"以下推薦價格最接近需求的商品。\n\n"
        )

    # =========================
    # AI Summary
    # =========================

    print("[Summary Mode] AI")

    summary = ask_ai(
        summary_prompt,
        model_name=SUMMARY_MODEL,
    )

    # AI 沒有正常回傳 → 使用原本的 fallback Summary
    if not summary or not summary.strip():
        print("[Summary AI] Empty response -> fallback")
        summary = _build_fallback_summary(products)

    if budget_notice:
        summary = budget_notice + summary

    if DEBUG_SUMMARY:
        print("\n========== Summary ==========")
        print(summary)
        print("=============================\n")

    print("[Summary End]")

    return summary