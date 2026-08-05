#product_filter_service.py
import re
DEBUG_SEARCH = False

# =========================
# Product Filter Config
# =========================

TITLE_REMOVE_PATTERNS = [

    r"\[.*?\]",
    r"【.*?】",
    r"\d+號前最高回饋\$?\d*",
    r"\d+/\d+前最高回饋\d*萬?",
    r"\d+/\d+前最高回饋\$?\d*",
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

FEATURE_KEYWORDS = {

    "gps": "GPS",
    "睡眠": "睡眠",
    "心率": "心率",
    "血氧": "血氧",
    "ecg": "ECG",
    "心電圖": "ECG",
}

KNOWN_BRANDS = [

    "Apple",
    "Samsung",
    "Garmin",
    "Huawei",
    "Google",
    "Amazfit",
    "Fitbit",
    "Xiaomi",

    "COROS",
    "Polar",
    "Suunto",

    "Oura",
    "RingConn",

    "OPPO",
    "realme",
]
SMART_BRANDS = [

    "Apple",
    "Samsung",
    "Garmin",
    "Huawei",
    "Amazfit",
    "Fitbit",
    "Google",
    "Xiaomi",
    "OPPO",
    "realme",
    "COROS",
    "Polar",
    "Suunto",
]
SMART_TITLE_KEYWORDS = [

    "智慧",
    "智能",

    "smart",

    "smartwatch",

    "wear os",
    "wearos",

    "智慧手錶",
    "智慧手環",
    "智慧戒指",

    "智能手錶",
    "智能手環",
    "智能戒指",
]
# =========================
# 配件 / 非手錶黑名單
# =========================

ACCESSORY_KEYWORDS = [

    # 錶帶
    "錶帶",
    "表帶",
    "腕帶",
    "替換帶",

    # 錶環
    "錶環",
    "表環",

    # 保護
    "保護貼",
    "保護殼",

    # 充電
    "充電器",
    "充電線",
    "充電座",

    # 配件
    "配件",
    "支架",
    "底座",

    # 手機
    "手機殼",
    "耳機殼",

    # 感測器
    "胸帶",
    "臂帶",
    "感測器",

    # 其他
    "吊飾",
    "掛繩",
    "貼紙",
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

    "腕錶",

    "手環",

    "智慧手環",

    "智能手環",

    "運動手環",

    "band",

    "xiaomi band",

    "mi band",

    "galaxy fit",

    "fit3",

    "fit 3",

    "huawei band",

    "smart band",

    "fit3",

    "fit 3",

    "galaxy fit3",
    
    "samsung fit",
    
    "戒指",

    "智慧戒指",

    "智能戒指",

    "指環",

    "智慧指環",

    "智能指環",

    "smart ring",

    "ring"
    
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
# Price
# =========================

def clean_price(price_text):

    if not price_text:
        return 0

    try:

        text = str(price_text)

        text = text.replace("$", "")
        text = text.replace("NT$", "")
        text = text.replace(",", "")

        return int(float(text))

    except (TypeError, ValueError):

        return 0

# =========================
# Price Parsing
# =========================

def parse_price(price_text):

    if not price_text:

        return {
            "price": 0,
            "currency": "",
            "display_price": ""
        }

    display_price = str(price_text).strip()

    text = display_price.upper()

    # 預設幣別
    currency = ""

    if "NT$" in text or "TWD" in text:

        currency = "TWD"

    elif "US$" in text or "USD" in text:

        currency = "USD"

    elif text.startswith("$"):

        # Google Shopping (US) 常見格式
        currency = "USD"

    # 保留數字
    number = re.sub(
        r"[^\d.]",
        "",
        text
    )

    try:

        price = int(float(number))

    except (TypeError, ValueError):

        price = 0

    return {

        "price": price,

        "currency": currency,

        "display_price": display_price
    }

# =========================
# Title
# =========================

def clean_title(title):

    if not title:

        return ""

    cleaned = str(title)

    for pattern in TITLE_REMOVE_PATTERNS:

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

    return cleaned.strip()
# =========================
# Brand
# =========================

def detect_brand(title):

    title_lower = title.lower()

    for brand in KNOWN_BRANDS:

        if brand.lower() in title_lower:

            return brand

    return "Other"


# =========================
# Recommendation Reason
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

    if rating >= 4.0:

        return (
            f"熱門選擇，"
            f"符合「{keyword}」使用情境"
        )

    return (
        f"符合「{keyword}」需求"
    )


# =========================
# Feature Extraction
# =========================

def extract_features(feature_text):

    feature_text = feature_text.lower()

    features = []

    for keyword, name in FEATURE_KEYWORDS.items():

        if keyword in feature_text:

            features.append(name)

    return features


# =========================
# Accessory Detection
# =========================

def is_accessory(title):

    title_lower = title.lower()

    for word in ACCESSORY_KEYWORDS:

        if word.lower() in title_lower:

            return True

    return False

# =========================
# Wearable Score
# =========================

def calculate_wearable_score(
    title,
    snippet=""
):

    score = 0

    title_lower = title.lower()

    # =========================
    # Brand Score
    # =========================

    for brand in SMART_BRANDS:

        if brand.lower() in title_lower:

            score += 2

    # =========================
    # Title Score
    # =========================

    for keyword in SMART_TITLE_KEYWORDS:

        if keyword.lower() in title_lower:

            score += 2

    return score

# =========================
# Wearable Detection
# =========================

def is_wearable_device(
    title,
    snippet=""
):

    score = calculate_wearable_score(
        title,
        snippet
    )
    title_lower = title.lower()

    is_wearable = any(

        word.lower() in title_lower

        for word in WEARABLE_KEYWORDS
    )

    smartwatch_match = any(

        word.lower() in title_lower

        for word in SMARTWATCH_KEYWORDS
    )

    return (
        is_wearable
        or
        smartwatch_match
    )

# =========================
# Product Clean
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

    except (TypeError, ValueError):

        rating = 0

    raw_title = item.get(
        "title",
        ""
    )

    snippet = item.get( 
        "snippet",
        ""
    )
    #debug1
    # print("\n========== Item Keys ==========")
    # print(item.keys())
    # print("================================")

    feature_text = (
        raw_title +
        " " +
        snippet
    ).lower()

    if DEBUG_SEARCH:

        print(
            "[Desc]",
            snippet
        )

    clean_name = clean_title(
        raw_title
    )

    # =========================
    # 黑名單
    # =========================

    matched = None

    for word in ACCESSORY_KEYWORDS:
        if word.lower() in clean_name.lower():
            matched = word
            break

    if matched:
        print(f"[Accessory] {matched} -> {clean_name}")
        return None

    # =========================
    # Feature Extraction
    # =========================

    features = extract_features(
        feature_text
    )
    #debug2
    # print("\n========== Feature ==========")
    # print("Title:", raw_title)
    # print("Snippet:", snippet)
    # print("Extract:", features)
    # print("=============================")

    #debug3
    raw_price = item.get("price", "0")

    price_info = parse_price(raw_price)

    print("[Raw Price]", raw_price)
    print("[Price Info]", price_info)

    return {

        "title": clean_name,

        "raw_title": raw_title,

        
        "price": price_info["price"],

        "currency": price_info["currency"],

        "display_price": price_info["display_price"],

        "platform": item.get(
            "source",
            ""
        ),

        "desc": snippet,

        "link": item.get(
            "product_link",
            ""
        ),

        "image": item.get(
            "thumbnail",
            ""
        ),

        "features": features,

        "tags": [],

        "rating": rating,

        "match": int(
            rating * 10
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