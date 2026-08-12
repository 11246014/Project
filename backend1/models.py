from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey
)

from database import Base

from pydantic import (
    BaseModel,
    EmailStr
)
from typing import Optional


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
    age_range = Column(String(50), nullable=True)
    occupation = Column(String(100), nullable=True)
    usage_scope = Column(String(200), nullable=True)
    current_device = Column(String(200), nullable=True)
    username = Column(String(100), nullable=True)


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

    name = Column(String(255))
    price = Column(Integer)
    description = Column(Text )
    platform = Column(String(255))
    image = Column(Text)
    rating = Column(Integer)
    reason = Column(Text)
    link = Column(String(255))

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    tag_name = Column(String(255))

class ProductTag(Base):
    __tablename__ = "product_tags"

    product_id = Column(Integer, ForeignKey("products.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)

class PromptTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    template: str
