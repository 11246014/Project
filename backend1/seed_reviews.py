import requests
API_BASE = "http://localhost:8000"


def get_product_id_by_name(keyword):
    response = requests.get(f"{API_BASE}/products")
    products = response.json()

    print("========== /products 回傳 ==========")
    print(products)
    print("====================================")

    for p in products:
        if keyword in p["name"]:
            print("找到商品資料：", p)
            return p["id"]

    print(f"[警告] 找不到包含「{keyword}」的商品，跳過")
    return None

seed_data_raw = [
    # GARMIN vivoactive 5 GPS 智慧手錶（全聯全電商）
    {"product_keyword": "GARMIN vivoactive 5 GPS 智慧手錶", "rating": 3,
     "content": "戴著跑步、游泳都沒問題，GPS 定位準確，續航力也很夠，一週充一次電就好"},
    {"product_keyword": "GARMIN vivoactive 5 GPS 智慧手錶", "rating": 2,
     "content": "螢幕在太陽下有點反光，看時間要遮一下，其他功能都還算滿意"},

    # GARMIN *Forerunner 智慧跑錶 165（台灣迪卡儂，資料庫裡有兩筆同名，只會對到第一筆）
    {"product_keyword": "Forerunner 智慧跑錶 165", "rating": 3,
     "content": "專門買來跑步用的，GPS 抓點很快也很準，錶身輕巧配戴很舒適"},
    {"product_keyword": "Forerunner 智慧跑錶 165", "rating": 2,
     "content": "音樂儲存空間有點小，長距離訓練偶爾會覺得續航不夠用"},

    # Garmin Forerunner 165 Music GPS智慧心率跑錶（全聯全電商）
    {"product_keyword": "Forerunner 165 Music GPS", "rating": 3,
     "content": "有音樂功能運動時可以直接聽歌，不用帶手機，運動偵測也蠻準的"},
    {"product_keyword": "Forerunner 165 Music GPS", "rating": 2,
     "content": "APP偶爾連線不穩，要重新配對才能同步資料"},

    # GARMIN Forerunner 70 GPS（Garmin 官方）
    {"product_keyword": "Forerunner 70 GPS", "rating": 3,
     "content": "入門款CP值高，GPS準確度不錯，日常配戴也不會太重"},
    {"product_keyword": "Forerunner 70 GPS", "rating": 2,
     "content": "功能比高階款簡化不少，進階訓練數據比較陽春"},

    # GARMIN Forerunner 170 Music（台灣迪卡儂）
    {"product_keyword": "Forerunner 170 Music", "rating": 3,
     "content": "續航力很讚，訓練加音樂功能一次用好幾天都不用充電"},
    {"product_keyword": "Forerunner 170 Music", "rating": 2,
     "content": "價格偏高，但功能對比其他錶款算是齊全"},

    # GARMIN Forerunner 165 GPS智慧心率跑錶（Coupang 酷澎）
    {"product_keyword": "Forerunner 165 GPS智慧心率跑錶", "rating": 3,
     "content": "心率偵測蠻準的，訓練時數據都跟得上，錶帶戴起來也舒適"},
    {"product_keyword": "Forerunner 165 GPS智慧心率跑錶", "rating": 2,
     "content": "到貨少了保護貼跟原廠盒損傷，希望出貨包裝能更注意"},

    # Smartband Joggers MAP08 Amecopain Global
    {"product_keyword": "Smartband Joggers MAP08", "rating": 2,
     "content": "價格便宜當入門手環還可以，但GPS偵測有時候不太準"},
    {"product_keyword": "Smartband Joggers MAP08", "rating": 1,
     "content": "用沒多久就常常連不上APP，續航也沒有想像中久"},

    # Smartwatch fitness band（Icpshop）
    {"product_keyword": "Smartwatch fitness band", "rating": 2,
     "content": "沒有品牌但基本計步心率功能都有，CP值算OK"},
    {"product_keyword": "Smartwatch fitness band", "rating": 1,
     "content": "螢幕不算清晰，太陽下幾乎看不到畫面內容"},

    # Hume Weave 2.0 Hume Health
    {"product_keyword": "Hume Weave 2.0", "rating": 3,
     "content": "外型簡約好看，長時間配戴也不會不舒服，健康數據記錄蠻詳細"},
    {"product_keyword": "Hume Weave 2.0", "rating": 2,
     "content": "APP介面還在適應，同步速度偶爾比較慢"},

    # GARMIN vivoactive 6 GPS 智慧手錶（Garmin 官方）
    {"product_keyword": "GARMIN vivoactive 6 GPS", "rating": 3,
     "content": "新款升級後螢幕更清晰，戶外太陽下也看得很清楚，運動模式選擇也更多"},
    {"product_keyword": "GARMIN vivoactive 6 GPS", "rating": 2,
     "content": "價格偏高，但整體使用體驗跟做工都有感覺到進步"},

    # GARMIN vivomove Sport 靈魂白,指針智慧手錶（Garmin 官方）
    {"product_keyword": "vivomove Sport", "rating": 3,
     "content": "指針錶面外觀很好看，日常配戴很百搭，基本運動追蹤功能也夠用"},
    {"product_keyword": "vivomove Sport", "rating": 2,
     "content": "沒有彩色螢幕可以顯示詳細數據，進階功能比較受限"},

    # Garmin vivoactive 5 GPS 智慧手錶-活力白（台灣迪卡儂）
    {"product_keyword": "活力白", "rating": 3,
     "content": "白色錶身很好看，GPS定位準確，重量也輕配戴不會有負擔"},
    {"product_keyword": "活力白", "rating": 2,
     "content": "錶帶材質稍微偏硬，第一週配戴需要一些時間適應"},
]

def run_seed():
    for item in seed_data_raw:
        product_id = get_product_id_by_name(item["product_keyword"])

        if product_id is None:
            continue

        payload = {
            "product_id": product_id,
            "rating": item["rating"],
            "content": item["content"],
            "is_seed": True
        }

        resp = requests.post(
            f"{API_BASE}/reviews",
            json=payload
        )

        print(resp.status_code, resp.json())


if __name__ == "__main__":
    run_seed()