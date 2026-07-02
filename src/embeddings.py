import torch
import numpy as np
from transformers import AutoTokenizer, AutoModel


class EmbeddingError(Exception):
    pass


class TransformerEmbedder:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

        self.model = AutoModel.from_pretrained(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

        self.model.eval()

    def create_embedding(self, text: str) -> np.ndarray:
        if not text.strip():
            raise EmbeddingError("Input text is empty.")

        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512
        )

        with torch.no_grad():
            outputs = self.model(**inputs)

        attention_mask = inputs["attention_mask"].unsqueeze(-1)

        embedding = (outputs.last_hidden_state * attention_mask).sum(dim=1)

        embedding = embedding / attention_mask.sum(dim=1).clamp(min=1e-9)

        return embedding.squeeze().numpy()