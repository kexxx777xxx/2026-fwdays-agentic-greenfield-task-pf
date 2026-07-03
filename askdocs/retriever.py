"""Retriever interface and the v1 vector implementation (FR-010).

Retrieval goes through the interface so the concrete vector search can be
swapped later (FR-101). A relevance floor (`min_score`) is applied here so a
question with no semantically relevant chunk yields an EMPTY result — which the
answer layer turns into an honest miss (FR-021) without calling the model.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from askdocs.embeddings import EmbeddingProvider
from askdocs.store import VectorStore

DEFAULT_TOP_K = 5
# Cosine floor. Measured on the ГущоЛіт corpus with paraphrase-multilingual-
# MiniLM: in-corpus questions top ~0.48–0.72, clearly-unrelated ones ~0.10–0.20.
# 0.35 separates those. Semantic false-friends (e.g. an unrelated question that
# still mentions a temperature) can slip above the floor; the answer layer's
# NO_ANSWER guard is the second line of defense. Tuned properly in add-eval-harness.
DEFAULT_MIN_SCORE = 0.35


@dataclass(frozen=True)
class RetrievedChunk:
    text: str
    source_path: str
    heading: str
    chunk_index: int
    score: float


class Retriever(ABC):
    """Interface: "find chunks relevant to a question"."""

    @abstractmethod
    def retrieve(self, question: str, k: int = DEFAULT_TOP_K) -> list[RetrievedChunk]: ...


class VectorRetriever(Retriever):
    def __init__(
        self,
        embedder: EmbeddingProvider,
        store: VectorStore,
        min_score: float = DEFAULT_MIN_SCORE,
    ) -> None:
        self._embedder = embedder
        self._store = store
        self._min_score = min_score

    def retrieve(self, question: str, k: int = DEFAULT_TOP_K) -> list[RetrievedChunk]:
        [vector] = self._embedder.embed([question])
        results = [
            RetrievedChunk(
                text=payload["text"],
                source_path=payload["source_path"],
                heading=payload.get("heading", ""),
                chunk_index=payload.get("chunk_index", 0),
                score=score,
            )
            for payload, score in self._store.search(vector, limit=k)
            # skip low-relevance or malformed points (foreign data without a
            # source is not citable — NFR-001)
            if score >= self._min_score and payload.get("text") and payload.get("source_path")
        ]
        # store.search already returns most-relevant first; keep that order.
        return results
