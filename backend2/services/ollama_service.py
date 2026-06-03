import requests

from config.settings import OLLAMA_URL, MODEL_NAME

def ask_ollama(prompt, timeout=120):

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        },
        timeout=timeout
    )

    response.raise_for_status()

    return response.json().get("response", "")