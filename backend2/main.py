from fastapi import FastAPI
from pydantic import BaseModel
import requests
from fastapi.middleware.cors import CORSMiddleware  

app = FastAPI()

# 1. 解決跨域問題 (CORS)：確保前端隊友不論是用 localhost 還是 ngrok 網址都能連進來
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置區域：將變數集中管理
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen3"  # 確保與你 Ollama 下載的模型名稱一致

class UserRequest(BaseModel):
    message: str

# 聊天歷史紀錄 (存於記憶體，重啟伺服器會重置)
chat_history = []

@app.get("/")
def home():
    # 這裡加上 W2 標記，方便你從瀏覽器確認程式已經更新
    return {"message": "Backend2 AI Server is Online (W2 Version)"}

# 【W1 功能優化：購物導購聊天】
@app.post("/ai/chat")
def ai_chat(req: UserRequest):
    global chat_history
    
    # 紀錄使用者訊息
    chat_history.append(f"使用者: {req.message}")
    
    # 組合對話脈絡
    conversation = "\n".join(chat_history)

    # 優化後的 Prompt：強化台灣用語與導購助理身份
    prompt = f"""你是一個專業且親切的購物導購助理，請使用「繁體中文」回答，並使用台灣生活化用語。
    
    ⚠️ 規則：
    1. 語氣要像真人的服務櫃員。
    2. 如果使用者有購買意願，請主動詢問他的「具體用途」或「預算範圍」。
    3. 絕對嚴禁使用簡體字。

    對話內容：
    {conversation}

    助理回應："""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
            timeout=30  # 增加超時保護，避免 AI 算太久導致當機
        )
        response.raise_for_status()
        result = response.json()["response"]
        
        # 紀錄 AI 回應
        chat_history.append(f"AI: {result}")
        
        return {"reply": result}
    except Exception as e:
        return {"reply": f"系統忙碌中，請稍後再試。錯誤訊息: {str(e)}"}

# 【W2 核心任務：提取搜尋關鍵字】
@app.post("/ai/search_keywords")
def get_keywords(req: UserRequest):
    """
    實作 W2 進度：將對話轉化為商品搜尋關鍵字。
    這能讓前端拿到結果後，去資料庫或網路 API 找商品。
    """
    prompt = f"你是一個搜尋優化專家。請從使用者的話中提取出一個最適合搜尋商品的『繁體中文關鍵字』。規則：只回傳關鍵字本身，不要有任何標點符號或解釋文字。使用者說：'{req.message}'"
    
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
            timeout=15
        )
        response.raise_for_status()
        keywords = response.json()["response"].strip()
        
        return {
            "original_message": req.message,
            "suggested_keyword": keywords
        }
    except Exception as e:
        return {"error": str(e)}