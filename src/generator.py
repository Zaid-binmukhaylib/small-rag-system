import os
import time

from google import genai
from google.genai import errors


class GeneratorError(Exception):
    pass


class Generator:
    # Tried in order; if one is rate-limited/overloaded, fall back to the next.
    # Only free-tier models are listed here.
    FALLBACK_MODELS = [
        "gemini-2.5-flash-lite",
        "gemini-2.0-flash-lite",
        "gemini-2.5-flash",
    ]

    def __init__(self, model: str | None = None, max_retries: int = 3):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise GeneratorError(
                "GEMINI_API_KEY environment variable is not set."
            )

        # If a specific model is given, try it first, then the fallbacks.
        self.models = [model] + self.FALLBACK_MODELS if model else self.FALLBACK_MODELS
        self.max_retries = max_retries
        self.client = genai.Client(api_key=api_key)

    def generate(self, resume_text: str, question: str) -> str:
        if not resume_text.strip():
            raise GeneratorError("Resume text is empty.")

        if not question.strip():
            raise GeneratorError("Question is empty.")

        prompt = f"""Answer the question using only the information in the resume.
If the answer is not found in the resume, reply:
"I couldn't find that information in the resume."

Resume:
{resume_text}

Question:
{question}

Answer:
"""

        last_error = None
        for model in self.models:
            for attempt in range(self.max_retries):
                try:
                    response = self.client.models.generate_content(
                        model=model,
                        contents=prompt,
                    )
                    return response.text
                except errors.ServerError as e:
                    # 503 / overloaded — wait and retry the same model.
                    last_error = e
                    time.sleep(2 * (attempt + 1))
                except errors.ClientError as e:
                    # 429 rate limit — move on to the next fallback model.
                    last_error = e
                    break

        raise GeneratorError(
            f"All models failed to generate an answer. Last error: {last_error}"
        )
