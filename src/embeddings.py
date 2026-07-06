import os

import numpy as np
from google import genai


class EmbeddingError(Exception):
    pass


class GeminiEmbedder:
    def __init__(self, model: str = "gemini-embedding-001"):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise EmbeddingError(
                "GEMINI_API_KEY environment variable is not set."
            )

        self.model = model
        self.client = genai.Client(api_key=api_key)

    def create_embedding(self, text: str) -> np.ndarray:
        if not text.strip():
            raise EmbeddingError("Input text is empty.")

        try:
            result = self.client.models.embed_content(
                model=self.model,
                contents=text,
            )
        except Exception as e:
            raise EmbeddingError(f"Failed to create embedding: {e}")

        return np.array(result.embeddings[0].values, dtype=np.float32)
