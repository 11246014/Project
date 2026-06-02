import httpx

BASE_URL = "https://champion-sandpit-rash.ngrok-free.dev/docs"


async def get_db_products():

    async with httpx.AsyncClient() as client:

        response = await client.get(
            f"{BASE_URL}/products"
        )

        return response.json()


async def save_product(product):

    async with httpx.AsyncClient() as client:

        response = await client.post(
            f"{BASE_URL}/products",
            json=product
        )

        return response.json()