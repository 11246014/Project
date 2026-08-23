# mock_data.py
#
# 開發期測試用假資料。
#
# ============================================================
# 為什麼改成「原始事件列表」而不是「算好的統計字典」？
# ------------------------------------------------------------
# 舊版的 MOCK_SUMMARY 是「已經算好的總和數字」，
# 側邊欄的來源篩選（chat / filter）跟日期範圍選了都一樣，
# 因為畫面根本沒有原始資料可以重新計算。
#
# 改成 MOCK_EVENTS（一筆一筆的原始事件，模擬 recommendation_events
# 資料表的每一列）之後，畫面上所有統計數字都是「即時算出來的」，
# 篩選來源、篩選日期範圍才會真的影響圖表結果。
#
# 之後接後端1的真實資料時，建議後端1不用自己寫 GROUP BY 統計，
# 只要開一支「回傳原始事件列表」的 API（例如 GET /analytics/events），
# 把 recommendation_events 資料表整包（去識別化後）回傳成這種格式即可，
# 統計邏輯完全交給這邊的 pandas 處理，後端1的工作量會小很多。
# ============================================================

import random
from datetime import datetime, timedelta

# 合作品牌名單（對照 sponsored_brands 資料表，is_active = true 的品牌）
SPONSORED_BRANDS = ["Garmin", "Amazfit"]

# ------------------------------------------------------------
# 各欄位的選項，皆對齊 FilterScreen 問卷實際文字
# ------------------------------------------------------------

# 第1題：使用情境（可複選）
USAGE_OPTIONS = [
    "運動（跑步 / 健身 / 戶外）",
    "日常生活（看時間 / 通知）",
    "工作 / 商務（訊息 / 行事曆）",
    "健康管理（心率 / 睡眠）",
    "穿搭 / 外型",
]

# 第2題：功能需求（可複選）
FEATURE_OPTIONS = [
    "GPS", "心率監測", "血氧", "ECG", "睡眠追蹤",
    "運動分析", "通知", "通話功能", "行動支付", "防水需求",
]

# 第4題：預算（單選）
BUDGET_OPTIONS = [
    "NT$1,000–5,000",
    "NT$5,000–15,000",
    "NT$15,000–30,000",
    "NT$30,000以上",
]

# 第5題：作業系統（單選）
OS_OPTIONS = ["iOS", "Android", "跨平台（皆可）"]

# 第6題：裝置類型（單選）
DEVICE_OPTIONS = ["手錶", "手環", "戒指", "其他"]

# 第9題：使用情境定位（選填，可能為空）
USAGE_SCOPE_OPTIONS = ["個人使用", "家庭共用", "要送禮", ""]

# 年齡層（對齊個人資訊欄位）
AGE_RANGE_OPTIONS = ["18歲以下", "19–25歲", "26–35歲", "36–45歲", "46–55歲", "56歲以上"]

# 推薦結果中，第1名商品的品牌／平台（用來驗證合作加權效果）
BRAND_OPTIONS = ["Garmin", "Apple", "Amazfit", "Xiaomi", "Samsung"]
PLATFORM_OPTIONS = ["momo", "蝦皮", "PChome", "Yahoo購物"]

# 事件來源
SOURCE_OPTIONS = ["filter", "chat"]


def _weighted_choice(options, weights, k=1):
    """依權重隨機抽樣，權重讓資料分布看起來更真實（有明顯的熱門選項）"""
    return random.choices(options, weights=weights, k=k)


def generate_mock_events(n: int = 180, days: int = 30, seed: int = 42) -> list[dict]:
    """
    產生 n 筆模擬的 recommendation_events 資料列。

    每一列代表「一次推薦事件」，欄位對齊資料庫實際規劃的欄位名稱：
    created_at / source / usage / features / device_type / budget_bucket /
    os / age_range / usage_scope / top_brand / top_platform
    """
    random.seed(seed)
    events = []
    now = datetime.now()

    for _ in range(n):
        # 日期均勻分布在最近 `days` 天內，讓「日期範圍篩選」有意義
        created_at = now - timedelta(
            days=random.randint(0, days - 1),
            hours=random.randint(0, 23),
        )

        # 使用情境：複選 1~2 個，運動/健康管理權重較高
        usage_picks = _weighted_choice(
            USAGE_OPTIONS, weights=[35, 20, 15, 25, 10],
            k=random.choice([1, 1, 2]),
        )
        usage_picks = list(dict.fromkeys(usage_picks))  # 去重複

        # 功能需求：複選 1~3 個，GPS/睡眠/防水權重較高
        feature_picks = _weighted_choice(
            FEATURE_OPTIONS,
            weights=[22, 16, 14, 8, 18, 10, 8, 5, 4, 15],
            k=random.choice([1, 2, 2, 3]),
        )
        feature_picks = list(dict.fromkeys(feature_picks))

        events.append({
            "created_at": created_at.strftime("%Y-%m-%d"),
            "source": _weighted_choice(SOURCE_OPTIONS, weights=[63, 37])[0],
            "usage": ",".join(usage_picks),
            "features": ",".join(feature_picks),
            "device_type": _weighted_choice(DEVICE_OPTIONS, weights=[55, 35, 8, 2])[0],
            "budget_bucket": _weighted_choice(BUDGET_OPTIONS, weights=[16, 44, 30, 10])[0],
            "os": _weighted_choice(OS_OPTIONS, weights=[46, 48, 6])[0],
            "age_range": _weighted_choice(AGE_RANGE_OPTIONS, weights=[3, 32, 40, 16, 6, 3])[0],
            "usage_scope": _weighted_choice(USAGE_SCOPE_OPTIONS, weights=[55, 15, 10, 20])[0],
            # 合作品牌權重稍微提高，模擬加權後曝光變多的效果
            "top_brand": _weighted_choice(
                BRAND_OPTIONS, weights=[26, 24, 20, 18, 12]
            )[0],
            "top_platform": _weighted_choice(
                PLATFORM_OPTIONS, weights=[37, 26, 23, 14]
            )[0],
        })

    return events


# 對外匯出：一份固定隨機種子產生的假資料，每次執行結果一致方便展示與除錯
MOCK_EVENTS = generate_mock_events()
