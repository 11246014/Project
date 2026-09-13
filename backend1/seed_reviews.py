import requests
API_BASE = "http://localhost:8000"


def get_product_id_by_name(keyword):
    products = requests.get(f"{API_BASE}/products").json()

    for p in products:
        if keyword in p["name"]:
            return p["id"]

    print(f"[警告] 找不到包含「{keyword}」的商品，跳過")
    return None


seed_data_raw = [
    {
        "product_keyword": "Apple Watch Series 10",
        "rating": 3,
        "content": "戴了兩個月，續航跟運動偵測都很滿意，唯一缺點是錶帶偏硬需要適應"
    },
    {
        "product_keyword": "Apple Watch Series 10",
        "rating": 2,
        "content": "GPS 準確但比較重，長時間配戴手腕會有點負擔"
    },
    {
        "product_keyword": "Garmin Fenix",
        "rating": 3,
        "content": "螢幕很清晰，戶外太陽下也看得清楚，APP介面也很直覺好上手"
    },
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