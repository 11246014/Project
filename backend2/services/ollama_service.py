import requests

from config.settings import (
    OLLAMA_URL,
    OLLAMA_MODEL
)


def ask_ollama(
    prompt,
    model_name=None,
    timeout=120
):
    """
    Send a prompt to Ollama
    and return the generated text.
    """

    model = model_name or OLLAMA_MODEL

    print(
        f"[Model] {model}"
    )

    response = requests.post(

        OLLAMA_URL,

        json={

            "model": model,

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