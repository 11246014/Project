# mock_data.py
#
# 開發 / 展示用假資料（USE_MOCK_DATA = True 時使用）。
#
# ============================================================
# 設計重點
# ------------------------------------------------------------
# 1. 資料形狀完全對齊後端1 GET /analytics/events 的欄位：
#    created_at / source / age_range / occupation / usage_scope /
#    device_type / usage / features / os / brand_preference /
#    budget_min / budget_max / top_brands / top_platforms / product_count
#    → 之後切到真實資料，app.py 不用改任何統計程式。
#
# 2. 為了讓品牌分析「看得出差異」，品牌不是隨機亂抽，而是用一個
#    迷你「推薦分數引擎」依事件條件（作業系統、預算、使用情境、功能、
#    裝置、年齡）打分，再依分數抽出前 3 名；合作品牌（Garmin、Apple）
#    另外乘上贊助加權。因此：
#      - Apple 在 iOS 使用者身上特別強、Samsung 在 Android 上特別強（受眾指數）
#      - Garmin 吃運動 / GPS 需求、預算較高（需求對照、預算落點）
#      - Xiaomi 吃低預算與學生（預算帶落點）
#      - Amazfit（非合作品牌）近 60 天曝光逐步上升（份額趨勢）
#      - Ultrahuman 只在最近 8 天才開始出現（用來展示「新品牌自動加入側邊欄」）
#
# 3. 刻意重現真實資料的「不完美」，讓後台的防呆與正規化都有東西可驗：
#      - 問卷（filter）與對話（chat）兩種來源的欄位詞彙粒度不同
#        （chat 的 usage 會出現 running / sleep、device_type 會出現 smartwatch）
#      - 年齡層、職業、使用情境定位、作業系統可能為空
#      - 職業是 App 端自由輸入，同一職業有多種寫法（學生 / 大學生 / 研究生）
#      - 同品牌占兩個推薦名額（top_brands 重複）、少於 3 個品牌
#        （沒有品牌欄位的商品被略過）
#      - chat 來源有少數品牌寫法不一致（Apple Watch / 蘋果 / garmin）
#        → 用來驗證 app.py 的 BRAND_LABEL_MAP 與自動合併機制
#      - 跳過預算題時 budget_min=0、budget_max=999999
#
# 4. 使用固定亂數種子（random.Random(seed)），除了「相對今天的日期」會
#    隨執行日往後移動外，其餘每次結果一致，方便展示與除錯。
# ============================================================

import random
from datetime import datetime, timedelta

# 合作品牌名單（對照 sponsored_brands 資料表，is_active = true 的品牌）
SPONSORED_BRANDS = ["Garmin", "Apple"]

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

# 對話來源（chat）經 backend2 正規化後的簡短詞彙，對應上面 5 類
CHAT_USAGE_ALIASES = {
    USAGE_OPTIONS[0]: ["運動", "running", "hiking", "健身"],
    USAGE_OPTIONS[1]: ["日常", "通知", "看時間"],
    USAGE_OPTIONS[2]: ["商務", "工作", "business"],
    USAGE_OPTIONS[3]: ["health", "sleep", "健康", "睡眠"],
    USAGE_OPTIONS[4]: ["穿搭", "style"],
}

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

# 每個預算選項對應的實際數字區間，跟後端 budget_min/budget_max 一致
BUDGET_RANGES = {
    "NT$1,000–5,000": (1000, 5000),
    "NT$5,000–15,000": (5000, 15000),
    "NT$15,000–30,000": (15000, 30000),
    "NT$30,000以上": (30000, 60000),
}

# 年齡層（對齊個人資訊欄位）
AGE_RANGE_OPTIONS = ["18 歲以下", "19–25 歲", "26–35 歲", "36–45 歲", "46–55 歲", "56 歲以上"]

