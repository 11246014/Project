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
        "\u667a\u6167\u624b\u9336": "smartwatch",
        "\u624b\u9336": "smartwatch",
        "smart band": "smart_band",
        "smart_band": "smart_band",
        "band": "smart_band",
        "\u667a\u6167\u624b\u74b0": "smart_band",
        "\u624b\u74b0": "smart_band",
        "smart ring": "smart_ring",
        "smart_ring": "smart_ring",
        "ring": "smart_ring",
        "\u667a\u6167\u6212\u6307": "smart_ring",
        "\u6212\u6307": "smart_ring",
        "\u85cd\u7259\u8033\u6a5f": "earbuds",
        "earbuds": "earbuds",
    }

    return mapping.get(text, value)


def normalize_usage(value):
    text = _lower(value)

    if text is None:
        return None

    mapping = {
        "running": "running",
        "run": "running",
        "\u8dd1\u6b65": "running",
        "hiking": "hiking",
        "outdoor": "hiking",
        "\u767b\u5c71": "hiking",
        "\u6236\u5916": "hiking",
        "\u6236\u5916 / \u767b\u5c71": "hiking",
        "health": "health_monitoring",
        "health_monitoring": "health_monitoring",
        "\u5065\u5eb7": "health_monitoring",
        "\u5065\u5eb7\u76e3\u6e2c": "health_monitoring",
        "sleep": "sleep",
        "sleep_monitoring": "sleep",
        "sleep_tracking": "sleep",
        "\u7761\u7720": "sleep",
        "\u7761\u7720\u76e3\u6e2c": "sleep",
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
        "\u5fc3\u7387": "heart_rate",
        "blood_oxygen": "blood_oxygen",
        "spo2": "blood_oxygen",
        "\u8840\u6c27": "blood_oxygen",
        "ecg": "ecg",
        "\u5fc3\u96fb\u5716": "ecg",
        "sleep": "sleep_tracking",
        "sleep_tracking": "sleep_tracking",
        "\u7761\u7720": "sleep_tracking",
        "\u7761\u7720\u76e3\u6e2c": "sleep_tracking",
        "waterproof": "water_resistance",
        "water_resistance": "water_resistance",
        "\u9632\u6c34": "water_resistance",
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
        "\u4e0d\u9650": "Cross",
    }

    return mapping.get(text, value)


def normalize_style(value):
    text = _lower(value)

    if text is None:
        return None

    mapping = {
        "sport": "sport",
        "\u904b\u52d5": "sport",
        "fashion": "fashion",
        "\u6642\u5c1a": "fashion",
        "business": "business",
        "\u5546\u52d9": "business",
    }

    return mapping.get(text, value)


def normalize_battery(value):
    text = _lower(value)

    if text is None:
        return None

    if text in (
        "high",
        "\u9577\u7e8c\u822a",
        "\u7e8c\u822a",
        "\u7e8c\u822a\u4e45",
        "5 \u5230 7 \u5929\u4ee5\u4e0a",
    ):
        return "high"

    if text in ("medium", "2 \u5230 3 \u5929"):
        return "medium"

    if text in ("low",):
        return "low"

    return value


def normalize_priority(value):
    text = _lower(value)

    if text is None:
        return None

    mapping = {
        "battery_life": "battery_life",
        "\u7e8c\u822a": "battery_life",
        "\u9577\u7e8c\u822a": "battery_life",
        "location_accuracy": "location_accuracy",
        "\u5b9a\u4f4d\u7cbe\u6e96": "location_accuracy",
        "gps": "location_accuracy",
        "value": "value",
        "cp": "value",
        "cp\u503c": "value",
        "durability": "durability",
        "\u8010\u7528": "durability",
        "ease_of_use": "ease_of_use",
        "\u64cd\u4f5c\u7c21\u55ae": "ease_of_use",
    }

    return mapping.get(text, value)


def normalize_occupation(value):
    text = _lower(value)

    if text is None:
        return None

    mapping = {
        "student": "student",
        "\u5b78\u751f": "student",
        "office_worker": "office_worker",
        "\u4e0a\u73ed\u65cf": "office_worker",
        "athlete": "athlete",
        "\u904b\u52d5\u54e1": "athlete",
    }

    return mapping.get(text, value)


def normalize_age_group(value):
    text = _lower(value)

    if text is None:
        return None

    mapping = {
        "senior": "senior",
        "\u9577\u8005": "senior",
        "\u9577\u8f29": "senior",
        "adult": "adult",
        "\u6210\u4eba": "adult",
        "child": "child",
        "\u5152\u7ae5": "child",
    }

    return mapping.get(text, value)
