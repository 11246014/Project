from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

OLLAMA_URL = "http://localhost:11434/api/generate"

class UserRequest(BaseModel):
    message: str


@app.get("/")
def home():
    return {"message": "Backend2 working"}


@app.post("/ai/recommend")
def ai_recommend(req: UserRequest):
    prompt = f"""
    你是一個購物助理，請把使用者需求轉成商品搜尋條件(JSON)

    使用者輸入：
    {req.message}

    只輸出 JSON，不要任何說明：

    {{
        "category": "",
        "price": "",
        "color": "",
        "usage": ""
    }}
    """

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "qwen3",
            "prompt": prompt,
            "stream": False
        }
    )

    result = response.json()

    return {
        "result": result["response"]
    }