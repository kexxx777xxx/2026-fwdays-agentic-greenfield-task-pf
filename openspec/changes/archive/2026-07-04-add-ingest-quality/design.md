# Design — add-ingest-quality

## Goals / Non-goals

**Goals:** chunk boundaries that never break a structural block; deterministic,
idempotent re-index including stale-chunk removal.

**Non-goals:** changing the store schema, the retriever, or the answer layer;
tuning retrieval thresholds (that is `add-eval-harness`).

## Key decisions

- **Parse with markdown-it-py, split between top-level blocks.** Tokenize the
  document; treat each top-level block (paragraph, table, fenced code, list,
  blockquote, hr) as atomic. Greedily pack blocks up to a soft character budget,
  flushing on heading boundaries. A single block larger than the budget is
  emitted whole — integrity wins over size.
- **Heading trail as citation context.** Maintain a stack of `(level, title)`;
  the chunk's `heading` is the `" > "`-joined trail (e.g. `Двигун > Паливо`).
- **Idempotency via delete-then-upsert per file.** For each document, call
  `store.delete_by_source(path)` then upsert its fresh chunks. Combined with
  deterministic `uuid5(path:index)` ids, re-ingesting unchanged content yields an
  identical point set, and a shrunk file cannot leave orphaned higher-index
  chunks.

## Data model

Unchanged from slice 1 (payload `{source_path, heading, chunk_index, text}`). A
new `VectorStore.delete_by_source(source_path)` removes all points for one file
via a payload filter on the indexed `source_path` keyword field.

## Error handling

Store/driver errors continue to surface as `StoreError` (from slice 1). Chunking
is pure and total: malformed markdown still yields whole-block chunks, never a
crash or dropped text.

## Risks & mitigations

- **markdown-it token `map` line ranges** must be sliced correctly against the
  source lines → covered by table/code integrity tests.
- **delete-before-upsert is not transactional** — a crash between them could drop
  a file's chunks; acceptable for a local single-writer ingest, re-runnable.
