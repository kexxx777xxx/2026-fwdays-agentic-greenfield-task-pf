"""@trace FR-004, TC-006 — re-index is idempotent; shrunk files leave no stale chunks.

Integration: needs the Qdrant service and the real embedding model, against a
collection dropped before each test (clean_store).
"""

import pytest

from askdocs.ingest import ingest_source
from askdocs.sources import LocalMarkdownSource

pytestmark = pytest.mark.integration


def _snapshot(store):
    return sorted((p["source_path"], p["chunk_index"], p["text"]) for _id, p in store.get_all())


def test_reingest_of_unchanged_corpus_is_identical(clean_store, embedder, corpus_dir):
    n1 = ingest_source(LocalMarkdownSource(corpus_dir), embedder, clean_store)
    snap1 = _snapshot(clean_store)
    n2 = ingest_source(LocalMarkdownSource(corpus_dir), embedder, clean_store)
    snap2 = _snapshot(clean_store)

    assert n1 == n2
    assert clean_store.count() == n1  # no duplicates after the second run
    assert snap1 == snap2  # same chunk set, same content


def test_shrunk_file_leaves_no_stale_chunks(clean_store, embedder, tmp_path):
    doc = tmp_path / "doc.md"
    doc.write_text(
        "# H\n\n" + "\n\n".join(f"Абзац номер {i} з текстом про ГущоЛіт." for i in range(80)),
        encoding="utf-8",
    )
    source = LocalMarkdownSource(tmp_path)

    ingest_source(source, embedder, clean_store)
    big_count = clean_store.count()
    assert big_count > 1  # the long file produced several chunks

    # edit the file so it produces far fewer chunks
    doc.write_text("# H\n\nКоротко.\n", encoding="utf-8")
    ingest_source(source, embedder, clean_store)

    snap = _snapshot(clean_store)
    assert clean_store.count() < big_count  # stale chunks were removed
    assert all(source_path == "doc.md" for source_path, _i, _t in snap)
    assert any("Коротко." in text for _sp, _i, text in snap)
    assert not any("Абзац номер 79" in text for _sp, _i, text in snap)  # no leftover
