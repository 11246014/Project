from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext

from database import SessionLocal
from models import User
from models import Product
import models
import schemas
import crud





from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# 取得資料庫連線
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 首頁
@app.get("/")
def home():
    return {"message": "FastAPI 成功運作"}



class UserCreate(BaseModel):
    email: EmailStr
    password: str

# 註冊 API


@app.post("/register")
def register_user(user: UserCreate):

    db = SessionLocal()

    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="此 Email 已被註冊"
        )
    print("password =", user.password)
    print("length =", len(user.password))

    hashed_password = pwd_context.hash(user.password)

    new_user = User(
        email=user.email,
        hashed_password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    db.close()

    return {
        "message": "會員註冊成功",
        "user_id": new_user.id
    }
class UserLogin(BaseModel):
    email: EmailStr
    password: str
#登入api
@app.post("/login")
def login(user: UserLogin):

    db = SessionLocal()

    # 查詢會員
    db_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    # Email不存在
    if not db_user:
        db.close()
        raise HTTPException(
            status_code=401,
            detail="帳號或密碼錯誤"
        )

    # 驗證密碼
    if not pwd_context.verify(
        user.password,
        db_user.hashed_password
    ):
        db.close()
        raise HTTPException(
            status_code=401,
            detail="帳號或密碼錯誤"
        )

    db.close()

    return {
        "message": "登入成功",
        "email": db_user.email
    }
#商品
class ProductCreate(BaseModel):
    name: str
    price: float
    stock: int
    description: str

# 創建商品 API
@app.post("/products")
def create_product(product: ProductCreate):

    db = SessionLocal()

    new_product = Product(
        name=product.name,
        price=product.price,
        stock=product.stock,
        description=product.description
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    db.close()

    return {
        "message": "商品新增成功",
        "id": new_product.id
    }

# 查詢商品 API
@app.get("/products")
def products(db: Session = Depends(get_db)):
    return crud.get_products(db)