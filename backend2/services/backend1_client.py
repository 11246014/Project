import httpx

BASE_URL = "https://champion-sandpit-rash.ngrok-free.dev"


async def get_db_products():

    async with httpx.AsyncClient() as client:

        response = await client.get(
            f"{BASE_URL}/products"
        )

        return response.json()


async def save_product(product):

    payload = {

        "name": product.get(
            "title",
            ""
        ),

        "price": int(
            product.get(
                "price",
                0
            )
        ),

        "description": product.get(
            "desc",
            ""
        )
    }

    async with httpx.AsyncClient() as client:

        response = await client.post(
            f"{BASE_URL}/products",
            json=payload
        )

        return response.json()