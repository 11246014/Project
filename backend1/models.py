from sqlalchemy import (
    Column,
    Integer,
    String,
    Text
)

from database import Base

from pydantic import (
    BaseModel,
    EmailStr
)


# =========================
# 使用者模型
# =========================

class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    email = Column(
        String(255),
        unique=True
    )

    hashed_password = Column(
        String(255)
    )


# =========================
# 登入模型
# =========================

class UserLogin(BaseModel):

    email: EmailStr

    password: str


# =========================
# 商品模型
# =========================

class Product(Base):

    __tablename__ = "products"

    id = Column(
        Integer,
        primary_key=True
    )

    name = Column(
        String(255)
    )

    price = Column(
        Integer
    )

    description = Column(
        Text
    )

    platform = Column(
        String(255)
    )

    image = Column(
        Text
    )

    rating = Column(
        Integer
    )

    reason = Column(
        Text
    )
