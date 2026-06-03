import os
import re
import requests

from dotenv import load_dotenv

load_dotenv()

SERPAPI_KEY = os.getenv(
    "SERPAPI_KEY"
)

# =========================
# 已知品牌
# =========================

KNOWN_BRANDS = [

    "Apple",
    "Samsung",
    "Garmin",
    "Xiaomi",
    "Fitbit",
    "Huawei",
    "Amazfit",
    "Google",
    "OPPO",
    "realme"
]


# =========================
# 清理價格
# =========================

def clean_price(price_text):

    if not price_text:
        return 0

    try:

        text = str(price_text)

        text = text.replace(
            "$",
            ""
        )

        text = text.replace(
            "NT$",
            ""
        )

        text = text.replace(
            ",",
            ""
        )

        value = float(text)

        return int(value)

    except Exception:

        return 0


# =========================
# 清理商品名稱
# =========================

def clean_title(title):

    if not title:
        return ""

    patterns = [

        r"\d+號前最高回饋\$?\d+",
        r"滿額送.*?",
        r"限時優惠",
        r"官方旗艦館",
        r"免運",
        r"現貨",
        r"快速出貨",
        r"蝦皮直送",
        r"【.*?】",
        r"\(.*?回饋.*?\)",
    ]

    cleaned = title

    for pattern in patterns:

        cleaned = re.sub(
            pattern,
            "",
            cleaned
        )

    cleaned = " ".join(
        cleaned.split()
    )

    return cleaned.strip()


# =========================
# 偵測品牌
# =========================

def detect_brand(title):

    title_lower = title.lower()

    for brand in KNOWN_BRANDS:

        if brand.lower() in title_lower:

            return brand

    return "Other"


# =========================
# 推薦理由
# =========================

def generate_reason(
    keyword,
    rating
):

    if rating >= 4.5:

        return (
            f"高評價商品，"
            f"適合有「{keyword}」需求的使用者"
        )

    elif rating >= 4.0:

        return (
            f"熱門選擇，"
            f"符合「{keyword}」使用情境"
        )

    return f"符合「{keyword}」需求"


# =========================
# 清理商品資料
# =========================

def clean_product(
    item,
    keyword
):

    rating = item.get(
        "rating",
        0
    )

    try:

        rating = float(rating)

    except:

        rating = 0

    raw_title = item.get(
        "title",
        ""
    )

    clean_name = clean_title(
        raw_title
    )

    return {

        "title": clean_name,

        "price": clean_price(
            item.get(
                "price",
                "0"
            )
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

        "rating": rating,

        "match": int(
            rating * 20
        ),

        "reason": generate_reason(
            keyword,
            rating
        ),

        "brand": detect_brand(
            clean_name
        ),

        "isTop": False
    }


# =========================
# 品牌去重複
# =========================

def remove_duplicate_brand(
    products
):

    brand_products = {}

    for product in products:

        brand = product.get(
            "brand",
            "Other"
        )

        if brand not in brand_products:

            brand_products[
                brand
            ] = product

        else:

            old_rating = brand_products[
                brand
            ]["rating"]

            new_rating = product[
                "rating"
            ]

            if new_rating > old_rating:

                brand_products[
                    brand
                ] = product

    return list(
        brand_products.values()
    )


# =========================
# SerpAPI 商品搜尋
# =========================

def web_search_products(
    keyword
):

    print("=" * 50)

    print(
        f"[Web Search] {keyword}"
    )

    print(

        f"[SERPAPI_KEY Loaded] "
        f"{SERPAPI_KEY[:10]}..."

        if SERPAPI_KEY

        else "[SERPAPI_KEY NOT FOUND]"
    )

    url = (
        "https://serpapi.com/search"
    )

    params = {

        "engine": "google_shopping",

        "q": keyword,

        "api_key": SERPAPI_KEY,

        "gl": "tw",

        "hl": "zh-tw"
    }

    try:

        print(
            "[SerpAPI Request Start]"
        )

        response = requests.get(

            url,

            params=params,

            timeout=30
        )

        print(
            "[SerpAPI Response OK]"
        )

        print(
            f"[Status Code] "
            f"{response.status_code}"
        )

        print(
            "[Response Preview]"
        )

        print(
            response.text[:1000]
        )

        data = response.json()

        shopping_results = data.get(
            "shopping_results",
            []
        )

        print(
            f"[Shopping Results Count] "
            f"{len(shopping_results)}"
        )

        products = []

        for item in shopping_results[:10]:

            print("=" * 30)

            print(
                item.get("title")
            )

            print(
                item.get("price")
            )

            product = clean_product(
                item,
                keyword
            )

            print(
                "Clean Title:",
                product["title"]
            )

            print(
                "Clean Price:",
                product["price"]
            )

            # =========================
            # 過濾過高價格
            # =========================

            if product["price"] > 30000:

                print(
                    "Price Filtered"
                )

                continue

            # =========================
            # 過濾空商品名稱
            # =========================

            if not product["title"]:

                print(
                    "Empty Title Filtered"
                )

                continue

            products.append(
                product
            )

        print(
            f"[Before Dedup] "
            f"{len(products)}"
        )

        products = remove_duplicate_brand(
            products
        )

        print(
            f"[After Dedup] "
            f"{len(products)}"
        )

        # =========================
        # 評分排序
        # =========================

        products.sort(

            key=lambda x: x["rating"],

            reverse=True
        )

        # =========================
        # Top Product
        # =========================

        if products:

            products[0][
                "isTop"
            ] = True

            products[0][
                "match"
            ] = 98

        print(
            f"[Web Search] 找到 "
            f"{len(products)} 筆商品"
        )

        print("=" * 50)

        return products

    except Exception as e:

        print(
            f"[Web Search Error] {e}"
        )

        print("=" * 50)

        return []