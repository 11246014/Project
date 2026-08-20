# vocabulary_normalizer.py


def _clean(value):

    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    return text


def _lower(value):

    text = _clean(value)

    if text is None:
        return None

    return text.lower()


def normalize_list(values, normalizer):

    if values is None or values == "":
        return []

    if not isinstance(values, list):
        values = [values]

    normalized = []

    for value in values:

        item = normalizer(value)

        if item and item not in normalized:
            normalized.append(item)

    return normalized


def normalize_device_type(value):

    text = _lower(value)

    if text is None:
        return None

    mapping = {

        "smartwatch": "smartwatch",
        "smart_watch": "smartwatch",
        "watch": "smartwatch",
        "智慧手錶": "smartwatch",
        "手錶": "smartwatch",

        "smart band": "smart_band",
        "smart_band": "smart_band",
        "band": "smart_band",
        "智慧手環": "smart_band",
        "手環": "smart_band",

        "smart ring": "smart_ring",
        "smart_ring": "smart_ring",
        "ring": "smart_ring",
        "智慧戒指": "smart_ring",
        "戒指": "smart_ring",

        "藍牙耳機": "earbuds",
        "earbuds": "earbuds",
    }

    return mapping.get(text, value)


def normalize_usage(value):

    text = _lower(value)

    if text is None:
        return None

    mapping = {

        # Running
        "running": "running",
        "run": "running",
        "跑步": "running",

        # Sport
        "運動": "運動",
        "運動（跑步 / 健身 / 戶外）": "運動",
        "運動（跑步/健身/戶外）": "運動",

        # Hiking / Outdoor
        "hiking": "hiking",
        "outdoor": "hiking",
        "登山": "hiking",
        "戶外": "hiking",
        "戶外 / 登山": "hiking",

        # Health
        "health": "health_monitoring",
        "health_monitoring": "health_monitoring",
        "健康": "health_monitoring",
        "健康監測": "health_monitoring",

        # Sleep
        "sleep": "sleep",
        "sleep_monitoring": "sleep",
        "sleep_tracking": "sleep",
        "睡眠": "sleep",
        "睡眠監測": "sleep",
    }

    return mapping.get(text, value)


def normalize_feature(value):

    text = _lower(value)

    if text is None:
        return None

    mapping = {

        "gps": "gps",

        "heart_rate": "heart_rate",
        "heart rate": "heart_rate",
        "心率": "heart_rate",

        "blood_oxygen": "blood_oxygen",
        "spo2": "blood_oxygen",
        "血氧": "blood_oxygen",

        "ecg": "ecg",
        "心電圖": "ecg",

        "sleep": "sleep_tracking",
        "sleep_tracking": "sleep_tracking",
        "睡眠": "sleep_tracking",
        "睡眠監測": "sleep_tracking",

        "waterproof": "water_resistance",
        "water_resistance": "water_resistance",
        "防水": "water_resistance",
    }

    return mapping.get(text, value)


def normalize_os(value):

    text = _lower(value)

    if text is None:
        return None

    mapping = {

        "ios": "iOS",
        "iphone": "iOS",

        "android": "Android",

        "cross": "Cross",
        "不限": "Cross",
    }

    return mapping.get(text, value)


def normalize_style(value):

    text = _lower(value)

    if text is None:
        return None

    mapping = {

        "sport": "sport",
        "運動": "sport",

        "fashion": "fashion",
        "時尚": "fashion",

        "business": "business",
        "商務": "business",
    }

    return mapping.get(text, value)


def normalize_battery(value):

    text = _lower(value)

    if text is None:
        return None

    if text in (
        "high",
        "長續航",
        "續航",
        "續航久",
        "5 到 7 天以上",
    ):
        return "high"

    if text in (
        "medium",
        "2 到 3 天",
    ):
        return "medium"

    if text in (
        "low",
    ):
        return "low"

    return value


def normalize_priority(value):

    text = _lower(value)

    if text is None:
        return None

    mapping = {

        "battery_life": "battery_life",
        "續航": "battery_life",
        "長續航": "battery_life",

        "location_accuracy": "location_accuracy",
        "定位精準": "location_accuracy",
        "gps": "location_accuracy",

        "value": "value",
        "cp": "value",
        "cp值": "value",

        "durability": "durability",
        "耐用": "durability",

        "ease_of_use": "ease_of_use",
        "操作簡單": "ease_of_use",
    }

    return mapping.get(text, value)


def normalize_occupation(value):

    text = _lower(value)

    if text is None:
        return None

    mapping = {

        "student": "student",
        "學生": "student",

        "office_worker": "office_worker",
        "上班族": "office_worker",

        "athlete": "athlete",
        "運動員": "athlete",
    }

    return mapping.get(text, value)


def normalize_age_group(value):

    text = _lower(value)

    if text is None:
        return None

    mapping = {

        "senior": "senior",
        "長者": "senior",
        "長輩": "senior",

        "adult": "adult",
        "成人": "adult",

        "child": "child",
        "兒童": "child",
    }

    return mapping.get(text, value)