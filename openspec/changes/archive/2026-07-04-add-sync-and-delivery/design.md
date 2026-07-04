# Design — add-sync-and-delivery

## Goals / Non-goals

**Goals:** a robust continuous reconciliation of a mounted `.md` directory with
the store (add/update/delete), started by `docker compose up`; the delivery docs.

**Non-goals:** filesystem-event (inotify) watching, real-time push, multi-corpus
projects (FR-105, future), a web UI (FR-103, future).

## Key decisions

- **Poll + diff, not inotify.** Bind-mount filesystem events are unreliable
  across the host→container boundary, so a timed reconciliation loop is the
  robust choice. Interval is `ASKDOCS_SYNC_INTERVAL` (default 5s), validated
  (reject non-numeric, ≤0, inf, nan — an inf interval would hang `sleep`).
- **Change detection via `content_hash`.** Each chunk's payload carries a
  `content_hash`; a pass compares the set of hashes on disk vs in the store per
  file. Unchanged files are skipped (no re-embedding); new/changed files are
  replaced wholesale (reusing the idempotent delete-then-upsert); files gone from
  disk have their chunks deleted.
- **The watcher must not die on a transient failure.** A failed pass (e.g. a
  vector-store blip) is logged and the loop continues, so sync stays continuous.
  `watch(..., max_iterations=N)` bounds the loop for tests.
- **`docker compose up` runs the watcher** (`command: python -m askdocs.sync`),
  which waits for Qdrant first — so a single command brings up a self-populating,
  self-freshening system (closes FR-052's "no manual steps" for real usage).

## Data model

Adds `content_hash` (sha256 of chunk text) to the existing payload
(`source_path, heading, chunk_index, text, content_hash`). Backward compatible:
retrieval/answer ignore it.

## Error handling

`_parse_interval` degrades to the default on bad input rather than crashing at
startup. `watch` catches per-pass exceptions and retries next tick. `main` waits
for Qdrant with a timeout before starting.

## Risks & mitigations

- **Re-embedding cost** if change detection is wrong → hashes compared per file;
  a no-op pass does zero embeds (tested).
- **A delete during a query** → deletes are wholesale per file and the store is
  single-writer; acceptable for local use.
