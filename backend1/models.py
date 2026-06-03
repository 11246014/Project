from sqlalchemy import Column, Integer, String, Text
from database import Base
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel, EmailStr



Base = declarative_base()
#使用者模型
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True)
    hashed_password = Column(String(255))


#登入模型
class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    price = Column(Integer)
    description = Column(Text)
