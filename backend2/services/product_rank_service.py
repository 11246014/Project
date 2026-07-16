# product_rank_service.py

# =========================
# Product Rank Service
# =========================

def calculate_product_score(
    product,
    user_need=None
):
    """
    計算商品分數

    暫時直接回傳 0，
    後續會加入：
    - Rating
    - Budget
    - Features
    - Usage
    - Brand
    """
    return 0


def rank_products(
    products,
    user_need=None
):
    """
    商品排序

    後續會依照 score 排序。
    """

    return products