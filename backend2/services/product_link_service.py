#product_link_service.py
"""
Product Link Service

負責：

1. 取得 Google Immersive Product 詳細資料
2. 解析商品的電商 Store Offers
3. 過濾無效 / Google 中介連結
4. 依電商優先順序選擇主要商品 Link
"""

import os

import requests
from dotenv import load_dotenv


load_dotenv()


# ==================================================
# Config
# ==================================================

DEBUG_LINK = True

SEARCH_TIMEOUT = 30

SERPAPI_KEY = os.getenv(
    "SERPAPI_KEY"
)


# ==================================================
# Taiwan Store Priority
# ==================================================

TAIWAN_STORE_PRIORITY = [
    "momo購物網",
    "PChome 24h購物",
    "蝦皮購物",
    "Yahoo奇摩購物中心",
    "酷澎",
    "Apple",
]


# ==================================================
# Link Validation
# ==================================================

def is_valid_store_link(link):
    """
    檢查是否為可以提供給前端的有效電商 Link。
    """

    if not link:
        return False

    link = str(link).strip()

    if not link:
        return False

    lower_link = link.lower()

    # =========================
    # Google 中介 / 搜尋 Link
    # =========================

    if "google.com/search" in lower_link:
        return False

    if "google.com/shopping" in lower_link:
        return False

    if "googleadservices.com" in lower_link:
        return False

    # =========================
    # URL Format
    # =========================

    return (
        lower_link.startswith("http://")
        or
        lower_link.startswith("https://")
    )


# ==================================================
# Extract Store Offers
# ==================================================

def extract_store_offers(stores):
    """
    將 Immersive Product 的 stores
    轉換成 WearWise Offer 格式。

    只保留有效電商 Link。
    """

    offers = []

    if not stores:
        return offers

    for store in stores:

        if not isinstance(store, dict):
            continue

        # =========================
        # Store
        # =========================

        name = store.get(
            "name",
            ""
        )

        # =========================
        # Link
        # =========================

        link = store.get(
            "link",
            ""
        )

        if not is_valid_store_link(link):
            continue

        # =========================
        # Price
        # =========================

        price = store.get(
            "extracted_price"
        )

        if price is None:

            price = store.get(
                "price",
                ""
            )

        # =========================
        # Offer
        # =========================

        offers.append({

            "store": name,

            "title": store.get(
                "title",
                ""
            ),

            "price": price,

            "currency": store.get(
                "currency",
                ""
            ),

            "rating": store.get(
                "rating",
                0
            ),

            "reviews": store.get(
                "reviews",
                0
            ),

            "link": link,
        })

    return offers


# ==================================================
# Select Store Link
# ==================================================

def select_store_link(
    stores,
    preferred_store=None,
):
    """
    從 Store Offers 中選擇主要商品 Link。

    優先順序：

    1. 使用指定 preferred_store
    2. 台灣電商優先順序
    3. 第一個有效 Link
    """

    if not stores:
        return ""

    # ==================================================
    # 1. Preferred Store
    # ==================================================

    if preferred_store:

        preferred_text = str(
            preferred_store
        ).strip().lower()

        if preferred_text:

            for store in stores:

                if not isinstance(
                    store,
                    dict,
                ):
                    continue

                name = str(
                    store.get(
                        "name",
                        "",
                    )
                ).strip().lower()

                if (
                    preferred_text
                    in name
                ):

                    link = store.get(
                        "link",
                        "",
                    )

                    if is_valid_store_link(
                        link
                    ):
                        return link

    # ==================================================
    # 2. Taiwan Store Priority
    # ==================================================

    for preferred_name in (
        TAIWAN_STORE_PRIORITY
    ):

        preferred_text = (
            preferred_name.lower()
        )

        for store in stores:

            if not isinstance(
                store,
                dict,
            ):
                continue

            name = str(
                store.get(
                    "name",
                    "",
                )
            ).strip().lower()

            if (
                preferred_text
                in name
            ):

                link = store.get(
                    "link",
                    "",
                )

                if is_valid_store_link(
                    link
                ):
                    return link

    # ==================================================
    # 3. First Valid Link
    # ==================================================

    for store in stores:

        if not isinstance(
            store,
            dict,
        ):
            continue

        link = store.get(
            "link",
            "",
        )

        if is_valid_store_link(
            link
        ):
            return link

    return ""


# ==================================================
# Fetch Immersive Product
# ==================================================

def fetch_immersive_product(
    api_url,
    preferred_store=None,
):
    """
    取得單一商品的
    Google Immersive Product 詳細資料。

    回傳：
        主要電商商品 Link

    如果取得失敗：
        回傳 ""
    """

    if not api_url:
        return ""

    try:

        # =========================
        # API Request
        # =========================

        response = requests.get(
            api_url,
            params={
                "api_key": SERPAPI_KEY,
            },
            timeout=SEARCH_TIMEOUT,
        )

        response.raise_for_status()

        data = response.json()

        # =========================
        # Product Results
        # =========================

        product_results = data.get(
            "product_results",
            {},
        )

        if not isinstance(
            product_results,
            dict,
        ):
            return ""

        # =========================
        # Stores
        # =========================

        stores = product_results.get(
            "stores",
            [],
        )

        if not isinstance(
            stores,
            list,
        ):
            stores = []

        # =========================
        # Extract Offers
        # =========================

        offers = extract_store_offers(
            stores
        )

        if DEBUG_LINK:

            print(
                "\n========== Product Link =========="
            )

            print(
                "Store Count:",
                len(stores),
            )

            print(
                "Valid Offers:",
                len(offers),
            )

        # =========================
        # Select Link
        # =========================

        link = select_store_link(
            stores,
            preferred_store=preferred_store,
        )

        if DEBUG_LINK:

            print(
                "Preferred Store:",
                preferred_store or "",
            )

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

    except ValueError as e:

        print(
            f"[Product Link JSON Error] {e}"
        )

        return ""

    except Exception as e:

        print(
            f"[Product Link Unexpected Error] {e}"
        )

        return ""