from services.ollama_service import ask_ollama
from config.settings import KEYWORD_MODEL


def detect_intent(message):

    prompt = f"""
請判斷使用者訊息。

使用者：
{message}

規則：

如果是在尋找商品、
比較商品、
推薦商品、
詢問智慧手錶、
智慧手環、
穿戴裝置

回答：

recommend

如果是一般聊天、
問候、
詢問系統功能、
閒聊

回答：

chat

只能回答：
recommend
或
chat
"""

    try:

        result = ask_ollama(
            prompt,
            model_name=KEYWORD_MODEL
        )

        result = result.lower().strip()

        print(
            f"[Intent Raw] {result}"
        )

        if "chat" in result:

            return "chat"

        return "recommend"

    except Exception as e:

        print(
            f"[Intent Error] {e}"
        )

        return "recommend"