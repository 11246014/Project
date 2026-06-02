from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

import models
import schemas
import crud

from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

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


# 註冊 API
@app.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user)


# 查詢商品 API
@app.get("/products")
def products(db: Session = Depends(get_db)):
    return crud.get_products(db)

@app.post("/products")
def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db)
):
    return crud.create_product(
        db,
        product
    )