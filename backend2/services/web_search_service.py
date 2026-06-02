import os
import requests

from dotenv import load_dotenv

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")


def web_search_products(keyword):

    print(f"[Web Search] {keyword}")

    url = "https://serpapi.com/search"

    params = {
        "engine": "google_shopping",
        "q": keyword,
        "api_key": SERPAPI_KEY,
        "gl": "tw",
        "hl": "zh-tw"
    }

    response = requests.get(
        url,
        params=params
    )

    data = response.json()

    products = []

    for item in data.get(
        "shopping_results",
        []
    )[:5]:

        products.append({

            "title": item.get(
                "title",
                ""
            ),

            "price": item.get(
                "price",
                0
            ),

            "platform": item.get(
                "source",
                ""
            ),

            "desc": item.get(
                "snippet",
                ""
            ),

            "link": item.get(
                "link",
                ""
            ),

            "image": item.get(
                "thumbnail",
                ""
            ),

            "tags": [],

            "rating": item.get(
                "rating",
                0
            ),

            "match": 90,

            "reason": "符合搜尋需求",

            "isTop": False
        })

    print(f"[Web Search] 找到 {len(products)} 筆商品")

    return products