from config.settings import AI_PROVIDER

from services.ollama_service import ask_ollama


def ask_ai(
    prompt,
    model_name=None,
    timeout=120
):
    try:

        if AI_PROVIDER == "gemini":

            from services.gemini_service import ask_gemini

            return ask_gemini(
                prompt,
                model_name=model_name
            )

        return ask_ollama(
            prompt,
            model_name=model_name,
            timeout=timeout
        )

    except Exception as e:

        print(
            f"[AI Error] {e}"
        )

        return ""