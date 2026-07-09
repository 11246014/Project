import asyncio
import time
from services.intent_service import (
    detect_intent
)

from services.ai_service import ask_ai
from config.settings import AI_PROVIDER
from services.chat_parser import parse_chat_message
from services.web_search_service import web_search_products
from services.product_formatter import format_product
# from services.product_analyzer_service import analyze_product
from services.backend1_client import save_product
from services.db_search_service import search_db_products
# from services.ai_rerank_service import ai_rerank


# =========================
# 簡易聊天記憶
# =========================

chat_history = []

# Keyword 專用記憶
user_history = []

# =========================
# 判斷是否為商品需求
# =========================

def is_product_request(message):

    keywords = [

        "手錶",
        "手環",
        "耳機",
        "穿戴",

        "推薦",
        "想找",

        "運動",
        "睡眠",
        "GPS",

        "健康",
        "智慧",

        "apple",
        "watch",

        "garmin",
        "amazfit",

        "galaxy",
        "huawei",

        "fitbit"
    ]
    for keyword in keywords:

        if keyword in message:

            return True

    return True


def recommend_products(user_message):

    total_start = time.time()
    global chat_history
    global user_history

    try:

        # =========================
        # Intent Detection
        # =========================

        intent = detect_intent(
            user_message
        )

        print(
            f"[Intent] {intent}"
        )

        if intent == "chat":

            reply = ask_ai(
                user_message
            )

            return {

                "summary": reply,

                "products": []
            }


        # =========================
        # 記錄聊天
        # =========================

        chat_history.append(
            f"使用者: {user_message}"
        )

        user_history.append(
            user_message
        )

        # AI摘要用
        chat_history = chat_history[-6:]

        # Keyword Extraction用
        user_history = user_history[-3:]

        conversation = "\n".join(
            user_history
        )

        # =========================
        # Keyword Extraction
        # =========================

        print("\n========== Conversation ==========")
        print(conversation)
        print("==================================\n")

        start = time.time()

        conversation_for_keyword = "\n".join(
            conversation.split("\n")[-5:]
        )

        recommendation_request = parse_chat_message(
            conversation_for_keyword
        )

        user_need = recommendation_request.need
        print(
            f"[Keyword Time] "
            f"{time.time() - start:.2f}s"
        )

        search_keyword = (
            user_need.search_query
            or ""
        )

        budget_min = (
            user_need.budget.min
            or 0
        )

        budget_max = (
            user_need.budget.max
            or 0
        )

        if not search_keyword:

            search_keyword = user_message

        print(
            f"[Budget] "
            f"{budget_min} ~ {budget_max}"
        )
        
        search_query = search_keyword

        if budget_max >= 10000:

            search_query += (
                f" {budget_min // 10000}萬到"
                f"{budget_max // 10000}萬"
            )

        print(
            f"[Search Query] "
            f"{search_query}"
        )

        print("\n====== Recommend Start ======")
        print(f"User: {user_message}")
        print(f"Keyword: {search_keyword}")

        # =========================
        # 先查資料庫
        # =========================
        start = time.time()

        filtered_products = asyncio.run(
            search_db_products(
                search_keyword
            )
        )

        print(
            f"[DB Search Time] "
            f"{time.time() - start:.2f}s"
        )

        # =========================
        # DB 沒資料 → SerpAPI
        # =========================
        if not filtered_products:

            print(
                "[DB] 無資料，改用 SerpAPI"
            )

            search_query = search_keyword

            if budget_max > 0:

                search_query += (
                    f" {budget_min // 10000}萬到"
                    f"{budget_max // 10000}萬"
                )

            print(
                f"[Search Query] "
                f"{search_query}"
            )

            start = time.time()

            filtered_products = (
                web_search_products(
                    search_query
                )
            )

            print(
                f"[Web Search Time] "
                f"{time.time() - start:.2f}s"
            )
        # =========================
        # Budget Filter
        # =========================

        budget_fallback = False

        original_products = (
            filtered_products.copy()
        )

        if budget_max > 0:

            before_count = len(
                filtered_products
            )

            filtered_products = [

                p for p in filtered_products

                if budget_min <=
                p.get(
                    "price",
                    0
                )
                <= budget_max
            ]

            print(
                f"[Budget Filter] "
                f"{before_count} -> "
                f"{len(filtered_products)}"
            )

            # =========================
            # 沒找到符合預算
            # =========================

            if len(filtered_products) == 0:

                budget_fallback = True

                print(
                    "[Budget Fallback]"
                )

                original_products.sort(

                    key=lambda p: (

                        p.get(
                            "price",
                            0
                        ) < budget_min,

                        abs(
                            p.get(
                                "price",
                                0
                            )
                            - budget_min
                        )
                    )
                )

                filtered_products = (
                    original_products[:3]
                )
            # # =========================
            # # 只分析前 3 筆商品
            # # =========================

            # analyzed_products = []

            # for product in filtered_products[:3]:

            #     print("\n[Analyze Start]")
            #     print(product.get("title"))

            #     start = time.time()

            #     start = time.time()

            #     analyzed = analyze_product(
            #         product
            #     )

            #     print(
            #         f"[Analyze Time] "
            #         f"{product['title']} "
            #         f"{time.time() - start:.2f}s"
            #     )

            #     print(
            #         f"[Analyze Time] "
            #         f"{product.get('title')} "
            #         f"{time.time() - start:.2f}s"
            #     )

            #     print("[Analyze End]")

            #     analyzed_products.append(
            #         analyzed
            #     )

            # # =========================
            # # 覆蓋前 3 筆
            # # =========================

            # for idx, analyzed in enumerate(
            #     analyzed_products
            # ):

            #     filtered_products[idx] = analyzed

            # print("\n===== Analyze Result =====")

            # for product in filtered_products:

            #     print(product)

            # =========================
            # 存進 Backend1
            # =========================

            for product in filtered_products:

                try:

                    if product.get("title"):

                        asyncio.run(
                            save_product(product)
                        )

                        print(
                            f"[Saved] {product.get('title')}"
                        )

                except Exception as e:

                    print(
                        f"[Save Error] {e}"
                    )

        else:

            print(
                 f"[Products] 共 {len(filtered_products)} 筆"
            )

        # =========================
        # 沒找到商品
        # =========================

        if not filtered_products:

            ai_reply = (
                "目前尚未找到符合需求的商品，"
                "可以再試試其他關鍵字。"
            )

            return {

                "summary": ai_reply,

                "products": [],

                "user_need": user_need.to_dict()
            }
        # =========================
        # Feature Weighting Lite
        # =========================

        conversation_text = conversation.lower()
        
        need_count = 0

        if "gps" in conversation_text:
            need_count += 1

        if "睡眠" in conversation_text:
            need_count += 1

        if "心率" in conversation_text:
            need_count += 1

        if "血氧" in conversation_text:
            need_count += 1

        if "ecg" in conversation_text:
            need_count += 1
        for idx, product in enumerate(filtered_products):

            score = product.get(
                "match",
                0
            )

            reason_parts = []

            features_text = " ".join(
                product.get(
                    "features",
                    []
                )
            ).lower()

            title_text = str(
                product.get(
                    "title",
                    ""
                )
            ).lower()

            # ===== GPS =====

            if "gps" in conversation_text:

                if "gps" in features_text:

                    score += 40

                    reason_parts.append("支援GPS定位")

            # ===== 睡眠 =====

            if (
                "睡眠" in conversation_text
                or "sleep" in conversation_text
            ):

                if "睡眠" in features_text:

                    score += 40

                    reason_parts.append("具備睡眠監測")

            # ===== 心率 =====

            if "心率" in conversation_text:

                if "心率" in features_text:

                    score += 30

                    reason_parts.append("提供心率監測")

            # ===== 血氧 =====

            if "血氧" in conversation_text:

                if "血氧" in features_text:

                    score += 30

                    reason_parts.append("支援血氧偵測")

            # ===== ECG =====

            if "ecg" in conversation_text:

                if (
                    "ecg" in features_text
                    or "心電圖" in features_text
                ):

                    score += 30

                    reason_parts.append("具備ECG心電圖功能")
            

            # ===== iPhone =====

            if (
                "iphone" in conversation_text
                or "ios" in conversation_text
            ):

                if "apple" in title_text:

                    score += 15

            # # =========================
            # # AI ReRank(上台展示直接關掉)
            # # =========================

            # if idx == 0:

            #     try:

            #         rerank = ai_rerank(
            #             conversation,
            #             product
            #         )

            #         ai_score = rerank.get(
            #             "score",
            #             50
            #         )

            #         print(
            #             f"[AI Score] "
            #             f"{product.get('title')} "
            #             f"{ai_score}"
            #         )

            #         score += ai_score // 4

            #         print(
            #             "[DEBUG]",
            #             score,
            #             ai_score,
            #             ai_score // 2
            #         )

            #         product["reason"] = (
            #             rerank.get(
            #                 "reason",
            #                 ""
            #             )
            #         )

            #     except Exception as e:

            #         print(
            #             f"[AI ReRank Error] {e}"
            #         )
            if reason_parts:

                product["reason"] = "、".join(reason_parts)

            else:

                product["reason"] = "符合使用需求"

            matched_count = len(reason_parts)

            if need_count > 0:

                hit_rate = matched_count / need_count

            else:

                hit_rate = 0
            final_score = int(
                score * 0.4 +
                hit_rate * 100 * 0.6
            )
            print(
                "[Hit Rate]",
                product.get("title"),
                f"{matched_count}/{need_count}",
                f"{hit_rate:.2f}",
                final_score
            )

            product["match"] = final_score

        # =========================
        # 重新排序
        # =========================

        filtered_products.sort(

            key=lambda x: x.get(
                "match",
                0
            ),

            reverse=True
        )

        print("\n===== ReRank Result =====")

        for product in filtered_products[:5]:

            print(
                product.get("title"),
                product.get("match")
            )
                

        # =========================
        # 固定只回傳 3 筆
        # =========================

        formatted_products = []

        for product in filtered_products[:3]:

            formatted_products.append(
                format_product(product)
            )
        # =========================
        # 保底處理
        # =========================

        if len(formatted_products) == 0:

            ai_reply = (
                "條件較嚴格，目前未找到完全符合的商品，"
                "建議放寬部分條件後再試試。"
            )

            return {

                "summary": ai_reply,

                "products": [],

                "user_need": user_need.to_dict()
            }

        # =========================
        # 商品摘要
        # =========================

        product_text = ""

        for idx, product in enumerate(
            formatted_products[:3],
            start=1
        ):

            product_text += f"""
順位:{idx}
商品:{product.get('name')}
價格:{product.get('price')}元
評分:{product.get('match')}
推薦原因:{product.get('reason')}
"""

        print("\n===== Product Summary =====")
        print(product_text)


        # =========================
        # AI Summary
        # =========================

        ollama_prompt = f"""
你是 WearWise 智慧穿戴推薦顧問。

請依照順位推薦商品。

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
        gemini_prompt = f"""
