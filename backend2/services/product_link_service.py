import os

import requests
from dotenv import load_dotenv

load_dotenv()

DEBUG_LINK = True

SEARCH_TIMEOUT = 30

SERPAPI_KEY = os.getenv(
    "SERPAPI_KEY"
)

TAIWAN_STORE_PRIORITY = [
    "momo購物網",
    "PChome 24h購物",
    "蝦皮購物",
    "Yahoo奇摩購物中心",
    "酷澎",
    "Apple",
]


def is_valid_store_link(link):
    if not link:
        return False

    link = link.lower().strip()

    if "google.com/search" in link:
        return False

    if "google.com/shopping" in link:
        return False

    if "googleadservices.com" in link:
        return False

    return (
        link.startswith("http://")
        or
        link.startswith("https://")
    )


def extract_store_offers(stores):

    offers = []

    for store in stores:

        name = store.get(
            "name",
            ""
        )

        price = store.get(
            "price",
            ""
        )

        link = store.get(
            "link",
            ""
        )

        if not is_valid_store_link(link):
            continue

        offers.append({
            "store": name,
            "price": price,
            "link": link,
        })

    return offers


def select_store_link(
    stores,
    preferred_store=None,
):

    if not stores:
        return ""

    if preferred_store:

        for store in stores:

            name = store.get(
                "name",
                "",
            )

            if preferred_store.lower() in name.lower():

                link = store.get(
                    "link",
                    "",
                )

                if is_valid_store_link(link):
                    return link

    for preferred_name in TAIWAN_STORE_PRIORITY:

        for store in stores:

            name = store.get(
                "name",
                "",
            )

            if preferred_name.lower() in name.lower():

                link = store.get(
                    "link",
                    "",
                )

                if is_valid_store_link(link):
                    return link

    for store in stores:

        link = store.get(
            "link",
            "",
        )

        if is_valid_store_link(link):
            return link

    return ""

def fetch_immersive_product(
    api_url,
    preferred_store=None,
):
    """
    取得單一商品的
    Google Immersive Product 詳細資料，
    並選出有效的電商商品 Link。
    """

    if not api_url:
        return ""

    try:

        response = requests.get(
            api_url,
            params={
                "api_key": SERPAPI_KEY,
            },
            timeout=SEARCH_TIMEOUT,
        )

        response.raise_for_status()

        data = response.json()

        product_results = data.get(
            "product_results",
            {},
        )

        stores = product_results.get(
            "stores",
            [],
        )

        if DEBUG_LINK:

            print(
                "\n========== Product Link =========="
            )

            print(
                "Stores:",
                len(stores),
            )

        link = select_store_link(
            stores,
            preferred_store=preferred_store,
        )

        if DEBUG_LINK:

            print(
                "Selected Link:",
                link,
            )

            print(
                "=================================\n"
            )

        return link

    except requests.RequestException as e:

        print(
            f"[Product Link Error] {e}"
        )

        return ""