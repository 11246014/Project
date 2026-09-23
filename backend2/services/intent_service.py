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
請判斷使用者訊息屬於哪一類。

{conversation_context}

使用者：
{message}

規則：

如果使用者正在討論、尋找、購買、比較或推薦商品，
回答：

recommend

例如：
- 我想買一支智慧手錶
- 幫我找智慧手環
- 有推薦的 Garmin 嗎？
- 我想找適合睡眠的穿戴裝置
- 哪一支智慧手錶比較好？
- 幫我推薦適合運動的手錶

注意：

只要和商品、購買或推薦需求有關，
就回答 recommend。

即使使用者目前只提供很少的需求，
也仍然回答 recommend。

「需求是否完整」不是這個分類的工作，
不要因為需求不完整而回答 chat。

如果目前正在進行商品推薦需求確認，
使用者是在回答前一個需求問題，
也回答 recommend。

如果是一般聊天、問候、閒聊，
或詢問系統功能，
且沒有商品或購買需求，

回答：

chat

例如：
- 你好
- 你好嗎？
- 今天天氣如何？
- 你可以做什麼？
- 謝謝你
- 我只是想跟你聊天

只能回答：

recommend

或

chat

不要輸出其他文字。
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