import numpy as np
from src.embeddings import TransformerEmbedder


class RetrieverError(Exception):
    pass


class Retriever:
    def __init__(self, embedder: TransformerEmbedder, threshold: float = 0.2):
        self.embedder = embedder
        self.threshold = threshold
        self.resume_embedding = None
        self.resume_text = None

    def index(self, resume_text: str):
        if not resume_text.strip():
            raise RetrieverError("Resume text is empty.")

        self.resume_text = resume_text
        self.resume_embedding = self.embedder.create_embedding(resume_text)

    def similarity_score(self, query: str) -> float:
        if self.resume_embedding is None:
            raise RetrieverError("Resume has not been indexed.")

        query_embedding = self.embedder.create_embedding(query)

        return self._cosine_similarity(
            self.resume_embedding,
            query_embedding
        )

    def is_relevant(self, query: str) -> bool:
        return self.similarity_score(query) >= self.threshold

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        norm_vec1 = np.linalg.norm(vec1)
        norm_vec2 = np.linalg.norm(vec2)

        if norm_vec1 == 0 or norm_vec2 == 0:
            return 0.0

        return float(
            np.dot(vec1, vec2) / (norm_vec1 * norm_vec2)
        )