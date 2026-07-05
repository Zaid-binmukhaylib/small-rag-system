from ollama import chat


class GeneratorError(Exception):
    pass


class Generator:
    def __init__(self, model: str = "qwen3:8b"):
        self.model = model

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

        response = chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            think=False
        )

        return response.message.content