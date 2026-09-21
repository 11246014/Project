#gemini_service.py
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from config.settings import GEMINI_MODEL

load_dotenv()


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def ask_gemini(
    prompt,
    model_name=None
):
    """
    Send a prompt to Gemini
    and return the generated text.
    """

    response = client.models.generate_content(
        model=model_name or GEMINI_MODEL,
        contents=prompt,
    )

    return (
        response.text
        if response.text
        else ""
    )


def ask_gemini_structured(
    prompt,
    schema,
    model_name=None,
):
    """
    Send a prompt to Gemini
    and return structured JSON text.
    """

    response = client.models.generate_content(
        model=model_name or GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema,
        ),
    )

    return (
        response.text
        if response.text
        else ""
    )