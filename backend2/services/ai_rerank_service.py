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

1. 禁止推測商品規格
2. 禁止推測 GPS
3. 禁止推測 心率
4. 禁止推測 血氧
5. 禁止推測 ECG
6. 禁止推測 睡眠監測
7. 只能根據商品名稱、商品描述、價格評分
8. 若商品資料未提及功能，不可自行補充
9. 評分依據應以名稱與描述出現的資訊為準
10. 不可根據品牌知名度加分
11. 不可自行推測續航力
12. 不可自行推測運動模式數量
13. 不可自行推測健康監測能力

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