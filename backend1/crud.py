from sqlalchemy.orm import Session

import models


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

def create_recommendation_event(
    db: Session,
    event_data,
):

    event_kwargs = {
        "user_need": event_data.user_need,
        "recommend_results": event_data.recommend_results,
    }

    if event_data.timestamp is not None:
        event_kwargs["timestamp"] = event_data.timestamp

        new_event = models.RecommendationEvent(**event_data.model_dump())
        db.add(new_event)
        db.commit()
        db.refresh(new_event)
        return new_event



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