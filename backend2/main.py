import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from routers.ai_router import router as ai_router
from routers.filter_router import router as filter_router

app = FastAPI()

# ===== 載入 Routers =====

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
    
# =========================
# 圖片代理 API
# =========================

@app.get("/image-proxy")
async def image_proxy(url: str = Query(..., description="原始圖片網址")):
    """
    圖片代理 API

    背景：
    Flutter Web 版使用 CanvasKit 渲染器，瀏覽器規定圖片來源
    必須提供 CORS header（Access-Control-Allow-Origin）才能被畫在 canvas 上。
    momo、PChome、蝦皮等電商圖片伺服器大多不會開放 CORS，
    導致 Image.network() 在 Web 版讀取失敗（App / 手機版不受影響）。

    解法：
    後端代替瀏覽器去抓外部圖片，再用自己的網域重新吐出去給前端。
    因為是自己的網域，本檔案已設定的 CORSMiddleware
    (allow_origins=["*"]) 會自動幫這支 API 的回應加上
    Access-Control-Allow-Origin，瀏覽器就能正常讀取圖片。
    """

    try:

        async with httpx.AsyncClient(timeout=10) as client:

            resp = await client.get(url)

            resp.raise_for_status()

        content_type = resp.headers.get(
            "content-type",
            "image/jpeg",
        )

        return Response(
            content=resp.content,
            media_type=content_type,
            headers={
                # 讓瀏覽器快取圖片 1 天，減少重複代理造成的延遲與流量
                "Cache-Control": "public, max-age=86400",
            },
        )

    except Exception as e:

        print(f"[Image Proxy Error] {url} -> {e}")

        # 圖片抓取失敗時回傳 404，前端的 errorBuilder 會接手顯示備用圖示
        raise HTTPException(
            status_code=404,
            detail="圖片載入失敗",
        )