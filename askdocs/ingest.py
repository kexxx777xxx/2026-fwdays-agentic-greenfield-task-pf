"""Ingest orchestration: DocSource -> chunk -> embed -> VectorStore (FR-001, FR-003).

Slice 1 does a straight load-and-upsert. Idempotent re-index with stale-chunk
removal is added in `add-ingest-quality` (FR-004).
"""

import os
import sys

from askdocs.chunking import chunk_document
from askdocs.embeddings import EmbeddingProvider
from askdocs.sources import DocSource
from askdocs.store import VectorStore

DEFAULT_COLLECTION = "askdocs"


def ingest_source(source: DocSource, embedder: EmbeddingProvider, store: VectorStore) -> int:
    """Chunk every document from the source, embed, and upsert. Returns chunk count."""
    chunks = []
    for doc in source.documents():
        chunks.extend(chunk_document(doc.source_path, doc.text))
    if chunks:
        vectors = embedder.embed([chunk.text for chunk in chunks])
        store.upsert(chunks, vectors)
    return len(chunks)


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    corpus = argv[0] if argv else os.environ.get("ASKDOCS_CORPUS", "/corpus")

    from askdocs.embeddings import SentenceTransformersProvider
    from askdocs.sources import LocalMarkdownSource
    from askdocs.store import QdrantStore

    embedder = SentenceTransformersProvider()
    store = QdrantStore(
        url=os.environ.get("QDRANT_URL", "http://localhost:6333"),
        collection=os.environ.get("ASKDOCS_COLLECTION", DEFAULT_COLLECTION),
        dimension=embedder.dimension,
    )
    count = ingest_source(LocalMarkdownSource(corpus), embedder, store)
    print(f"ingested {count} chunk(s) from {corpus}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
