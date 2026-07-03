# Add ingest-quality

## Why

The skeleton's chunker splits on blank lines with a size budget — it can cut a
markdown table or fenced code block in half, which corrupts both retrieval and
the cited context. And ingest currently only upserts, so a shrunk or edited file
leaves stale chunks behind. This slice makes ingestion trustworthy: structure-
aware chunking (FR-002) and idempotent re-index (FR-004).

## What Changes

- Replace the naive chunker with a structure-aware one (markdown-it-py): split
  only on markdown block boundaries; a table, fenced code block, or list group
  is never cut mid-block; an atomic block larger than the budget stays whole; the
  heading trail is the chunk's citation context (FR-002).
- Make ingest idempotent (FR-004): re-indexing an unchanged corpus yields the
  same chunk set (no duplicates); when a file changes or shrinks, its old chunks
  are replaced and sections that no longer exist leave no stale chunks.
- Idempotency tests run against a clean, ephemeral Qdrant (TC-006).

## Impact

- Affected specs (ADDED to baseline `ingest`): structural-integrity + idempotency
  requirements.
- Affected code: `askdocs/chunking.py` (rewritten structure-aware),
  `askdocs/ingest.py` (delete-then-upsert per file), `askdocs/store.py`
  (`delete_by_source`), `tests/test_chunking.py`, `tests/test_ingest_idempotency.py`.
- Dependencies: slice 1 (`add-rag-skeleton`). No new packages (markdown-it-py
  already in `requirements.txt`).
