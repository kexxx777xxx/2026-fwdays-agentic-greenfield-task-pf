"""@trace FR-010 — retrieve finds relevant chunks, ordered, empty on no-match.

Integration: needs the Qdrant service and the real embedding model.
"""

import pytest

from askdocs.ingest import ingest_source
from askdocs.retriever import VectorRetriever
from askdocs.sources import LocalMarkdownSource

pytestmark = pytest.mark.integration


@pytest.fixture
def retriever(clean_store, embedder, corpus_dir):
    ingest_source(LocalMarkdownSource(corpus_dir), embedder, clean_store)
    return VectorRetriever(embedder, clean_store)


def test_relevant_chunk_retrieved(retriever):
    # The corpus says the ГущоЛіт engine runs on fermented coffee grounds.
    results = retriever.retrieve("З чого зроблений двигун ГущоЛіт?")
    assert results, "expected at least one relevant chunk"
    joined = " ".join(r.text for r in results).lower()
    assert "гущ" in joined or "паливо" in joined or "двигун" in joined
    for r in results:
        assert r.source_path.endswith(".md")


def test_results_ordered_by_score(retriever):
    results = retriever.retrieve("Хто входить до екіпажу ГущоЛіт?")
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)


def test_no_relevant_chunks_returns_empty(retriever):
    # A question with no bearing on the ГущоЛіт corpus scores far below the floor.
    results = retriever.retrieve("How do I cook Italian pasta carbonara at home?")
    assert results == []
