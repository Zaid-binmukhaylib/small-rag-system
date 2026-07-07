from src.pdf_reader import extract_data_from_pdf
from src.embeddings import TransformerEmbedder
from src.retriever import Retriever
from src.generator import Generator


class RAGPipeline:
    def __init__(self, resume_path: str):
        self.embedder = TransformerEmbedder()
        self.retriever = Retriever(self.embedder)
        self.generator = Generator()

        resume_text = extract_data_from_pdf(resume_path)
        self.retriever.index(resume_text)

    def answer(self, question: str, history: list | None = None) -> str:
        # Only filter the first question. Follow-up questions rely on the
        # conversation context, so we let them through.
        if not history and not self.retriever.is_relevant(question):
            return "I can only answer questions about the resume."

        return self.generator.generate(
            self.retriever.resume_text,
            question,
            history
        )