from ollama import chat


class GeneratorError(Exception):
    pass


class Generator:
    def __init__(self, model: str = "qwen3:8b"):
        self.model = model

    def generate(self, resume_text: str, question: str, history: list | None = None) -> str:
        if not resume_text.strip():
            raise GeneratorError("Resume text is empty.")

        if not question.strip():
            raise GeneratorError("Question is empty.")

        system_prompt = f"""You are an assistant that answers questions about the resume below.
Use only the information in the resume. If the answer is not found in the resume, reply:
"I couldn't find that information in the resume."
Take the previous conversation into account when answering follow-up questions.

Resume:
{resume_text}
"""

        # Build the multi-turn message list: system + past conversation + new question.
        messages = [{"role": "system", "content": system_prompt}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": question})

        response = chat(
            model=self.model,
            messages=messages,
            think=False
        )

        return response.message.content