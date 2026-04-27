chat_history = []
from fastapi import FastAPI
from pydantic import BaseModel
import requests
from fastapi.middleware.cors import CORSMiddleware  

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_URL = "http://localhost:11434/api/generate"

class UserRequest(BaseModel):
    message: str


@app.get("/")
def home():
    return {"message": "Backend2 working"}


@app.post("/ai/chat")
def ai_chat(req: UserRequest):
    global chat_history

    # 加入使用者訊息
    chat_history.append(f"使用者: {req.message}")

    # 組合對話
    conversation = "\n".join(chat_history)

    prompt = f"""
    你是一個購物導購助理，請用「繁體中文」回答，並使用台灣用語。

    ⚠️ 規則：
    - 一律使用繁體中文
    - 不要出現任何簡體字
    - 語氣自然，像真人對話
    - 如果出現簡體字，請自動轉為繁體

    對話內容：
    {conversation}

    請給出自然回應
    """

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "qwen3",
            "prompt": prompt,
            "stream": False
        }
    )

    result = response.json()["response"]

    # 加入AI回應
    chat_history.append(f"AI: {result}")

    return {
        "reply": result
    }