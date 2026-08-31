from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
    Boolean,
    Float,
    JSON,
    func,
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
    description = Column(Text, default="")
    platform = Column(String(255), default="")
    image = Column(Text, default="")
    rating = Column(Integer, default=0)
    reason = Column(Text, default="")
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
# 合作廠商
class SponsoredBrand(Base):

    __tablename__ = "sponsored_brands"

    id = Column(Integer,primary_key=True,index=True)
    brand_name = Column(String(255),nullable=False,index=True)
    platform = Column(String(255),nullable=False,index=True)
    sponsor_level = Column(String(50),nullable=False,default="standard")
    boost_rate = Column(Float,nullable=False,default=0.0)
    is_active = Column(Boolean,nullable=False,default=True )
    created_at = Column(DateTime,server_default=func.now())
    updated_at = Column(DateTime,server_default=func.now(),onupdate=func.now())
    
class History(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String(255), index=True)
    name = Column(String(255))
    price = Column(Integer, default=0)
    image = Column(Text)
    tags = Column(Text)              # 用逗號分隔字串存 List[str]，例如 "#GPS,#防水"
    rating = Column(Integer, default=0)
    platform = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
# 推薦事件模型

class RecommendationEvent(Base):
    __tablename__ = "recommendation_events"
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    source = Column(String(20))
    age_range = Column(String(50), nullable=True)
    occupation = Column(String(100), nullable=True)
    usage_scope = Column(String(50), nullable=True)
    device_type = Column(String(50), nullable=True)
    usage = Column(String(255), nullable=True) # 逗號分隔
    features = Column(String(255), nullable=True) # 逗號分隔
    os = Column(String(50), nullable=True)
    brand_preference = Column(String(100), nullable=True)
    budget_min = Column(Integer, nullable=True)
    budget_max = Column(Integer, nullable=True)
    top_brands = Column(String(255), nullable=True) # 逗號分隔
    top_platforms = Column(String(255), nullable=True) # 逗號分隔
    product_count = Column(Integer, default=0)