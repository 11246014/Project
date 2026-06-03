import os

from openai import OpenAI

from dotenv import load_dotenv

load_dotenv()


client = OpenAI(

    api_key=os.getenv(
        "OPENAI_API_KEY"
    )
)


def ask_ai(prompt):

    try:

        response = client.chat.completions.create(

            model="gpt-4o-mini",

            messages=[

                {
                    "role": "system",

                    "content": (
                        "你是智慧穿戴商品推薦專家"
                    )
                },

                {
                    "role": "user",

                    "content": prompt
                }
            ],

            temperature=0.3
        )

        return response.choices[0].message.content

    except Exception as e:

        print(
            f"[AI Error] {e}"
        )

        return "AI 回應失敗"