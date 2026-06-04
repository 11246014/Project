# services/ai_service.py

from services.ollama_service import ask_ollama


def ask_ai(prompt):

    try:

        return ask_ollama(prompt)

    except Exception as e:

        print(
            f"[AI Error] {e}"
        )

        return """
score: 50
reason: fallback
"""