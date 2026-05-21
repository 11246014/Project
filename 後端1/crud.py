from sqlalchemy.orm import Session
import models

def create_user(db: Session, user):
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    return new_user


def get_products(db: Session):
    return db.query(models.Product).all()
