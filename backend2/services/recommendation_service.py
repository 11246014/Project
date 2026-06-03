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


def recommend_products(user_message):

    global chat_history

    try:

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
            user_message
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
            # 避免 Ollama timeout
            # =========================

            analyzed_products = []

            for product in filtered_products[:3]:

                analyzed = analyze_product(
                    product
                )

                analyzed_products.append(
                    analyzed
                )

            # =========================
            # 只覆蓋前 3 筆
            # 保留其餘商品
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

            final_prompt = f"""
你是一位台灣智慧穿戴裝置專賣店店員。

使用繁體中文與自然聊天口氣。

最近對話：
{conversation}

使用者最新訊息：
{user_message}

目前尚未找到符合條件的商品。

請：
1. 自然回覆使用者
2. 詢問需求
3. 不要推薦不存在的商品
4. 控制在3句內
"""

            ai_reply = ask_ollama(
                final_prompt
            )

            chat_history.append(
                f"AI: {ai_reply}"
            )

            return {

                "summary": ai_reply,

                "products": []
            }

        # =========================
        # 商品格式統一
        # =========================

        formatted_products = []

        for product in filtered_products:

            formatted_products.append(
                format_product(product)
            )

        # =========================
        # 建立商品摘要
        # =========================

        product_text = ""

        for idx, product in enumerate(
            formatted_products[:3],
            start=1
        ):

            product_text += f"""
商品{idx}

名稱：
{product.get('name', '')}

價格：
{product.get('price', 0)}

推薦理由：
{product.get('reason', '')}
"""

        print("\n===== Product Summary =====")
        print(product_text)

        # =========================
        # AI 推薦
        # =========================

        final_prompt = f"""
你是智慧穿戴商品推薦助手。

請根據使用者需求推薦商品。

使用者需求：
{user_message}

商品資料：
{product_text}

請用繁體中文簡短推薦，
控制在100字內。
"""

        try:

            ai_reply = ask_ollama(
                final_prompt
            )

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