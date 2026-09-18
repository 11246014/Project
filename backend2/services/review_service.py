#review_service.py
import json
from collections import Counter

from services.ai_service import (
    ask_ai,
    ask_ai_structured,
)

from services.backend1_client import (
    get_reviews_by_product,
    update_review,
    upsert_review_summary,
)
from services.ranking.constants import REVIEW_KEYWORD_OPTIONS


BATCH_THRESHOLD = 5

REVIEW_KEYWORD_SCHEMA = {
    "type": "object",
    "properties": {
        "pros": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": REVIEW_KEYWORD_OPTIONS["pros"],
            },
            "uniqueItems": True,
        },
        "cons": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": REVIEW_KEYWORD_OPTIONS["cons"],
            },
            "uniqueItems": True,
        },
    },
    "required": [
        "pros",
        "cons",
    ],
    "additionalProperties": False,
}

def extract_review_keywords(content: str) -> dict:
    """
    使用 AI 分析單則評論，萃取 pros / cons。

    AI 只能從 REVIEW_KEYWORD_OPTIONS 裡選擇，
    不允許產生新的關鍵字。

    回傳格式：
    {
        "pros": ["續航佳", "配戴舒適"],
        "cons": ["價格偏高"]
    }
    """

    if not content or not content.strip():
        return {
            "pros": [],
            "cons": [],
        }

    pros_options = REVIEW_KEYWORD_OPTIONS.get("pros", [])
    cons_options = REVIEW_KEYWORD_OPTIONS.get("cons", [])

    prompt = f"""
你是一個智慧穿戴產品評論分析助手。

請分析以下使用者評論，從固定的關鍵字選項中，
找出評論中明確提到的優點（pros）與缺點（cons）。

【重要規則】
1. pros 只能從下列選項選擇：
{json.dumps(pros_options, ensure_ascii=False)}

2. cons 只能從下列選項選擇：
{json.dumps(cons_options, ensure_ascii=False)}

3. 不可以自行創造新的關鍵字。
4. 如果評論沒有提到某個優點或缺點，就不要選。
5. 同一個關鍵字不要重複。
6. 最後只能輸出 JSON，不要輸出 Markdown。
7. JSON 格式必須完全如下：

{{
    "pros": [],
    "cons": []
}}

使用者評論：
{content}
"""

    try:
        result = ask_ai_structured(
            prompt,
            schema=REVIEW_KEYWORD_SCHEMA,
        )

        if not result:
            return {
                "pros": [],
                "cons": [],
            }

        data = json.loads(result)

        if not isinstance(data, dict):
            return {
                "pros": [],
                "cons": [],
            }

        raw_pros = data.get("pros", [])
        raw_cons = data.get("cons", [])

        if not isinstance(raw_pros, list):
            raw_pros = []

        if not isinstance(raw_cons, list):
            raw_cons = []

        # ---------------------------------------------------------
        # 最重要的安全限制：
        # 不論 AI 回傳什麼，最後只允許固定清單中的關鍵字。
        # ---------------------------------------------------------

        valid_pros = [
            keyword
            for keyword in raw_pros
            if keyword in pros_options
        ]

        valid_cons = [
            keyword
            for keyword in raw_cons
            if keyword in cons_options
        ]

        # 去除重複，同時保留原本順序
        valid_pros = list(dict.fromkeys(valid_pros))
        valid_cons = list(dict.fromkeys(valid_cons))

        return {
            "pros": valid_pros,
            "cons": valid_cons,
        }

    except json.JSONDecodeError as e:
        print(f"[Review AI JSON Error] {e}")
        return {
            "pros": [],
            "cons": [],
        }

    except Exception as e:
        print(f"[Review Keyword Error] {e}")
        return {
            "pros": [],
            "cons": [],
        }


def aggregate_top_keywords(
    reviews: list,
    field: str,
    top_n: int = 3,
) -> list:
    """
    統計評論中的 pros / cons，取得出現次數最高的關鍵字。

    field:
        "pros" 或 "cons"

    回傳：
        ["續航佳", "配戴舒適", "APP 好用"]
    """

    if field not in ("pros", "cons"):
        return []

    counter = Counter()

    for review in reviews:
        if not isinstance(review, dict):
            continue

        keywords = review.get(field, [])

        # Backend1 儲存格式為逗號分隔字串；同時保留對 list 的相容處理。
        if isinstance(keywords, str):
            keywords = [
                keyword.strip()
                for keyword in keywords.split(",")
                if keyword.strip()
            ]
        elif not isinstance(keywords, list):
            continue

        for keyword in keywords:
            if keyword:
                counter[keyword] += 1

    return [
        keyword
        for keyword, _count in counter.most_common(top_n)
    ]


