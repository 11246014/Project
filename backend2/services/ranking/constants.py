# services/ranking/constants.py

"""
Ranking Constants

負責：
1. Query Mapping
2. Device / Usage / Feature 關鍵字
3. 推薦理由 Mapping
4. Priority 關鍵字
"""

# ==================================================
# Query Mapping
# ==================================================

DEVICE_QUERY_TERMS = {
    "smartwatch": "智慧手錶",
    "smart_band": "智慧手環",
    "smart_ring": "智慧戒指",
    "earbuds": "藍牙耳機",
}

USAGE_QUERY_TERMS = {
    "running": "跑步",
    "hiking": "登山",
    "health_monitoring": "健康",
    "sleep": "睡眠",

    "日常": "",
    "商務": "",
    "戶外": "",
    "運動": "運動",
    "健康": "健康",
}

FEATURE_QUERY_TERMS = {
    "gps": "GPS",
    "heart_rate": "心率",
    "blood_oxygen": "血氧",
    "ecg": "ECG",
    "sleep_tracking": "睡眠",
    "睡眠監測": "睡眠",
    "water_resistance": "防水",
}

# ==================================================
# Device Keywords
# ==================================================

DEVICE_KEYWORDS = {

    "smartwatch": [
        "智慧手錶",
        "智慧腕錶",
        "watch",
        "smartwatch",
        "apple watch",
        "galaxy watch",
        "pixel watch",
        "ticwatch",
        "garmin",
        "forerunner",
        "fenix",
        "instinct",
        "venu",
        "vivoactive",
        "amazfit",
        "huawei watch",
        "xiaomi watch",
        "mi watch",
    ],

    "smart_band": [
        "智慧手環",
        "手環",
        "band",
        "smart band",
        "mi band",
        "xiaomi band",
        "huawei band",
        "galaxy fit",
        "fit",
        "fit3",
        "vivosmart",
        "fitbit inspire",
    ],

    "smart_ring": [
        "智慧戒指",
        "戒指",
        "指環",
        "smart ring",
        "ring",
        "oura",
        "ringconn",
    ],

    "earbuds": [
        "藍牙耳機",
        "airpods",
        "galaxy buds",
        "buds",
        "earbuds",
    ],
}

# ==================================================
# Usage Keywords
# ==================================================

USAGE_KEYWORDS = {

    "running": [
        "跑步",
        "跑錶",
        "forerunner",
        "runner",
    ],

    "hiking": [
        "登山",
        "戶外",
        "hiking",
        "instinct",
        "fenix",
    ],

    "health_monitoring": [
        "健康",
        "健康監測",
        "health",
    ],

    "sleep": [
        "睡眠",
        "sleep",
    ],

    "運動": [
        "運動",
        "跑步",
        "forerunner",
    ],

    "健康": [
        "健康",
        "心率",
        "血氧",
    ],
}

USAGE_REASON = {
    "running": "適合跑步訓練",
    "hiking": "適合登山健行",
    "health_monitoring": "適合健康監測",
    "sleep": "適合睡眠監測",
    "運動": "適合運動",
    "健康": "適合健康管理",
}

# ==================================================
# Feature Keywords
# ==================================================

FEATURE_KEYWORDS = {

    "GPS": [
        "gps",
        "定位",
        "導航",
        "衛星",
    ],

    "睡眠": [
        "睡眠",
        "sleep",
    ],

    "血氧": [
        "血氧",
        "spo2",
    ],

    "ECG": [
        "ecg",
        "心電圖",
    ],

    "防水": [
        "防水",
        "ip68",
        "5atm",
    ],

    "心率": [
        "心率",
        "heart rate",
    ],
}

FEATURE_REASON = {
    "GPS": "支援GPS定位",
    "睡眠": "具備睡眠監測",
    "血氧": "支援血氧偵測",
    "ECG": "具備ECG心電圖功能",
    "心率": "提供心率監測",
    "防水": "具備防水功能",
}

# ==================================================
# Priority Keywords
# ==================================================

CORE_FACTOR_KEYWORDS = {

    "battery_life": [
        "續航",
        "長續航",
        "電池",
    ],

    "location_accuracy": [
        "gps",
        "定位",
        "高精度",
        "精準",
        "感測",
    ],

    "durability": [
        "軍規",
        "防摔",
        "耐用",
    ],

    "value": [
        "cp值",
        "超值",
    ],
}

PRIORITY_EVIDENCE_TERMS = {

    "battery_life": [
        "長續航",
        "強勢續航",
        "超高續航",
        "續航",
        "solar",
        "太陽能",
    ],

    "location_accuracy": [
        "gps",
        "gps定位",
        "定位",
    ],

    "durability": [
        "耐用",
        "堅固",
        "軍規",
        "防摔",
    ],

    "ease_of_use": [
        "操作簡單",
        "簡單操作",
        "容易使用",
        "易用",
    ],
}