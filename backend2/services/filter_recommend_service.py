import json

from services.ai_service import ask_ai


def generate_filter_recommendation(filters, products):

    prompt = f"""
你是 WearWise 智慧穿戴推薦顧問。

請根據篩選結果推薦商品。

規則：

1. 依照商品排序順序介紹
2. 第一個商品介紹較詳細
3. 第二個商品簡短介紹
4. 第三個商品一句話帶過
5. 每個商品都需提到價格
6. 優先參考推薦原因
7. 不可推測不存在的功能
8. 不可自行補充規格
9. 不可自行比較產品優劣
10. 不可出現結論段落
11. 不可出現開場白
12. 使用繁體中文
13. 使用台灣用語
14. 控制在150字內
15. 直接輸出純文字
16. 不要使用 Markdown
17. 若推薦原因未提及某功能，不得自行補充
18. 請將推薦原因改寫成自然語句
19. 不要重複相同句型
20. 回覆直接從第一個商品開始介紹

使用者條件：

{json.dumps(filters, ensure_ascii=False)}

商品資料：

{json.dumps(products[:3], ensure_ascii=False)}
"""

    result = ask_ai(prompt)

    return result