import asyncio
import time
from services.intent_service import (
    detect_intent
)

from services.ollama_service import ask_ollama
from services.keyword_service import extract_keyword
from services.web_search_service import web_search_products
from services.product_formatter import format_product
from services.product_analyzer_service import analyze_product
from services.backend1_client import save_product
from services.db_search_service import search_db_products


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

            reply = ask_ollama(
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

        keyword_result = extract_keyword(
            conversation
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
            # =========================
            # 只分析前 3 筆商品
            # =========================

            analyzed_products = []

            for product in filtered_products[:3]:

                print("\n[Analyze Start]")
                print(product.get("title"))

                start = time.time()

                analyzed = analyze_product(
                    product
                )

                print(
                    f"[Analyze Time] "
                    f"{product.get('title')} "
                    f"{time.time() - start:.2f}s"
                )

                print("[Analyze End]")

                analyzed_products.append(
                    analyzed
                )

            # =========================
            # 覆蓋前 3 筆
            # =========================

            for idx, analyzed in enumerate(
                analyzed_products
            ):

                filtered_products[idx] = analyzed

            print("\n===== Analyze Result =====")

            for product in filtered_products:

                print(product)

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
                f"[DB] 命中資料庫商品 {len(filtered_products)} 筆"
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

        for product in filtered_products:

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
            formatted_products,
            start=1
        ):

            product_text += f"""

推薦順位：
{idx}

商品名稱：
{product.get('name', '')}

價格：
{product.get('price', '')}

平台：
{product.get('platform', '')}

評分：
{product.get('rating', '')}

推薦原因：
{product.get('reason', '')}
"""

        print("\n===== Product Summary =====")
        print(product_text)

        # =========================
        # AI Summary
        # =========================

        final_prompt = f"""
你是 WearWise 智慧穿戴推薦顧問。

請根據使用者需求與商品資料，
用自然聊天方式推薦商品。

規則：

1. 每個商品獨立介紹

2. 優先連結使用者需求

3. 說明為什麼適合

4. 可以提到商品價格

5. 不要逐條列功能

6. 不要說商品1商品2

7. 不要重複商品名稱

8. 使用繁體中文

9. 像真人推薦

10. 控制在200字內

11. 商品介紹順序必須依照推薦順位

12. 第一順位優先介紹

13. 不可自行更改推薦順序

14. 不可自行推測商品支援性或規格

15. 只能根據提供的商品資料介紹

16. 若資料未提及，禁止自行補充

17. 第一順位商品需詳細介紹

18. 第二順位商品可簡短介紹

19. 第三順位商品僅需一句話帶過

20. 優先說明第一順位推薦原因

21. 避免三個商品平均篇幅

22. 整體控制在150字內

23. 每個商品都必須提到價格

24. 價格請直接使用商品資料中的價格

25. 不可省略價格資訊

26. 不可自行判斷符合預算

27. 不可使用：
「符合預算」
「預算內」
「價格符合需求」

聊天紀錄：

{conversation}

目前使用者最新需求：

{user_message}

商品資料：

{product_text}
"""
        try:

            print("\n[Summary Start]")

            budget_notice = ""

            if budget_fallback:

                budget_notice = (

                    f"未找到完全符合 "
                    f"{budget_min}~{budget_max} 元"
                    f"預算的商品，"
                    f"以下推薦價格最接近需求的商品。\n\n"
                )

            start = time.time()

            ai_reply = ask_ollama(
                final_prompt
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