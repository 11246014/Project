from config.settings import AI_PROVIDER

from services.ollama_service import (
    ask_ollama,
    ask_ollama_structured,
)

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
    
def ask_ai_structured(
    prompt,
    schema,
    model_name=None,
    timeout=120,
):
    try:
        if AI_PROVIDER == "gemini":
            from services.gemini_service import ask_gemini_structured

            return ask_gemini_structured(
                prompt,
                schema=schema,
                model_name=model_name,
            )

        return ask_ollama_structured(
            prompt,
            schema=schema,
            model_name=model_name,
            timeout=timeout,
        )

    except Exception as e:
        print(f"[Structured AI Error] {e}")
        return ""