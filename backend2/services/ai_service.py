import os

from dotenv import load_dotenv

from config.settings import AI_PROVIDER

from services.ollama_service import ask_ollama

load_dotenv()

# =====================
# Gemini 初始化
# =====================

if AI_PROVIDER == "gemini":

    import google.generativeai as genai

    genai.configure(
        api_key=os.getenv(
            "GEMINI_API_KEY"
        )
    )

    gemini_model = (
        genai.GenerativeModel(
            "gemini-2.5-flash"
        )
    )


def ask_ai(
    prompt,
    model_name=None
):

    try:

        # =====================
        # Gemini
        # =====================

        if AI_PROVIDER == "gemini":

            response = (
                gemini_model.generate_content(
                    prompt
                )
            )

            return (
                response.text
                if response.text
                else ""
            )

        # =====================
        # Ollama
        # =====================

        return ask_ollama(
            prompt,
            model_name=model_name
        )

    except Exception as e:

        print(
            f"[AI Error] {e}"
        )

        return ""