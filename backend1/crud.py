from sqlalchemy.orm import Session

import models
from schemas import ReviewCreate, ReviewProcessUpdate, ReviewSummaryUpsert

def create_user(db: Session, user):

    new_user = models.User(**user.dict())

    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    return new_user


def get_products(db: Session):

    return db.query(
        models.Product
    ).all()


def create_product(db: Session, product):

    new_product = models.Product(
        name=product.name,
        price=product.price,
        description=product.description
    )

    db.add(new_product)

    db.commit()

    db.refresh(new_product)

    return new_product

# =========================
# Sponsor CRUD
# =========================

def get_active_sponsors(db: Session):

    return (
        db.query(models.SponsoredBrand)
        .filter(
            models.SponsoredBrand.is_active == True
        )
        .all()
    )


# =========================
# Analytics CRUD
# =========================

def get_recommendation_events(db: Session):

    return (
        db.query(
            models.RecommendationEvent
        )
        .order_by(
            models.RecommendationEvent.timestamp.desc()
        )
        .all()
    )
def get_all_recommendation_events(db: Session):
    return (
    db.query(models.RecommendationEvent)
    .order_by(models.RecommendationEvent.created_at.desc())
    .all()
    )
def create_recommendation_event(
    db: Session,
    event_data
):
    new_event = models.RecommendationEvent(
        **event_data.model_dump()
    )

    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    return new_event

def create_review(db: Session, review: ReviewCreate):
    new_review = models.ProductReview(**review.dict())
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    recalc_positive_ratio(db, review.product_id)  # 立即更新好評率，不等AI
    return new_review
def recalc_positive_ratio(db: Session, product_id: int):
    """純 SQL 計算，毫秒等級，跟 AI 完全脫鉤"""
    reviews = db.query(models.ProductReview).filter_by(product_id=product_id).all()
    total = len(reviews)
    ratio = (
    round(
        sum(1 for r in reviews if r.rating == 3) / total,
        2
    )
    if total
    else 0.0
)
    summary = db.query(models.ProductReviewSummary).filter_by(product_id=product_id).first()
    if not summary:
        summary = models.ProductReviewSummary(product_id=product_id)
        db.add(summary)
    summary.review_count = total
    summary.positive_ratio = ratio
    db.commit()
def get_reviews(db: Session, limit: int = 50, offset: int = 0):
    """取得所有商品的心得列表，依時間新到舊排序，給社群動態牆分頁使用"""
    return (db.query(models.ProductReview)
            .order_by(models.ProductReview.created_at.desc())
            .offset(offset).limit(limit).all())
def get_reviews_by_product(db: Session, product_id: int):
    """取得單一商品的所有心得，給商品詳情頁「查看全部心得」使用"""
    return (db.query(models.ProductReview)
            .filter_by(product_id=product_id)
            .order_by(models.ProductReview.created_at.desc()).all())
def get_review_summary(db: Session, product_id: int):
    """取得單一商品的彙整摘要，給商品詳情頁的社群評價卡片使用"""
    return db.query(models.ProductReviewSummary).filter_by(product_id=product_id).first()
def get_all_review_summaries(db: Session):
    """給後端 2 score_engine 一次性撈取全部商品的摘要用"""
    return db.query(models.ProductReviewSummary).all()
def update_review_processing(db: Session, review_id: int, update: 
ReviewProcessUpdate):
    """後端 2 抽取完單則心得的情緒/優缺點後，呼叫這支寫回資料庫"""
    review = db.query(models.ProductReview).filter_by(id=review_id).first()
    if not review:
        return None
    for field, value in update.dict(exclude_unset=True).items():
        setattr(review, field, value)
    db.commit()
    db.refresh(review)
    return review
def upsert_review_summary(db: Session, product_id: int, data: ReviewSummaryUpsert):
    """後端 2 批次彙整完摘要後，呼叫這支寫入/覆蓋 product_review_summary"""
    summary = db.query(models.ProductReviewSummary).filter_by(product_id=product_id).first()
    if not summary:
        summary = models.ProductReviewSummary(product_id=product_id)
        db.add(summary)
    for field, value in data.dict(exclude_unset=True).items():
        setattr(summary, field, value)
    db.commit()
    return summary