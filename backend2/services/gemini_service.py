import os
import time

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

    model = model_name or GEMINI_MODEL

    # ==================================================
    # Gemini Debug
    # ==================================================

    start_time = time.perf_counter()

    print(
        f"[Gemini] Request Start | "
        f"model={model} | "
        f"prompt_len={len(prompt)}"
    )

    # ==================================================
    # Gemini Request
    # ==================================================

    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )

    # ==================================================
    # Gemini Timing
    # ==================================================

    elapsed = time.perf_counter() - start_time

    print(
        f"[Gemini] Request Time: {elapsed:.2f}s"
    )

    # ==================================================
    # Response
    # ==================================================

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

    model = model_name or GEMINI_MODEL

    start_time = time.perf_counter()

    print(
        f"[Gemini Structured] Request Start | "
        f"model={model} | "
        f"prompt_len={len(prompt)}"
    )

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema,
        ),
    )

    elapsed = time.perf_counter() - start_time

    print(
        f"[Gemini Structured] Request Time: "
        f"{elapsed:.2f}s"
    )

    return (
        response.text
        if response.text
        else ""
    )