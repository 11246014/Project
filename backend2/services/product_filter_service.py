import re

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
    "Xiaomi",
    "Fitbit",
    "Huawei",
    "Amazfit",
    "Google",
    "OPPO",
    "realme",
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