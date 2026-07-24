import time

from config.settings import SUMMARY_MODEL
from services.ai_service import ask_ai

def _build_persona_text(persona):
    """
    將使用者 Persona 轉換成自然語言描述，
    讓 AI 生成摘要時能參考此背景資訊。

    只有欄位存在時才輸出對應描述，避免產生空泛或誤導的句子。
    """

    parts = []

    if persona.age_range:
        parts.append(f"年齡層為{persona.age_range}")

    if persona.occupation:
        parts.append(f"職業為{persona.occupation}")

    if persona.usage_scope:
        scope_map = {
            "個人使用": "此次為個人使用",
            "家庭共用": "此次為家庭共用",
            "要送禮": "此次用途為送禮",
        }
        parts.append(
            scope_map.get(persona.usage_scope, f"使用情境為{persona.usage_scope}")
        )

    if persona.current_device:
        parts.append(f"目前使用的穿戴裝置為{persona.current_device}")

    if not parts:
        return ""

    return "使用者背景：" + "、".join(parts) + "。\n\n"

def generate_summary(
    products,
    user_need,
    budget_fallback=False
):
    print("[Summary Service]")
    
    if not products:
        return "目前沒有找到符合條件的推薦商品。"

    # =========================
    # 建立商品摘要文字
    # =========================

    product_text = ""

    for idx, product in enumerate(products, start=1):

        product_text += f"""
順位:{idx}
商品:{product.get('name', '')}
價格:{product.get('price', '')}元
評分:{product.get('match', 0)}
推薦原因:{product.get('reason', '')}
"""

    # =========================
    # Prompt
    # =========================

    persona_text = _build_persona_text(user_need.persona)

    summary_prompt = f"""
你是 WearWise 智慧穿戴推薦顧問。

{persona_text}請依照順位推薦商品。

規則：

1. 依照順位1、2、3介紹
2. 第一順位介紹較詳細
3. 第二順位簡短介紹
4. 第三順位簡單帶過
5. 每個商品都要提到價格
6. 優先參考推薦原因
7. 不可推測不存在的功能
8. 不可自行補充規格
9. 不可自行比較產品優劣
10. 不可自行總結
11. 不要出現「建議依需求選擇」
12. 不要出現結論段落
13. 不要出現開場白
14. 使用繁體中文
15. 控制在150~220字
16. 不要使用 Markdown
17. 不要使用 ** ##
18. 直接輸出純文字
19. 不要只重複推薦原因欄位內容
20. 回覆直接從第一順位開始介紹
21. 請將推薦原因改寫成自然語句
22. 不要重複使用相同推薦詞句
23. 優先參考推薦原因與評分內容撰寫介紹
24. 只能使用商品資料中的推薦原因。
25. 若資料未提及，不得自行補充任何功能。
26. 若推薦原因只有GPS，則以GPS相關用途作為介紹重點。
27. 若推薦原因未提及心率，不得提及心率。
28. 若推薦原因未提及睡眠，不得提及睡眠。
29. 若推薦原因未提及血氧，不得提及血氧。
30. 不得根據品牌名稱推測功能。
31. 不得根據型號推測功能。
32. 可將推薦原因改寫為自然語句，但不得改變原意。
33. 若上方提供使用者背景資訊，可適度呼應（例如提及此為送禮用途、或提及升級自目前裝置），但不得虛構背景中未提及的功能或規格。

格式範例：

1. 商品A（3000元）
推薦原因...

2. 商品B（5000元）
推薦原因...

3. 商品C（2000元）
推薦原因...

商品資料：

{product_text}
"""

    try:
        print("========== Summary Input ==========")

        for p in products:
            print(p)

        print("===================================")
        
        print("\n[Summary Start]")
        print(
            f"[Product Text Length] {len(product_text)}"
        )

        budget_notice = ""

        if budget_fallback:

            budget_notice = (
                f"未找到完全符合 "
                f"{user_need.budget.min}~{user_need.budget.max} 元"
                f"預算的商品，"
                f"以下推薦價格最接近需求的商品。\n\n"
            )

        start = time.time()

        ai_reply = ask_ai(
            summary_prompt,
            model_name=SUMMARY_MODEL
        )

        print(
            f"[Summary Time] "
            f"{time.time() - start:.2f}s"
        )

        if budget_notice:
            ai_reply = budget_notice + ai_reply

        if not ai_reply or not ai_reply.strip():

            ai_reply = (
                "已為您整理幾款符合需求的商品，"
                "可以參考下方推薦。"
            )

        print(
            f"[Summary Content] {ai_reply}"
        )

        print("[Summary End]")

        return ai_reply

    except Exception as e:

        print(f"[Summary Error] {e}")

        return (
            "目前 AI 推薦暫時無法產生，"
            "但已列出符合需求的商品。"
        )