"""EmbeddingProvider interface and the v1 sentence-transformers implementation.

The model name lives here and ONLY here (single source of truth); the Dockerfile
bakes it by instantiating this provider.
"""

from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    """Interface: "turn text into vectors"."""

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]: ...

    @property
    @abstractmethod
    def dimension(self) -> int: ...


class SentenceTransformersProvider(EmbeddingProvider):
    MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

    def __init__(self) -> None:
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer(self.MODEL_NAME)

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [vector.tolist() for vector in self._model.encode(texts)]

    @property
    def dimension(self) -> int:
        # Method was renamed get_sentence_embedding_dimension -> get_embedding_dimension
        # across versions; prefer the new name, fall back for older installs.
        getter = getattr(self._model, "get_embedding_dimension", None) or (
            self._model.get_sentence_embedding_dimension
        )
        dim = getter()
        return dim if dim is not None else len(self.embed(["x"])[0])
