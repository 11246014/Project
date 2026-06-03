from services.ai_service import ask_ai


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

請只回：

score: 分數
reason: 原因

"""

    try:

        response = ask_ai(prompt)

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