def generate_summary_text(
    reviews: list,
    top_pros: list,
    top_cons: list,
) -> str:
    """
    使用 AI 根據評論與 Top pros / cons 產生產品社群摘要。

    這個摘要會寫入 product_review_summary.summary_text。

    Recommendation 時只讀取這個結果，
    不在推薦流程中再次呼叫 AI。
    """

    if not reviews:
        return ""

    review_contents = []

    for review in reviews:
        if not isinstance(review, dict):
            continue

        content = review.get("content", "")

        if content:
            review_contents.append(str(content))

    if not review_contents:
        return ""

    pros_text = "、".join(top_pros) if top_pros else "無明顯優點"
    cons_text = "、".join(top_cons) if top_cons else "無明顯缺點"

    reviews_text = "\n".join(
        f"- {content}"
        for content in review_contents
    )

    prompt = f"""
你是一個智慧穿戴產品的社群評論摘要助手。

請根據以下使用者評論，
產生一段簡短、客觀、適合顯示給消費者看的社群心得摘要。

【目前統計出的熱門優點】
{pros_text}

【目前統計出的熱門缺點】
{cons_text}

【使用者評論】
{reviews_text}

要求：
1. 使用繁體中文。
2. 摘要要客觀，不要誇大。
3. 可以提到使用者常見的優點與缺點。
4. 不要虛構評論中沒有提到的資訊。
5. 不需要列點。
6. 只輸出摘要文字，不要輸出 JSON。
7. 不要加上「摘要：」等標題。
"""

    try:
        result = ask_ai(prompt)

        if not result:
            return ""

        return result.strip()

    except Exception as e:
        print(f"[Review Summary Error] {e}")
        return ""


def process_single_review(
    review_id: int,
    content: str,
):
    """
    處理單則評論。

    Step A：
    1. AI 分析評論
    2. 萃取 pros / cons
    3. 回寫 Backend1
    4. 判斷是否需要進行產品批次彙整
    """

    try:
        # ---------------------------------------------------------
        # Step A：AI 分析單則評論
        # ---------------------------------------------------------

        keywords = extract_review_keywords(content)

        pros = keywords.get("pros", [])
        cons = keywords.get("cons", [])

        review_data = {
            'pros': ','.join(pros),
            'cons': ','.join(cons),
            'process_status': 'done',
        }

        # ---------------------------------------------------------
        # 回寫 Backend1
        # ---------------------------------------------------------

        review = update_review(
            review_id,
            review_data,
        )

        if not review:
            print(
                f"[Review Process] "
                f"review_id={review_id} 更新 Backend1 失敗"
            )
            return

        # ---------------------------------------------------------
        # 取得這則評論所屬產品
        #
        # Backend1 回傳的欄位名稱可能依目前 API 實作而不同，
        # 因此依序嘗試常見欄位。
        # ---------------------------------------------------------

        product_id = (
            review.get("product_id")
            or review.get("productId")
        )

        if not product_id:
            print(
                f"[Review Process] "
                f"review_id={review_id} 找不到 product_id"
            )
            return

        # ---------------------------------------------------------
        # Step B：取得該產品目前所有評論
        # ---------------------------------------------------------

        reviews = get_reviews_by_product(product_id)

        if not reviews:
            print(
                f"[Review Process] "
                f"product_id={product_id} 沒有評論資料"
            )
            return

        # ---------------------------------------------------------
        # 計算目前「已處理」評論數量
        #
        # 只有已經具有 pros / cons 欄位的評論才算處理完成。
        # ---------------------------------------------------------

        processed_reviews = []

        for item in reviews:
            if not isinstance(item, dict):
                continue

            if "pros" in item and "cons" in item:
                processed_reviews.append(item)

        processed_count = len(processed_reviews)

        # ---------------------------------------------------------
        # 每 5 則進行一次 batch aggregation
        #
        # 第 1～5 則時執行
        # 第 10、15、20...則時再次執行
        # ---------------------------------------------------------

        if (
            processed_count <= BATCH_THRESHOLD
            or processed_count % BATCH_THRESHOLD == 0
        ):
            run_batch_aggregation(
                product_id,
                processed_reviews,
            )

    except Exception as e:
        print(
            f"[Review Process Error] "
            f"review_id={review_id}, error={e}"
        )


def run_batch_aggregation(
    product_id: int,
    reviews: list,
):
    """
    對單一產品的評論進行批次彙整。

    1. Counter 統計 Top 3 pros
    2. Counter 統計 Top 3 cons
    3. AI 產生 summary_text
    4. 更新 Backend1 的 product_review_summary
    """

    if not product_id:
        return

    if not reviews:
        return

    try:
        # ---------------------------------------------------------
        # 1. 統計 Top 3 pros
        # ---------------------------------------------------------

        top_pros = aggregate_top_keywords(
            reviews,
            "pros",
            top_n=3,
        )

        # ---------------------------------------------------------
        # 2. 統計 Top 3 cons
        # ---------------------------------------------------------

        top_cons = aggregate_top_keywords(
            reviews,
            "cons",
            top_n=3,
        )

        # ---------------------------------------------------------
        # 3. AI 產生 summary_text
        #
        # 這裡只呼叫一次 AI。
        # Recommendation 不會再呼叫 AI。
        # ---------------------------------------------------------

        summary_text = generate_summary_text(
            reviews,
            top_pros,
            top_cons,
        )
        total = len(reviews)
        positive = sum(1 for r in reviews if r.get('rating') == 3)

        # ---------------------------------------------------------
        # 4. 更新 product_review_summary
        # ---------------------------------------------------------

        summary_data = {
            'review_count': total,
            'positive_ratio': round(positive / total, 2) if total else 0.0,
            'top_pros': top_pros,
            'top_cons': top_cons,
            'summary_text': summary_text,
        }

        result = upsert_review_summary(
            product_id,
            summary_data,
        )

        if not result:
            print(
                f"[Review Batch] "
                f"product_id={product_id} summary 更新失敗"
            )
            return

        print(
            f"[Review Batch] "
            f"product_id={product_id}, "
            f"reviews={len(reviews)}, "
            f"top_pros={top_pros}, "
            f"top_cons={top_cons}"
        )

    except Exception as e:
        print(
            f"[Review Batch Error] "
            f"product_id={product_id}, error={e}"
        )