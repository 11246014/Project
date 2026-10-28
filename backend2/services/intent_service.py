# services/intent_service.py

import re

from services.ai_service import ask_ai
from config.settings import KEYWORD_MODEL


# ==================================================
# Quick Intent Keywords
# ==================================================

# 明確代表「商品推薦 / 商品需求」的關鍵字。
# 命中時直接回傳 recommend，不需要呼叫 Gemini。
RECOMMEND_KEYWORDS = (
    # 推薦 / 購買
    "推薦",
    "建議",
    "想買",
    "要買",
    "幫我買",
    "幫我找",
    "幫我推薦",
    "推薦一下",
    "推薦一",
    "推薦幾",
    "哪一支",
    "哪個比較好",
    "哪款比較好",
    "哪一款",
    "比較一下",
    "比較看看",

    # 商品
    "智慧手錶",
    "智能手錶",
    "智慧手環",
    "智能手環",
    "藍牙耳機",
    "無線耳機",
    "穿戴裝置",
    "運動手錶",
    "運動手環",
    "smartwatch",
    "smart watch",
    "smart band",
    "earbuds",
    "airpods",

    # 品牌
    "apple watch",
    "garmin",
    "samsung",
    "galaxy watch",
    "huawei",
    "amazfit",
    "fitbit",
    "xiaomi",
    "coros",
    "polar",
    "suunto",
    "oura",
    "ringconn",

    # 常見需求條件
    "預算",
    "價格",
    "多少錢",
    "幾千",
    "一萬",
    "兩萬",
    "三萬",
    "gps",
    "心率",
    "血氧",
    "睡眠",
    "跑步",
    "運動",
    "游泳",
    "健身",
    "續航",
    "電池",
    "iphone",
    "ios",
    "android",
)


# 明確代表一般聊天的訊息。
# 只有很明確的情況才直接判斷 chat，
# 避免錯把商品需求判成一般聊天。
CHAT_EXACT_MESSAGES = {
    "你好",
    "嗨",
    "哈囉",
    "hello",
    "hi",
    "hey",
    "早安",
    "午安",
    "晚安",
    "謝謝",
    "謝謝你",
    "感謝",
    "感謝你",
}


# 一般聊天 / 系統功能相關關鍵字。
CHAT_KEYWORDS = (
    "你可以做什麼",
    "你能做什麼",
    "你會做什麼",
    "怎麼使用",
    "怎麼用你",
    "你是誰",
    "你叫什麼",
    "你好嗎",
    "今天天氣",
    "只是聊天",
    "陪我聊天",
)


# ==================================================
# Helpers
# ==================================================

def _normalize_message(message):
    """
    將使用者訊息做最基本的正規化。

    不修改原始訊息內容，
    只用於 Quick Intent 判斷。
    """

    if message is None:
        return ""

    return str(message).strip()


def _quick_intent(message, in_recommendation=False):
    """
    使用 Python 規則快速判斷 Intent。

    回傳：
        "recommend"
        "chat"
        None

    None 代表：
        Python 無法安全判斷，
        交給 Gemini。

    設計原則：

    1. 正在推薦流程中：
       使用者的短回答預設視為 recommend。

    2. 明確商品 / 購買 / 推薦需求：
       直接 recommend。

    3. 明確問候 / 閒聊：
       直接 chat。

    4. 不確定：
       回傳 None，交給 Gemini。
    """

    text = _normalize_message(message)

    if not text:
        return None

    text_lower = text.lower()

    # ==================================================
    # 1. Recommendation Context
    # ==================================================
    #
    # 如果目前已經在推薦需求確認流程，
    # 大部分後續回答都是需求條件。
    #
    # 例如：
    #   跑步
    #   睡眠
    #   Garmin
    #   一萬五以內
    #   要 GPS
    #
    # 這些應直接視為 recommend。
    #
    if in_recommendation:

        # 明確的一般聊天 / 問候仍可判斷 chat。
        if text_lower in CHAT_EXACT_MESSAGES:
            return "chat"

        for keyword in CHAT_KEYWORDS:
            if keyword in text_lower:
                return "chat"

        # 推薦流程中的任何非空短回答，
        # 都先視為推薦需求延續。
        #
        # 這與原本 Prompt 的設計一致：
        # 「使用者是在回答前一個需求問題」
        # → recommend
        if len(text) <= 30:
            return "recommend"

        # 長訊息如果明確包含商品需求，
        # 也可以直接判斷。
        for keyword in RECOMMEND_KEYWORDS:
            if keyword in text_lower:
                return "recommend"

        # 長訊息且無法安全判斷，
        # 交給 Gemini。
        return None

    # ==================================================
    # 2. Exact Chat
    # ==================================================

    if text_lower in CHAT_EXACT_MESSAGES:
        return "chat"

    # ==================================================
    # 3. Chat Keywords
    # ==================================================

    for keyword in CHAT_KEYWORDS:
        if keyword in text_lower:
            return "chat"

    # ==================================================
    # 4. Recommendation Keywords
    # ==================================================

    for keyword in RECOMMEND_KEYWORDS:
        if keyword in text_lower:
            return "recommend"

    # ==================================================
    # 5. Budget / Requirement Pattern
    # ==================================================
    #
    # 有些使用者不一定寫出「推薦」，
    # 但直接輸入需求條件。
    #
    # 例如：
    #   10000
    #   10000元
    #   一萬五以內
    #   5000-10000
    #
    # 如果單獨出現價格資訊，
    # 很可能是在提供商品需求。
    #
    if re.search(
        r"\d+\s*(元|塊|k|千|萬)",
        text_lower,
    ):
        return "recommend"

    if re.search(
        r"\d+\s*[-~到至]\s*\d+",
        text_lower,
    ):
        return "recommend"

    if re.search(
        r"(一萬|兩萬|二萬|三萬|四萬|五萬)"
        r".{0,6}"
        r"(內|以下|以內|左右|上下)",
        text,
    ):
        return "recommend"

    # ==================================================
    # 6. Very Short Requirement Answers
    # ==================================================
    #
    # 在沒有推薦上下文時，
    # 單純一個「跑步」「睡眠」等詞，
    # 無法 100% 確定是不是推薦需求。
    #
    # 所以這裡不要直接判斷，
    # 交給 Gemini。
    #
    # 這是為了避免誤判一般聊天。
    #
    return None


