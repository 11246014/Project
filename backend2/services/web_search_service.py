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
# 配件 / 非手錶黑名單
# =========================

BAD_KEYWORDS = [

    "錶帶",
    "表帶",
    "皮帶",
    "皮带",

    "保護貼",
    "保護殼",

    "充電線",
    "充電器",

    "配件",
    "替換帶",
    "腕帶",

    "手機殼",
    "耳機殼",

    "臂帶",
    "胸帶",
    "感測器",

    "襪子",
    "鞋子"
]

# =========================
# 穿戴裝置白名單
# =========================

WEARABLE_KEYWORDS = [

    "智慧手錶",
    "智慧手環",
    "智慧腕錶",

    "智能手錶",
    "智能手表",

    "運動手錶",

    "smartwatch",

    "watch",

    "watch fit",

    "galaxy watch",

    "apple watch",

    "garmin",

    "amazfit",

    "fitbit",

    "huawei",

    "xiaomi watch",

    "mi watch",

    "穿戴",

    "腕錶"
]

# =========================
# 智慧手錶強化白名單
# =========================

SMARTWATCH_KEYWORDS = [

    "智慧手錶",

    "智能手錶",

    "智慧腕錶",

    "smartwatch",

    "watch",

    "watch fit",

    "galaxy watch",

    "apple watch",

    "garmin",

    "huawei watch",

    "xiaomi watch"
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
# 商品名稱清理
# =========================

def clean_title(title):

    if not title:
        return ""

    cleaned = str(title)

    patterns = [

        r"\[.*?\]",
        r"【.*?】",
        r"\(.*?回饋.*?\)",

        r"\d+號前最高回饋\$?\d*",
        r"最高回饋\$?\d*",

        r"限時優惠",
        r"官方旗艦館",
        r"蝦皮直送",
        r"快速出貨",
        r"現貨",
        r"買一送一",
        r"熱銷推薦",
        r"優惠到",
        r"超值優惠",
        r"免運",

        r"聖誕禮物",
        r"交換禮物",
    ]

    for pattern in patterns:

        cleaned = re.sub(

            pattern,

            "",

            cleaned,

            flags=re.IGNORECASE
        )

    if "(" in cleaned:

        cleaned = cleaned.split("(")[0]

    if "（" in cleaned:

        cleaned = cleaned.split("（")[0]

    cleaned = re.sub(

        r"([a-z])([A-Z])",

        r"\1 \2",

        cleaned
    )

    cleaned = re.sub(

        r"[A-Z0-9\-]{12,}",

        "",

        cleaned
    )

    words = cleaned.split()

    filtered_words = []

    for word in words:

        if (
            len(word) >= 15
            and re.search(r"[A-Z]", word)
            and re.search(r"\d", word)
        ):

            continue

        filtered_words.append(word)

    cleaned = " ".join(filtered_words)

    replacements = {

        "智慧型手錶": "智慧手錶",
        "智能手表": "智慧手錶",
        "智能手錶": "智慧手錶",
        "智慧腕錶": "智慧手錶",
    }

    for old, new in replacements.items():

        cleaned = cleaned.replace(
            old,
            new
        )

    cleaned = re.sub(

        r"\s+",

        " ",

        cleaned
    )

    cleaned = cleaned.strip()

    return cleaned


# =========================
# 品牌偵測
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
# 商品資料清理
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

    # =========================
    # 黑名單過濾
    # =========================

    for word in BAD_KEYWORDS:

        if word.lower() in clean_name.lower():

            print(
                f"[Filtered] {clean_name}"
            )

            return None

    # =========================
    # 穿戴裝置過濾
    # =========================

    title_lower = clean_name.lower()

    is_wearable = any(

        keyword.lower() in title_lower

        for keyword in WEARABLE_KEYWORDS
    )

    smartwatch_match = any(

        keyword.lower() in title_lower

        for keyword in SMARTWATCH_KEYWORDS
    )

    if not is_wearable and not smartwatch_match:

        print(
            f"[Not Wearable] {clean_name}"
        )

        return None

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
# 品牌去重
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

        if brand == "Other":

            brand_products[
                f"Other_{len(brand_products)}"
            ] = product

        elif brand not in brand_products:

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
# Web Search
# =========================

def web_search_products(
    keyword
):

    print("=" * 50)

    print(
        f"[Web Search] {keyword}"
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

        response = requests.get(

            url,

            params=params,

            timeout=30
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

            if not product:

                continue

            print(
                "Clean Title:",
                product["title"]
            )

            print(
                "Clean Price:",
                product["price"]
            )

            if product["price"] > 30000:

                continue

            if not product["title"]:

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

        products.sort(

            key=lambda x: x["rating"],

            reverse=True
        )

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