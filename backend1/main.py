from fastapi import (
    FastAPI,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from pydantic import (
    BaseModel,
    EmailStr
)

from passlib.context import CryptContext

from database import (
    SessionLocal,
    engine
)

from models import (
    User,
    Product
)

import models
import crud


# =========================
# 建立資料表
# =========================

models.Base.metadata.create_all(
    bind=engine
)

# =========================
# FastAPI
# =========================

app = FastAPI()

# =========================
# 密碼加密
# =========================

pwd_context = CryptContext(

    schemes=["bcrypt"],

    deprecated="auto"
)

# =========================
# DB 連線
# =========================

def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()


# =========================
# 首頁
# =========================

@app.get("/")
def home():

    return {

        "message": "FastAPI 成功運作"
    }


# =========================
# 註冊 Schema
# =========================

class UserCreate(BaseModel):

    email: EmailStr

    password: str


# =========================
# 登入 Schema
# =========================

class UserLogin(BaseModel):

    email: EmailStr

    password: str


# =========================
# 商品 Schema
# =========================

class ProductCreate(BaseModel):

    name: str

    price: int

    description: str = ""

    platform: str = ""

    image: str = ""

    rating: int = 0

    reason: str = ""


# =========================
# 註冊 API
# =========================

@app.post("/register")
def register_user(user: UserCreate):

    db = SessionLocal()

    existing_user = (

        db.query(User)

        .filter(
            User.email == user.email
        )

        .first()
    )

    # =========================
    # Email 已存在
    # =========================

    if existing_user:

        raise HTTPException(

            status_code=400,

            detail="此 Email 已被註冊"
        )

    # =========================
    # 密碼加密
    # =========================

    hashed_password = pwd_context.hash(
        user.password
    )

    # =========================
    # 建立會員
    # =========================

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


# =========================
# 登入 API
# =========================

@app.post("/login")
def login(user: UserLogin):

    db = SessionLocal()

    # =========================
    # 查詢會員
    # =========================

    db_user = (

        db.query(User)

        .filter(
            User.email == user.email
        )

        .first()
    )

    # =========================
    # 帳號不存在
    # =========================

    if not db_user:

        db.close()

        raise HTTPException(

            status_code=401,

            detail="帳號或密碼錯誤"
        )

    # =========================
    # 密碼錯誤
    # =========================

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


# =========================
# 新增商品 API
# =========================

@app.post("/products")
def create_product(
    product: ProductCreate
):

    db = SessionLocal()

    # =========================
    # 建立商品
    # =========================

    new_product = Product(

        name=product.name,

        price=product.price,

        description=product.description,

        platform=product.platform,

        image=product.image,

        rating=product.rating,

        reason=product.reason
    )

    db.add(new_product)

    db.commit()

    db.refresh(new_product)

    db.close()

    return {

        "message": "商品新增成功",

        "id": new_product.id
    }


# =========================
# 查詢商品 API
# =========================

@app.get("/products")
def products(

    db: Session = Depends(
        get_db
    )
):

    return crud.get_products(db)