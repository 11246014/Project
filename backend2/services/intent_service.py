# intent_service.py

from services.ai_service import ask_ai
from config.settings import KEYWORD_MODEL


def detect_intent(message, in_recommendation=False):

    # =========================
    # Conversation Context
    # =========================

    conversation_context = ""

    if in_recommendation:

        conversation_context = """
目前這段對話已經進入「商品推薦需求確認」階段。

因此，如果使用者只是回答前一個問題，
例如：

- 睡眠
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

    # =========================
    # Intent Prompt
    # =========================

    prompt = f"""
你是 WearWise 的對話意圖判斷器。

你的任務只有一個：
判斷使用者目前的訊息屬於「商品推薦對話」還是「一般聊天」。

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

這些都屬於推薦需求的延續，因此回答：
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

即使使用者提供的需求還不完整，
仍然回答 recommend。

「需求是否完整」不是你的判斷工作。

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

    # =========================
    # AI Intent Detection
    # =========================

    try:

        result = ask_ai(
            prompt,
            model_name=KEYWORD_MODEL
        )

        result = result.lower().strip()

        print(
            f"[Intent Raw] {result}"
        )

        print(
            f"[Intent] "
            f"{'chat' if 'chat' in result else 'recommend'}"
        )

        # =========================
        # Final Intent
        # =========================

        if "chat" in result:

            return "chat"

        return "recommend"

    except Exception as e:

        print(
            f"[Intent Error] {e}"
        )

        return "recommend"