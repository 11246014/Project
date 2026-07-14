import os

import google.generativeai as genai

from dotenv import load_dotenv

from config.settings import GEMINI_MODEL

load_dotenv()

genai.configure(
    api_key=os.getenv(
        "GEMINI_API_KEY"
    )
)


def ask_gemini(
    prompt,
    model_name=None
):
    """
    Send a prompt to Gemini
    and return the generated text.
    """

    model = genai.GenerativeModel(
        model_name or GEMINI_MODEL
    )

    response = model.generate_content(
        prompt
    )

    return (
        response.text
        if response.text
        else ""
    )