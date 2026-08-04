import requests
import json

API_KEY = "ab0d5918fc93a088e607edb55955d6f1b8927e62ebe38b8d57dd770a662be6fc"

params = {
    "engine": "google_shopping",
    "q": "Apple Watch",
    "api_key": API_KEY,
    "gl": "tw",
    "hl": "zh-tw"
}

response = requests.get(
    "https://serpapi.com/search",
    params=params
)

data = response.json()

print(json.dumps(data, indent=2, ensure_ascii=False))
