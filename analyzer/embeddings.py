"""
Embeddings — Tạo vector embeddings cho repos bằng sentence-transformers.
"""
import numpy as np
from typing import Optional

from config import EMBEDDING_MODEL


class EmbeddingGenerator:
    """Tạo embeddings bằng sentence-transformers (chạy local)."""

    def __init__(self):
        self.model = None
        self._model_name = EMBEDDING_MODEL

    def _load_model(self):
        """Lazy load model khi cần."""
        if self.model is None:
            print(f"[Embedding] Đang tải model {self._model_name}...")
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(self._model_name)
                print(f"[Embedding] Model đã sẵn sàng.")
            except ImportError:
                print("[Embedding] CẢNH BÁO: sentence-transformers chưa cài.")
                print("[Embedding] Chạy: pip install sentence-transformers")
                self.model = None
            except Exception as e:
                print(f"[Embedding] Lỗi tải model: {e}")
                self.model = None

    def generate(self, text: str) -> Optional[list[float]]:
        """Tạo embedding cho 1 đoạn text."""
        self._load_model()
        if self.model is None:
            return None

        try:
            embedding = self.model.encode(text, show_progress_bar=False)
            return embedding.tolist()
        except Exception as e:
            print(f"[Embedding] Lỗi encode: {e}")
            return None

    def generate_batch(self, texts: list[str], batch_size: int = 32) -> list[Optional[list[float]]]:
        """Tạo embeddings cho nhiều texts cùng lúc."""
        self._load_model()
        if self.model is None:
            return [None] * len(texts)

        try:
            # Lọc texts rỗng
            valid_indices = [i for i, t in enumerate(texts) if t and t.strip()]
            valid_texts = [texts[i] for i in valid_indices]

            if not valid_texts:
                return [None] * len(texts)

            # Batch encode
            print(f"[Embedding] Encoding {len(valid_texts)} texts...")
            embeddings = self.model.encode(
                valid_texts,
                batch_size=batch_size,
                show_progress_bar=True,
            )

            # Map lại kết quả
            result = [None] * len(texts)
            for idx, emb in zip(valid_indices, embeddings):
                result[idx] = emb.tolist()

            return result
        except Exception as e:
            print(f"[Embedding] Lỗi batch encode: {e}")
            return [None] * len(texts)

    def compute_similarity(self, emb1: list[float], emb2: list[float]) -> float:
        """Tính cosine similarity giữa 2 embeddings."""
        a = np.array(emb1)
        b = np.array(emb2)
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))


# Singleton instance
_embedding_generator = None

def get_embedding_generator() -> EmbeddingGenerator:
    global _embedding_generator
    if _embedding_generator is None:
        _embedding_generator = EmbeddingGenerator()
    return _embedding_generator
