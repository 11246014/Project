import asyncio

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
        "智慧"
    ]

    for keyword in keywords:

        if keyword in message:

            return True

    return False


def recommend_products(user_message):

    global chat_history

    try:

        # =========================
        # 非商品需求
        # =========================

        if (
            not is_product_request(user_message)
            and len(chat_history) <= 1
        ):

            return {

                "summary": (
                    "您好～我是 WearWise 智慧穿戴助手！\n"
                    "您可以直接輸入：\n"
                    "『推薦運動手錶』\n"
                    "『睡眠監測手環』\n"
                    "『GPS智慧手錶』"
                ),

                "products": []
            }

        # =========================
        # 記錄聊天
        # =========================

        chat_history.append(
            f"使用者: {user_message}"
        )

        chat_history = chat_history[-6:]

        conversation = "\n".join(
            chat_history
        )

        # =========================
        # Keyword Extraction
        # =========================

        search_keyword = extract_keyword(
            conversation
        )

        print("\n====== Recommend Start ======")
        print(f"User: {user_message}")
        print(f"Keyword: {search_keyword}")

        # =========================
        # 先查資料庫
        # =========================

        filtered_products = asyncio.run(
            search_db_products(
                search_keyword
            )
        )

        # =========================
        # DB 沒資料 → SerpAPI
        # =========================

        if not filtered_products:

            print("[DB] 無資料，改用 SerpAPI")

            filtered_products = web_search_products(
                search_keyword
            )

            print(
                f"[Web Search] 找到 {len(filtered_products)} 筆商品"
            )

            # =========================
            # 只分析前 3 筆商品
            # =========================

            analyzed_products = []

            for product in filtered_products[:3]:

                print("\n[Analyze Start]")
                print(product.get("title"))

                analyzed = analyze_product(
                    product
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
        # 固定只回傳 3 筆
        # =========================

        formatted_products = []

        for product in filtered_products[:3]:

            formatted_products.append(
                format_product(product)
            )

        # =========================
        # 商品摘要
        # =========================

        product_text = ""

        for product in formatted_products:

            product_text += f"""

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

4. 可以提到價格是否符合需求

5. 不要逐條列功能

6. 不要說商品1商品2

7. 不要重複商品名稱

8. 使用繁體中文

9. 像真人推薦

10. 控制在200字內

聊天紀錄：

{conversation}

目前使用者最新需求：

{user_message}

商品資料：

{product_text}
"""
        try:

            print("\n[Summary Start]")

            ai_reply = ask_ollama(
                final_prompt
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