"""VectorStore interface and the v1 Qdrant implementation (FR-003, TC-005)."""

import uuid
from abc import ABC, abstractmethod

from qdrant_client import QdrantClient, models

from askdocs.chunking import Chunk

# Fixed namespace so chunk IDs are deterministic across runs — re-upserting the
# same (file, chunk index) overwrites rather than duplicates.
_ID_NAMESPACE = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")


class StoreError(RuntimeError):
    """Raised when the vector store is unreachable or rejects an operation."""


def chunk_id(chunk: Chunk) -> str:
    return str(uuid.uuid5(_ID_NAMESPACE, f"{chunk.source_path}:{chunk.chunk_index}"))


class VectorStore(ABC):
    """Interface: "persist and look up chunk vectors"."""

    @abstractmethod
    def upsert(self, chunks: list[Chunk], vectors: list[list[float]]) -> None: ...

    @abstractmethod
    def count(self) -> int: ...

    @abstractmethod
    def get_all(self) -> list[tuple[str, dict]]:
        """Return (id, payload) for every stored chunk."""

    @abstractmethod
    def search(self, vector: list[float], limit: int) -> list[tuple[dict, float]]:
        """Return (payload, similarity score) for the most similar chunks."""


class QdrantStore(VectorStore):
    def __init__(self, url: str, collection: str, dimension: int) -> None:
        try:
            self._client = QdrantClient(url=url)
            self._collection = collection
            if not self._client.collection_exists(collection):
                self._client.create_collection(
                    collection_name=collection,
                    vectors_config=models.VectorParams(
                        size=dimension, distance=models.Distance.COSINE
                    ),
                )
                self._client.create_payload_index(
                    collection_name=collection,
                    field_name="source_path",
                    field_schema=models.PayloadSchemaType.KEYWORD,
                )
        except Exception as e:  # noqa: BLE001 — translate driver errors to a typed one
            raise StoreError(f"cannot reach vector store at {url}: {e}") from e

    def upsert(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        points = [
            models.PointStruct(
                id=chunk_id(chunk),
                vector=vector,
                payload={
                    "source_path": chunk.source_path,
                    "heading": chunk.heading,
                    "chunk_index": chunk.chunk_index,
                    "text": chunk.text,
                },
            )
            for chunk, vector in zip(chunks, vectors, strict=True)
        ]
        if points:
            self._client.upsert(self._collection, points=points, wait=True)

    def count(self) -> int:
        return self._client.count(self._collection, exact=True).count

    def get_all(self) -> list[tuple[str, dict]]:
        points: list[tuple[str, dict]] = []
        offset = None
        while True:
            batch, offset = self._client.scroll(
                self._collection, limit=256, offset=offset, with_payload=True
            )
            points.extend((str(p.id), p.payload) for p in batch)
            if offset is None:
                return points

    def search(self, vector: list[float], limit: int) -> list[tuple[dict, float]]:
        hits = self._client.query_points(
            self._collection, query=vector, limit=limit, with_payload=True
        ).points
        return [(hit.payload, hit.score) for hit in hits]
