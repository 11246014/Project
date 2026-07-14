from services.ai_service import ask_ai
from config.settings import KEYWORD_MODEL


def ai_rerank(
    filters,
    product
):

    prompt = f"""

你是智慧穿戴商品推薦專家。

使用者需求：

{filters}

商品資料：

商品名稱：
{product.get("title")}

商品描述：
{product.get("desc")}

價格：
{product.get("price")}

請評估：

1. 此商品是否符合使用者需求
2. 給 0~100 分
3. 說明原因

重要規則：

重要規則：

若商品名稱或描述沒有出現：

GPS
心率
血氧
ECG
睡眠監測
防水

則不得在 reason 中提及。

違反規則直接評分 0 分。

只能引用商品名稱與商品描述出現的文字。

請只回：

score: 分數
reason: 原因

"""

    try:

        response = ask_ai(
            prompt,
            model_name=KEYWORD_MODEL
        )

        print(
            "[AI Rerank]",
            response
        )

        score = 50

        lines = response.split("\n")

        for line in lines:

            if "score" in line.lower():

                numbers = "".join(

                    c for c in line

                    if c.isdigit()
                )

                if numbers:

                    score = int(numbers)

                    break

        score = max(
            0,
            min(
                score,
                100
            )
        )

        return {

            "score": score,

            "reason": response
        }

    except Exception as e:

        print(
            f"[AI Rerank Error] {e}"
        )

        return {

            "score": 50,

            "reason": "AI rerank failed"
        }