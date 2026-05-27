from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.search_router import router as search_router
from routers.ai_router import router as ai_router

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 載入 AI Router
app.include_router(ai_router)

@app.get("/")
def home():
    return {
        "status": "AI Brain Online",
        "version": "W6 Modular Version"
    }

app.include_router(search_router)