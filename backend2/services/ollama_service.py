import requests

from config.settings import (
    OLLAMA_URL,
    MODEL_NAME
)

def ask_ollama(
    prompt,
    model_name=None,
    timeout=120
):
    print(
    f"[Model] {model_name}"
    )
    
    if not model_name:

        model_name = MODEL_NAME

    response = requests.post(

        OLLAMA_URL,

        json={

            "model": model_name,

            "prompt": prompt,

            "stream": False
        },

        timeout=timeout
    )

    response.raise_for_status()

    return response.json().get(
        "response",
        ""
    )