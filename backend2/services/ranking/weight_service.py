# services/ranking/weight_service.py

"""
Weight Service

負責：
1. 基礎權重設定
2. Feature Bonus
3. Dynamic Weight 計算
"""

# ==================================================
# Base Weight
# ==================================================

BASE_SCORE = {
    "device": 20,
    "usage": 15,
    "feature": 20,
    "priority": 10,
    "budget": 10,
    "brand": 15,
    "os": 25,
    "rating": 1,
}

# ==================================================
# Feature Bonus
# ==================================================

FEATURE_BONUS = {
    "GPS": 15,
    "睡眠": 15,
    "血氧": 18,
    "ECG": 20,
    "防水": 10,
    "心率": 12,

    "battery_life": 20,
    "location_accuracy": 20,
    "durability": 18,
    "value": 15,
}

# ==================================================
# Dynamic Weight
# ==================================================

def build_dynamic_weights(need):
    """
    根據使用者需求動態調整各項權重。
    """

    weights = BASE_SCORE.copy()

    # ==================================================
    # Usage
    # ==================================================

    if getattr(need, "usage", None):
        weights["usage"] = 25

    # ==================================================
    # Feature
    # ==================================================

    if getattr(need, "features", None):
        weights["feature"] = 35

    # ==================================================
    # Priority
    # ==================================================

    if getattr(need, "priorities", None):
        weights["priority"] = 20

    # ==================================================
    # Brand
    # ==================================================

    if (
        getattr(need, "preferences", None)
        and getattr(need.preferences, "brand", None)
    ):
        weights["brand"] = 20

    # ==================================================
    # OS
    # ==================================================

    if (
        getattr(need, "preferences", None)
        and getattr(need.preferences, "os", None)
        and need.preferences.os != "Cross"
    ):
        weights["os"] = 20

    # ==================================================
    # Budget
    # ==================================================

    if (
        getattr(need, "budget", None)
        and getattr(need.budget, "max", None)
    ):
        weights["budget"] = 15

    return weights