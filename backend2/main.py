from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.search_router import router as search_router
from routers.ai_router import router as ai_router
from routers.filter_router import router as filter_router

app = FastAPI()

# ===== 載入 Routers =====

app.include_router(search_router)

app.include_router(ai_router)

app.include_router(filter_router)

# ===== CORS =====

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== 測試首頁 =====

@app.get("/")
def home():

    return {
        "status": "AI Brain Online",
        "version": "W6 Modular Version"
    }