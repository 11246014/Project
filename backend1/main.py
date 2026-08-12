from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    status,
    Query
)
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.future import select

from sqlalchemy.orm import Session,declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from models import PromptTemplateCreate



from pydantic import (
    BaseModel,
    EmailStr
)
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
    func,
)
from passlib.context import CryptContext

from database import (
    SessionLocal,
    engine
)
from typing import Dict,List, Optional
from models import (
    User,
    Product,
    Base, Tag, ProductTag
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
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

    username: str = ""

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

    link: str=""
    class Config:
        from_attributes = True

class UserProfileUpdate(BaseModel):
    age_range: str=""
    occupation: str=""
    usage_scope: str=""
    current_device: str=""
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
    print("DB hash:", db_user.hashed_password)


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

    new_product = Product(

        name=product.name,

        price=product.price,

        description=product.description,
        platform=product.platform,

        image=product.image,

        rating=product.rating,

        reason=product.reason,

        link=product.link
        
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


@app.get("/products", response_model=List[ProductCreate])
def products(

    db: Session = Depends(
        get_db
    )
):

    return crud.get_products(db)
#修改商品
@app.put("/products/{product_id}")
def update_product(
    product_id: int,
    product_data: ProductCreate
):

    db = SessionLocal()

    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="商品不存在"
        )

    product.name = product_data.name
    product.price = product_data.price
    product.description = product_data.description
    product.platform = product_data.platform
    product.image = product_data.image
    product.rating = product_data.rating
    product.reason = product_data.reason
    product.link = product_data.link

    db.commit()

    db.close()

    return {
        "message": "商品更新成功"
    }
#刪除商品
@app.delete("/products/{product_id}")
def delete_product(product_id: int):

    db = SessionLocal()

    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="商品不存在"
        )

    db.delete(product)
    db.commit()

    db.close()

    return {
        "message": "商品刪除成功"
    }
#用tag尋找商品
@app.get("/products/by-tag")
def get_products_by_tag(tag: str = Query(...), db: Session = Depends(get_db)):

    # 1️⃣ 找 tag id
    tag_obj = db.query(models.Tag)\
        .filter(models.Tag.tag_name == tag)\
        .first()

    if not tag_obj:
        return {"message": "找不到此標籤", "data": []}

    # 2️⃣ 找 product_id
    product_ids = db.query(models.ProductTag.product_id)\
        .filter(models.ProductTag.tag_id == tag_obj.id)\
        .subquery()

    # 3️⃣ 找商品
    products = db.query(models.Product)\
        .filter(models.Product.id.in_(product_ids))\
        .all()

    # 4️⃣ 回傳
    return [
        {
            "id": p.id,
            "name": p.name
        }
        for p in products
    ]
# 找這個商品的 tag
@app.get("/recommend/{product_id}")
def recommend(product_id: int):

    db = SessionLocal()

    # 取得目前商品標籤
    tag_ids = (
        db.query(ProductTag.tag_id)
        .filter(ProductTag.product_id == product_id)
        .all()
    )

    tag_ids = [tag[0] for tag in tag_ids]

    # 找相同標籤商品
    products = (
        db.query(Product)
        .join(
            ProductTag,
            Product.id == ProductTag.product_id
        )
        .filter(
            ProductTag.tag_id.in_(tag_ids),
            Product.id != product_id
        )
        .distinct()
        .all()
    )

    return products
class WatchPromptTemplate(Base):
    __tablename__ = "watch_prompt_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False) # 範例: "sports_expert"
    description = Column(String(200))                                 # 範例: "針對運動員的推薦"
    template = Column(Text, nullable=False)

# 用於建立/更新 Prompt 模板

# 用於請求渲染推薦 Prompt 的 Schema
class RenderPromptRequest(BaseModel):
    variables: Dict[str, str]
def render_watch_prompt(template_str: str, variables: dict) -> str:
    try:
        # 將字典打散，動態替換模板中括號 {} 內字串
        return template_str.format(**variables)
    except KeyError as e:
        raise ValueError(f"渲染失敗，缺少關鍵參數: {e}")
# --- 1. 後台管理：註冊/新增智慧手錶推薦模板 ---
@app.post("/api/prompts", status_code=201)
def create_template(
    payload: PromptTemplateCreate,
    db: Session = Depends(get_db)
):
    result = db.execute(
        select(WatchPromptTemplate).where(
            WatchPromptTemplate.name == payload.name
        )
    )

    if result.scalars().first():
        raise HTTPException(status_code=400, detail="模板已存在")

    new_template = WatchPromptTemplate(**payload.model_dump())
    db.add(new_template)
    db.commit()

    return {"ok": True}
# --- 2. 前台調用：動態讀取模板並渲染 Prompt ---
@app.post("/api/prompts/{name}/render")
def render_template_endpoint(name: str, payload: RenderPromptRequest, db: Session = Depends(get_db)):

    result = db.execute(
        select(WatchPromptTemplate).where(
            WatchPromptTemplate.name == name
        )
    )

    prompt_record = result.scalars().first()

    if not prompt_record:
        raise HTTPException(status_code=404, detail="找不到模板")

    final_prompt = render_watch_prompt(prompt_record.template, payload.variables)

    return {
        "template_name": name,
        "rendered_prompt": final_prompt
    }

@app.put("/users/{email}/profile")
def update_profile(
    email: str,
    profile: UserProfileUpdate,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="找不到使用者"
        )

    user.age_range = profile.age_range
    user.occupation = profile.occupation
    user.usage_scope = profile.usage_scope
    user.current_device = profile.current_device

    db.commit()
    db.refresh(user)

    return {
        "message": "個人資料更新成功"
    }
@app.get("/me/{email}")
def get_me(
    email: str,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="找不到使用者"
        )

    return {
        "email": user.email,
        "username": user.username or user.email.split("@")[0],
        "age_range": user.age_range,
        "occupation": user.occupation,
        "usage_scope": user.usage_scope,
        "current_device": user.current_device
    }
#歷史紀錄 Schema


class HistoryItem(BaseModel):
    name: str
    price: int = 0
    image: str = ""
    tags: List[str] = []
    rating: float = 0
    platform: str = ""


# =========================
# 新增歷史紀錄 API
# =========================

@app.post("/history/{email}")
def add_history(
    email: str,
    item: HistoryItem,
    db: Session = Depends(get_db)
):

    record = models.History(
        user_email=email,
        name=item.name,
        price=item.price,
        image=item.image,
        tags=",".join(item.tags),
        rating=int(item.rating),
        platform=item.platform,
    )

    db.add(record)
    db.commit()

    return {
        "message": "已加入歷史紀錄"
    }


# =========================
# 查詢歷史紀錄 API
# =========================

@app.get("/history/{email}")
def get_history(
    email: str,
    db: Session = Depends(get_db)
):

    records = (
        db.query(models.History)
        .filter(models.History.user_email == email)
        .order_by(models.History.id.desc())
        .limit(20)
        .all()
    )

    return [
        {
            "name": r.name,
            "price": r.price,
            "image": r.image,
            "tags": r.tags.split(",") if r.tags else [],
            "rating": r.rating,
            "platform": r.platform,
            "viewedAt": r.created_at.strftime("%m/%d %H:%M") if r.created_at else "",
        }
        for r in records
    ]