# 職業：App 端是「自由輸入」，所以假資料同一類職業刻意產生多種寫法，
# 讓 app.py 的 OCCUPATION_LABEL_MAP 歸類機制有東西可驗
OCCUPATION_RAW_OPTIONS = {
    "學生": ["學生", "大學生", "研究生", "高中生"],
    "上班族": ["上班族", "行政人員", "業務", "會計"],
    "工程師 / 科技業": ["工程師", "軟體工程師", "PM", "設計師"],
    "教育 / 醫療": ["教師", "老師", "護理師", "醫師"],
    "運動 / 健身": ["運動員", "教練", "健身教練"],
    "自由工作者": ["自由工作者", "接案", "自媒體"],
    "其他": ["家管", "退休", "軍警"],
}

# 事件來源
SOURCE_OPTIONS = ["filter", "chat"]

# 平台
PLATFORM_OPTIONS = ["momo", "蝦皮", "PChome", "Yahoo購物"]

# ------------------------------------------------------------
# 品牌特性表：每個品牌對事件條件的「親和度」（>1 加分、<1 扣分）
# 這就是上面說的「迷你推薦分數引擎」的參數。
# usage 的 key 對應 USAGE_OPTIONS 的索引（0 運動、1 日常、2 商務、3 健康、4 穿搭）；
# budget 四個數字依序對應 BUDGET_OPTIONS 四個級距。
# ------------------------------------------------------------
BRAND_PROFILES = {
    "Garmin": {
        "pop": 1.00, "sponsor": True,
        "os": {"iOS": 1.0, "Android": 1.0},
        "budget": [0.4, 1.0, 1.5, 1.2],
        "usage": {0: 2.0, 3: 1.1, 1: 0.6, 2: 0.6, 4: 0.4},
        "feature": {"GPS": 2.0, "運動分析": 1.8, "心率監測": 1.2, "防水需求": 1.3, "行動支付": 0.8},
        "device": {"手錶": 1.2, "手環": 0.5, "戒指": 0.05, "其他": 0.3},
        "age": {"26–35 歲": 1.3, "36–45 歲": 1.4, "19–25 歲": 0.8},
    },
    "Apple": {
        "pop": 1.00, "sponsor": True,
        "os": {"iOS": 2.6, "Android": 0.06},
        "budget": [0.2, 0.9, 1.5, 1.6],
        "usage": {1: 1.4, 2: 1.3, 4: 1.3, 0: 0.9, 3: 1.0},
        "feature": {"通話功能": 1.6, "行動支付": 1.8, "通知": 1.4, "ECG": 1.5, "血氧": 1.1},
        "device": {"手錶": 1.4, "手環": 0.3, "戒指": 0.05, "其他": 0.3},
        "age": {"19–25 歲": 1.2, "26–35 歲": 1.2},
    },
    "Amazfit": {
        "pop": 0.70, "sponsor": False,
        "os": {"iOS": 0.9, "Android": 1.2},
        "budget": [1.5, 1.8, 0.5, 0.15],
        "usage": {0: 1.4, 3: 1.2, 1: 1.0, 2: 0.7, 4: 0.7},
        "feature": {"睡眠追蹤": 1.4, "心率監測": 1.3, "運動分析": 1.3, "防水需求": 1.2, "GPS": 1.2},
        "device": {"手錶": 1.0, "手環": 1.4, "戒指": 0.05, "其他": 0.4},
        "age": {"19–25 歲": 1.3, "26–35 歲": 1.1},
        "trend": 1.1,                          # 近期曝光逐步上升
    },
    "Xiaomi": {
        "pop": 1.00, "sponsor": False,
        "os": {"iOS": 0.5, "Android": 1.5},
        "budget": [2.6, 1.1, 0.12, 0.03],
        "usage": {1: 1.3, 0: 1.0, 3: 0.9, 2: 0.7, 4: 0.8},
        "feature": {"睡眠追蹤": 1.3, "通知": 1.3, "防水需求": 1.1, "ECG": 0.2, "行動支付": 0.7},
        "device": {"手錶": 0.7, "手環": 2.2, "戒指": 0.05, "其他": 0.4},
        "age": {"18 歲以下": 1.6, "19–25 歲": 1.5, "46–55 歲": 0.7},
    },
    "Samsung": {
        "pop": 0.95, "sponsor": False,
        "os": {"iOS": 0.04, "Android": 2.2},
        "budget": [0.2, 1.1, 1.6, 1.0],
        "usage": {3: 1.5, 1: 1.2, 0: 1.0, 2: 1.0, 4: 1.0},
        "feature": {"ECG": 1.9, "血氧": 1.7, "心率監測": 1.4, "睡眠追蹤": 1.3, "通話功能": 1.2},
        "device": {"手錶": 1.5, "手環": 0.3, "戒指": 0.3, "其他": 0.3},
        "age": {"36–45 歲": 1.3, "46–55 歲": 1.3},
    },
    "Huawei": {
        "pop": 0.70, "sponsor": False,
        "os": {"iOS": 0.7, "Android": 1.3},
        "budget": [0.6, 1.4, 1.2, 0.5],
        "usage": {3: 1.6, 0: 1.1, 1: 0.9, 2: 0.9, 4: 0.8},
        "feature": {"心率監測": 1.6, "血氧": 1.5, "睡眠追蹤": 1.5, "運動分析": 1.1},
        "device": {"手錶": 1.1, "手環": 1.3, "戒指": 0.05, "其他": 0.3},
        "age": {"36–45 歲": 1.5, "46–55 歲": 1.6, "56 歲以上": 1.8},
    },
    "Fitbit": {
        "pop": 0.55, "sponsor": False,
        "os": {"iOS": 1.1, "Android": 1.0},
        "budget": [0.8, 1.5, 0.8, 0.2],
        "usage": {3: 1.6, 0: 1.1, 1: 1.0, 2: 0.7, 4: 0.6},
        "feature": {"睡眠追蹤": 1.7, "心率監測": 1.4, "運動分析": 1.0, "ECG": 0.7},
        "device": {"手錶": 0.8, "手環": 1.7, "戒指": 0.1, "其他": 0.3},
        "age": {"26–35 歲": 1.2, "36–45 歲": 1.2},
    },
    "Coros": {
        "pop": 0.40, "sponsor": False,
        "os": {"iOS": 1.0, "Android": 1.0},
        "budget": [0.1, 0.9, 1.7, 1.4],
        "usage": {0: 2.6, 3: 0.8, 1: 0.3, 2: 0.2, 4: 0.2},
        "feature": {"GPS": 2.2, "運動分析": 2.0, "防水需求": 1.4, "行動支付": 0.2, "通話功能": 0.1},
        "device": {"手錶": 1.4, "手環": 0.1, "戒指": 0.02, "其他": 0.1},
        "age": {"26–35 歲": 1.4, "36–45 歲": 1.2},
    },
    "Oura": {
        "pop": 0.35, "sponsor": False,
        "os": {"iOS": 1.3, "Android": 0.9},
        "budget": [0.05, 0.5, 1.6, 1.8],
        "usage": {3: 2.2, 4: 1.4, 0: 0.5, 1: 0.8, 2: 0.8},
        "feature": {"睡眠追蹤": 2.3, "心率監測": 1.3, "血氧": 1.2, "行動支付": 0.1},
        "device": {"手錶": 0.05, "手環": 0.05, "戒指": 8.0, "其他": 0.1},
        "age": {"26–35 歲": 1.4, "36–45 歲": 1.3},
    },
    # 新品牌：只在最近 8 天才開始出現，用來展示「側邊欄自動加入新品牌」
    "Ultrahuman": {
        "pop": 0.60, "sponsor": False, "only_last_days": 8,
        "os": {"iOS": 1.2, "Android": 1.0},
        "budget": [0.05, 0.6, 1.5, 1.6],
        "usage": {3: 2.0, 4: 1.5, 0: 0.7, 1: 0.8, 2: 0.8},
        "feature": {"睡眠追蹤": 2.0, "心率監測": 1.2, "血氧": 1.2},
        "device": {"手錶": 0.05, "手環": 0.05, "戒指": 8.0, "其他": 0.1},
        "age": {"26–35 歲": 1.4, "19–25 歲": 1.2},
    },
}

