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