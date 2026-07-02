import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


class GeneratorError(Exception):
    pass


class Generator:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-large")
        self.model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-large")
        self.model.eval()

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
Answer:"""

        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.model.generate(**inputs, max_new_tokens=100, do_sample=False)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)