# 合作品牌推薦加權（模擬 Score Engine 對贊助品牌的加分）
SPONSOR_BOOST = 1.25

# chat 來源偶爾出現的品牌別名寫法（驗證 app.py 的 BRAND_LABEL_MAP）
CHAT_BRAND_VARIANTS = {
    "Apple": ["Apple Watch", "蘋果", "apple"],
    "Garmin": ["garmin", "佳明"],
    "Xiaomi": ["小米", "Mi Band"],
    "Samsung": ["三星", "Galaxy Watch"],
    "Huawei": ["華為"],
}


def _weighted_choice(rng, options, weights, k=1):
    """依權重隨機抽樣，權重讓資料分布看起來更真實（有明顯的熱門選項）"""
    return rng.choices(list(options), weights=weights, k=k)


def _pick_without_replacement(rng, names, weights, k):
    """依權重不放回抽 k 個（Plackett-Luce），用來模擬「依分數排名取前幾名」"""
    names, weights = list(names), list(weights)
    picked = []
    for _ in range(min(k, len(names))):
        choice = rng.choices(range(len(names)), weights=weights, k=1)[0]
        picked.append(names.pop(choice))
        weights.pop(choice)
    return picked


def _brand_scores(rng, ctx):
    """
    迷你推薦分數引擎：依事件條件替每個品牌打分。
    ctx 內含 os / budget_idx / usage_idx(list) / features(list) /
    device / age / progress(0=最舊,1=最新) / days_ago
    """
    scores = {}
    for name, prof in BRAND_PROFILES.items():
        # 新品牌：還沒上線的日期不會出現
        if prof.get("only_last_days") is not None and ctx["days_ago"] > prof["only_last_days"]:
            continue

        s = prof["pop"]
        # 作業系統：沒填就不加分也不扣分
        if ctx["os"] in prof["os"]:
            s *= prof["os"][ctx["os"]]
        # 預算：跳過預算題（None）時不影響
        if ctx["budget_idx"] is not None:
            s *= prof["budget"][ctx["budget_idx"]]
        # 使用情境：取多選的平均親和度
        if ctx["usage_idx"]:
            s *= sum(prof["usage"].get(i, 1.0) for i in ctx["usage_idx"]) / len(ctx["usage_idx"])
        # 功能需求：每個功能逐一連乘後開 0.7 次方，避免一次疊太多
        feat_mult = 1.0
        for f in ctx["features"]:
            feat_mult *= prof["feature"].get(f, 1.0)
        s *= feat_mult ** 0.7
        # 裝置類型
        if ctx["device"] in prof["device"]:
            s *= prof["device"][ctx["device"]]
        # 年齡
        s *= prof["age"].get(ctx["age"], 1.0)
        # 時間趨勢：Amazfit 越近越強
        if "trend" in prof:
            s *= 0.5 + 0.9 * ctx["progress"] * prof["trend"]
        # 贊助加權
        if prof["sponsor"]:
            s *= SPONSOR_BOOST
        # 加一點隨機雜訊，避免同條件永遠同排名
        s *= rng.uniform(0.75, 1.3)
        scores[name] = s
    return scores