你是 WearWise 智慧穿戴推薦顧問。

請依照順位推薦商品。

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
        if AI_PROVIDER == "gemini":

            final_prompt = gemini_prompt

        else:

            final_prompt = ollama_prompt

        try:

            print("\n[Summary Start]")
            print(
                f"[Product Text Length] {len(product_text)}"
            )

            budget_notice = ""

            if budget_fallback:

                budget_notice = (

                    f"未找到完全符合 "
                    f"{budget_min}~{budget_max} 元"
                    f"預算的商品，"
                    f"以下推薦價格最接近需求的商品。\n\n"
                )

            start = time.time()

            from config.settings import SUMMARY_MODEL

            ai_reply = ask_ai(
                final_prompt,
                model_name=SUMMARY_MODEL
            )
            print(
                f"[Summary Time] "
                f"{time.time() - start:.2f}s"
            )

            if budget_notice:

                ai_reply = (
                    budget_notice
                    + ai_reply
                )

            if not ai_reply.strip():

                ai_reply = (
                    "已為您整理幾款符合需求的商品，"
                    "可以參考下方推薦。"
                )

            print(
                f"[Summary Content] {ai_reply}"
            )

            print("[Summary End]")

        except Exception as e:

            print(
                f"[Recommend AI Error] {e}"
            )

            ai_reply = (
                "目前 AI 推薦暫時無法產生，"
                "但已列出符合需求的商品。"
            )
        # =========================
        # AI 回覆記錄
        # =========================

        chat_history.append(
            f"AI: {ai_reply}"
        )

        chat_history = chat_history[-6:]

        print(
            f"[Total Time] "
            f"{time.time() - total_start:.2f}s"
        )

        print("====== Recommend End ======\n")

        # =========================
        # 回傳前端
        # =========================

        return {

            "summary": ai_reply,

            "products": formatted_products,

            "user_need": user_need.to_dict()
        }

    except Exception as e:

        print(
            f"[Recommendation Error] {e}"
        )

        return {

            "summary": "不好意思，目前推薦系統有點忙碌，請稍後再試～",

            "products": [],

            "error": str(e)
        }
