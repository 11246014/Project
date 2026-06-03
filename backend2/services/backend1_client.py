import requests

BASE_URL = "https://champion-sandpit-rash.ngrok-free.dev"


async def save_product(product):

    try:

        payload = {

            "name": product.get(
                "title",
                ""
            ),

            "price": product.get(
                "price",
                0
            ),

            "description": product.get(
                "desc",
                ""
            ),

            "platform": product.get(
                "platform",
                ""
            ),

            "image": product.get(
                "image",
                ""
            ),

            "rating": int(
                product.get(
                    "rating",
                    0
                )
            ),

            "reason": product.get(
                "reason",
                ""
            )
        }

        response = requests.post(

            f"{BASE_URL}/products",

            json=payload,

            timeout=10
        )

        print(
            f"[Save Product] {response.status_code}"
        )

        print(response.text)

    except Exception as e:

        print(
            f"[Save Error] {e}"
        )