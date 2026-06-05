import asyncio
import time
from services.intent_service import (
    detect_intent
)

from services.ai_service import ask_ai
from config.settings import AI_PROVIDER
from services.keyword_service import extract_keyword
from services.web_search_service import web_search_products
from services.product_formatter import format_product
from services.product_analyzer_service import analyze_product
from services.backend1_client import save_product
from services.db_search_service import search_db_products
from services.ai_rerank_service import ai_rerank


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

        keyword_result = extract_keyword(
            conversation_for_keyword
        )
        print(
            f"[Keyword Time] "
            f"{time.time() - start:.2f}s"
        )

        search_keyword = keyword_result.get(
            "keyword",
            ""
        )

        budget_min = keyword_result.get(
            "budget_min",
            0
        )

        budget_max = keyword_result.get(
            "budget_max",
            0
        )

        if not search_keyword:

            search_keyword = user_message

        print(
            f"[Budget] "
            f"{budget_min} ~ {budget_max}"
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

                "products": []
            }
        # =========================
        # Feature Weighting Lite
        # =========================

        conversation_text = conversation.lower()

        for idx, product in enumerate(filtered_products):

            print(
                "[Before AI]",
                product.get("title"),
                product.get("match")
            )
            score = product.get(
                "match",
                0
            )

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

                    score += 15

            # ===== 睡眠 =====

            if (
                "睡眠" in conversation_text
                or "sleep" in conversation_text
            ):

                if "睡眠" in features_text:

                    score += 15

            # ===== 心率 =====

            if "心率" in conversation_text:

                if "心率" in features_text:

                    score += 10

            # ===== 血氧 =====

            if "血氧" in conversation_text:

                if "血氧" in features_text:

                    score += 10

            # ===== ECG =====

            if "ecg" in conversation_text:

                if (
                    "ecg" in features_text
                    or "心電圖" in features_text
                ):

                    score += 20

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

            product["match"] = score

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

                "products": []
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
推薦順位:{idx}
商品名稱:{product.get('name')}
價格:{product.get('price')}
"""

        print("\n===== Product Summary =====")
        print(product_text)

        import re

        age = ""
        job = ""
        preference = ""
        current_product = ""

        text = conversation.lower()

        # 年齡

        age_match = re.search(
            r"(\d{1,3})\s*歲",
            conversation
        )

        if age_match:

            age = age_match.group(1)

        # 職業

        jobs = [
            "老師",
            "學生",
            "工程師",
            "上班族",
            "業務",
            "醫師"
        ]

        for j in jobs:

            if j in conversation:

                job = j

        # 偏好

        preferences = [
            "跑步",
            "健身",
            "游泳",
            "登山",
            "騎車"
            "健康管理",
            "睡眠",
            "戶外",
            "商務",
            "日常"
        ]

        for p in preferences:

            if p in conversation:

                preference = p

        # 目前使用產品

        brands = [
            "garmin",
            "apple watch",
            "galaxy watch",
            "amazfit",
            "huawei"
        ]

        for b in brands:

            if b in text:

                current_product = b

                break
        # =========================
        # AI Summary
        # =========================

        ollama_prompt = f"""
你是 WearWise 智慧穿戴推薦顧問。

請根據使用者需求與商品資料，
用自然聊天方式推薦商品。

規則：

1. 必須依照推薦順位介紹
2. 第一順位優先介紹
3. 不可自行更改推薦順序
4. 第一順位可稍微詳細
5. 第二順位簡短介紹
6. 第三順位一句話即可
7. 每個商品都必須提到價格
8. 價格必須直接使用提供資料
9. 不可省略價格
10. 不可自行推測功能或規格
11. 不可補充未提供資訊
12. 不可自行判斷符合預算
13. 不可使用：
   - 符合預算
   - 預算內
   - 價格符合需求
14. 使用繁體中文
15. 使用台灣用語
16. 控制在150字內
17. 若使用者資訊為「未提供」請直接忽略
18. 可參考使用者年齡、職業、偏好與目前使用商品
19. 優先說明第一順位推薦原因
20. 不要重複商品名稱過多次

使用者資訊：

年齡：
{age if age else "未提供"}

職業：
{job if job else "未提供"}

偏好：
{preference if preference else "未提供"}

目前使用商品：
{current_product if current_product else "未提供"}

最新需求：

{user_message}

商品資料：

{product_text}
"""
        gemini_prompt = f"""
你是 WearWise 智慧穿戴推薦顧問。

請根據推薦順位介紹商品。

規則：

1. 只能使用商品名稱與價格
2. 禁止推測任何功能
3. 禁止推測任何規格
4. 禁止推測 GPS
5. 禁止推測心率
6. 禁止推測血氧
7. 禁止推測睡眠監測
8. 第一名介紹稍微詳細
9. 第二名簡短介紹
10. 第三名一句話即可
11. 每個商品都必須提到價格
12. 必須依照推薦順位
13. 使用繁體中文
14. 控制150字內

使用者資訊：

年齡：
{age if age else "未提供"}

職業：
{job if job else "未提供"}

偏好：
{preference if preference else "未提供"}

目前使用商品：
{current_product if current_product else "未提供"}

使用者需求：

{user_message}

商品：

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

            "products": formatted_products
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