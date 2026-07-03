"""@trace FR-003 — ingest stores chunks with source metadata for citation.

Integration: needs the Qdrant service and the real embedding model.
"""

import pytest

from askdocs.ingest import ingest_source
from askdocs.sources import LocalMarkdownSource

pytestmark = pytest.mark.integration


def test_chunks_stored_with_source_metadata(clean_store, embedder, corpus_dir):
    count = ingest_source(LocalMarkdownSource(corpus_dir), embedder, clean_store)
    assert count > 0
    assert clean_store.count() == count

    payloads = [payload for _id, payload in clean_store.get_all()]
    assert payloads
    for payload in payloads:
        # metadata sufficient to cite: relative path, heading trail, chunk index
        assert payload["source_path"].endswith(".md")
        assert "heading" in payload
        assert isinstance(payload["chunk_index"], int)
        assert payload["text"].strip()

    # a known source file is represented
    assert any(p["source_path"] == "proekt.md" for p in payloads)


def test_empty_corpus_stores_nothing(clean_store, embedder, tmp_path):
    count = ingest_source(LocalMarkdownSource(tmp_path), embedder, clean_store)
    assert count == 0
    assert clean_store.count() == 0