# ==================================================
# Main Intent Detection
# ==================================================

def detect_intent(message, in_recommendation=False):
    """
    判斷使用者訊息：

        recommend
        chat

    流程：

        User Message
             ↓
        Quick Intent
             │
             ├── recommend → 直接返回
             │
             ├── chat → 直接返回
             │
             └── None
                    ↓
                Gemini
                    ↓
            recommend / chat

    Quick Intent 的目的：

    - 減少不必要的 Gemini 呼叫
    - 降低 Intent Detection 延遲
    - 保留 Gemini 作為 fallback
    - 不改變原本 detect_intent() 的使用方式
    """

    # ==================================================
    # Quick Intent
    # ==================================================

    quick_result = _quick_intent(
        message,
        in_recommendation=in_recommendation,
    )

    if quick_result is not None:

        print(
            f"[Intent Quick] "
            f"{quick_result} "
            f"(skip AI)"
        )

        return quick_result

    # ==================================================
    # Conversation Context
    # ==================================================

    conversation_context = ""

    if in_recommendation:

        conversation_context = """
目前這段對話已經進入「商品推薦需求確認」階段。

因此，如果使用者只是回答前一個問題，
例如：

- 睡眠
- 跑步
- 主要拿來運動
- 一萬五以內
- 要有心率
- 要有血氧
- iPhone
- Android
- Garmin
- 希望續航久一點

這些都屬於商品推薦需求，
必須回答：

recommend

即使這一句單獨看起來像一般聊天，
只要是在延續商品推薦需求，
仍然回答 recommend。
"""

    # ==================================================
    # Intent Prompt
    # ==================================================

    prompt = f"""
你是 WearWise 的對話意圖判斷器。

你的任務只有一個：

判斷使用者目前的訊息屬於
「商品推薦對話」
還是
「一般聊天」。

你只能輸出以下其中一個：

recommend
chat

不要輸出任何其他文字。

【重要：目前是否正在推薦流程】

{conversation_context}

如果目前已經進入商品推薦需求確認階段，
使用者後續回答前一個問題時，
即使回答只有一個詞或一個條件，
也必須判斷為 recommend。

例如：

- 睡眠
- 跑步
- 主要拿來運動
- 一萬五以內
- 要有心率
- 要有血氧
- iPhone
- Android
- Garmin
- 希望續航久一點

這些都屬於推薦需求的延續。

因此回答：

recommend


【一般商品推薦】

如果使用者正在：

- 尋找商品
- 購買商品
- 比較商品
- 詢問商品
- 要求推薦商品

回答：

recommend

例如：

- 我想買一支智慧手錶
- 幫我找智慧手環
- 有推薦的 Garmin 嗎？
- 哪一支智慧手錶比較好？
- 幫我推薦適合跑步的手錶
- 我想找適合睡眠的穿戴裝置

即使使用者提供的需求還不完整，
仍然回答 recommend。

「需求是否完整」不是你的判斷工作。

不要因為需求不完整而回答 chat。


【一般聊天】

只有當使用者沒有進行商品推薦需求，
而是在：

- 問候
- 閒聊
- 感謝
- 詢問系統功能

才回答：

chat

例如：

- 你好
- 你好嗎？
- 謝謝你
- 我只是想跟你聊天
- 你可以做什麼？

【使用者訊息】

{message}

只輸出：

recommend

或

chat
"""

    # ==================================================
    # AI Intent Detection
    # ==================================================

    try:

        result = ask_ai(
            prompt,
            model_name=KEYWORD_MODEL
        )

        if not isinstance(result, str):
            result = ""

        result = result.lower().strip()

        print(
            f"[Intent Raw] {result}"
        )

        # ==================================================
        # Final Intent
        # ==================================================
        #
        # Gemini 理論上只會回傳：
        # recommend / chat
        #
        # 這裡仍保留 fallback，
        # 避免 AI 回傳空值或奇怪內容。
        #

        if result == "chat":
            print("[Intent] chat")
            return "chat"

        if result == "recommend":
            print("[Intent] recommend")
            return "recommend"

        # --------------------------------------------------
        # 保留原本較寬鬆的相容處理
        # --------------------------------------------------

        if "chat" in result:
            print("[Intent] chat")
            return "chat"

        print("[Intent] recommend")
        return "recommend"

    except Exception as e:

        print(
            f"[Intent Error] {e}"
        )

        # 與原本版本保持一致：
        # Intent 判斷失敗時，
        # 預設進入推薦流程。
        return "recommend"