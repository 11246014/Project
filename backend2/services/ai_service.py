# services/ai_service.py

from services.gemini_service import ask_gemini
from services.ollama_service import ask_ollama


USE_GEMINI = True


def ask_ai(
    prompt,
    model_name=None
):

    try:

        # =====================
        # Gemini
        # =====================

        if USE_GEMINI:

            return ask_gemini(
                prompt
            )

        # =====================
        # Ollama Fallback
        # =====================

        return ask_ollama(
            prompt,
            model_name=model_name
        )

    except Exception as e:

        print(
            f"[AI Error] {e}"
        )

        try:

            print(
                "[Fallback Ollama]"
            )

            return ask_ollama(
                prompt,
                model_name=model_name
            )

        except Exception as e:

            print(
                f"[Fallback Error] {e}"
            )

            return """
score: 50
reason: fallback
"""