def generate_mock_events(n: int = 600, days: int = 60, seed: int = 42) -> list[dict]:
    """
    產生 n 筆模擬的 recommendation_events 資料列（預設 600 筆、近 60 天）。

    筆數取 600 的原因：後台預設「最小樣本數 = 5」，品牌 × 年齡 × 職業
    這類交叉分組若只有 180 筆，大部分分組會被遮蔽成「樣本不足」，
    展示效果很差；600 筆能讓多數品牌的各項分析都有足夠樣本可看。
    """
    rng = random.Random(seed)
    events = []
    today = datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)

    # 日期權重：越近期事件越多（模擬使用者成長）、週末略多
    day_offsets = list(range(days))
    day_weights = []
    for off in day_offsets:
        weight = 1.0 + 1.4 * (1 - off / days)
        if (today - timedelta(days=off)).weekday() >= 5:
            weight *= 1.2
        day_weights.append(weight)

    for _ in range(n):
        days_ago = rng.choices(day_offsets, weights=day_weights, k=1)[0]
        created_at = today - timedelta(days=days_ago)
        progress = 1 - days_ago / days
        source = _weighted_choice(rng, SOURCE_OPTIONS, [65, 35])[0]
        is_chat = source == "chat"

        # ---- 年齡層與職業（職業與年齡相關；chat 來源較常缺值）----
        age = _weighted_choice(rng, AGE_RANGE_OPTIONS, [3, 33, 38, 16, 7, 3])[0]
        if age in ("18 歲以下", "19–25 歲"):
            occ_group_w = [62, 12, 10, 3, 5, 5, 3]
        elif age == "26–35 歲":
            occ_group_w = [6, 38, 28, 8, 8, 9, 3]
        else:
            occ_group_w = [1, 36, 14, 22, 8, 7, 12]
        occ_group = _weighted_choice(rng, list(OCCUPATION_RAW_OPTIONS), occ_group_w)[0]
        occupation = rng.choice(OCCUPATION_RAW_OPTIONS[occ_group])
        if rng.random() < (0.25 if is_chat else 0.08):
            occupation = None
        # 先保留原始年齡給分數引擎用，再決定輸出時要不要把年齡留空
        age_for_engine = age
        if rng.random() < (0.12 if is_chat else 0.04):
            age = None

        # ---- 使用情境（複選）----
        usage_idx = list(dict.fromkeys(_weighted_choice(
            rng, range(5), [35, 20, 15, 25, 10], k=rng.choice([1, 1, 2])
        )))
        usage_full = [USAGE_OPTIONS[i] for i in usage_idx]
        # chat 來源：詞彙粒度不同，會被 app.py 正規化回 5 類
        usage_out = [rng.choice(CHAT_USAGE_ALIASES[u]) for u in usage_full] if is_chat else usage_full

        # ---- 功能需求：依使用情境調整權重 ----
        feat_w = {f: 1.0 for f in FEATURE_OPTIONS}
        for i in usage_idx:
            boost = {
                0: {"GPS": 3.0, "運動分析": 2.6, "心率監測": 1.8, "防水需求": 2.0},
                1: {"通知": 2.6, "行動支付": 2.0, "通話功能": 1.4},
                2: {"通知": 2.2, "通話功能": 2.2, "行動支付": 1.4},
                3: {"心率監測": 3.0, "睡眠追蹤": 3.0, "血氧": 2.4, "ECG": 2.0},
                4: {"通知": 1.4, "行動支付": 1.2},
            }[i]
            for f, m in boost.items():
                feat_w[f] *= m
        feature_picks = list(dict.fromkeys(_weighted_choice(
            rng, FEATURE_OPTIONS, [feat_w[f] for f in FEATURE_OPTIONS],
            k=rng.choice([1, 2, 2, 3, 3]),
        )))
        if is_chat and rng.random() < 0.15:
            feature_picks = []  # 對話中沒明確提功能

        # ---- 預算：與年齡 / 職業相關；None = 跳過這題 ----
        if occ_group == "學生" or age_for_engine in ("18 歲以下", "19–25 歲"):
            budget_w = [34, 42, 12, 3, 9]
        elif occ_group in ("工程師 / 科技業", "運動 / 健身"):
            budget_w = [8, 30, 34, 18, 10]
        else:
            budget_w = [14, 40, 28, 8, 10]
        budget_choice = _weighted_choice(rng, BUDGET_OPTIONS + [None], budget_w)[0]
        if budget_choice is None:
            budget_min, budget_max, budget_idx = 0, 999999, None
        else:
            budget_min, budget_max = BUDGET_RANGES[budget_choice]
            budget_idx = BUDGET_OPTIONS.index(budget_choice)

        # ---- 作業系統（年輕族群 iOS 略多）----
        os_w = [50, 40, 4, 6] if age_for_engine in ("19–25 歲", "26–35 歲") else [36, 52, 5, 7]
        os_choice = _weighted_choice(rng, ["iOS", "Android", "跨平台（皆可）", None], os_w)[0]
        if is_chat and rng.random() < 0.2:
            os_choice = None

        # ---- 裝置類型：與預算、情境相關 ----
        dev_w = {"手錶": 52.0, "手環": 30.0, "戒指": 8.0, "其他": 3.0, None: 7.0}
        if budget_idx == 0:
            dev_w["手環"] *= 2.2
        if 3 in usage_idx or 4 in usage_idx:
            dev_w["戒指"] *= 2.5
        device = _weighted_choice(rng, list(dev_w), list(dev_w.values()))[0]
        device_out = device
        if is_chat and device:
            device_out = {"手錶": "smartwatch", "手環": "smart_band", "戒指": "smart_ring"}.get(device, "earbuds")

        usage_scope = _weighted_choice(rng, ["個人使用", "家庭共用", "要送禮", None], [55, 14, 11, 20])[0]
        if is_chat and rng.random() < 0.3:
            usage_scope = None

        # ---- 推薦分數引擎 → 前 3 名品牌 ----
        ctx = {
            "os": os_choice, "budget_idx": budget_idx, "usage_idx": usage_idx,
            "features": feature_picks, "device": device, "age": age_for_engine,
            "progress": progress, "days_ago": days_ago,
        }
        scores = _brand_scores(rng, ctx)
        brands = _pick_without_replacement(rng, list(scores), list(scores.values()), 3)

        # 真實資料的不完美：同品牌占兩個名額 / 缺品牌欄位的商品被略過
        roll = rng.random()
        if roll < 0.10 and len(brands) >= 2:
            brands[1] = brands[0]                 # 同品牌占兩個名額
        elif roll < 0.15:
            brands = brands[:2]                   # 只剩 2 個品牌
        elif roll < 0.16:
            brands = brands[:1]                   # 只剩 1 個品牌
        product_count = max(len(brands), rng.choice([3, 5, 5, 8, 10]))

        # chat 來源：少數品牌用別名寫法
        brands_out = []
        for b in brands:
            if is_chat and b in CHAT_BRAND_VARIANTS and rng.random() < 0.12:
                brands_out.append(rng.choice(CHAT_BRAND_VARIANTS[b]))
            else:
                brands_out.append(b)

        platforms = _weighted_choice(rng, PLATFORM_OPTIONS, [37, 26, 23, 14], k=len(brands))

        # 偏好品牌：只有 chat 在使用者提到時才有值（問卷路徑恆為空）
        brand_preference = None
        if is_chat and rng.random() < 0.25:
            brand_preference = rng.choice(["Apple", "Garmin", "小米", "Samsung"])

        events.append({
            "created_at": created_at.strftime("%Y-%m-%d"),
            "source": source,
            "age_range": age,
            "occupation": occupation,
            "usage_scope": usage_scope,
            "device_type": device_out,
            "usage": ",".join(usage_out),
            "features": ",".join(feature_picks),
            "os": os_choice,
            "brand_preference": brand_preference,
            "budget_min": budget_min,
            "budget_max": budget_max,
            "top_brands": ",".join(brands_out),
            "top_platforms": ",".join(platforms),
            "product_count": product_count,
        })

    return events


# 對外匯出：一份固定隨機種子產生的假資料，方便展示與除錯
MOCK_EVENTS = generate_mock_events()
