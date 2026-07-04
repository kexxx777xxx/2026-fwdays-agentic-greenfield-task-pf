# Add sync-and-delivery

## Why

Ingest is a one-shot command; a real "chat with your docs" tool must keep the
index in step with the corpus as files are added, edited, and removed (FR-060).
And the project needs its front door — a README that says what askdocs is and
how to run it (FR-050) — plus the agent operating rules (FR-051). This is the
final MVP slice; after it all 15 shipped FRs are delivered.

## What Changes

- Continuous sync (FR-060): a watcher reconciles the mounted `.md` directory with
  the vector store on a timer — new files are indexed, edited files replaced
  (no stale chunks), deleted files removed. `docker compose up` runs it, so the
  index self-populates and stays fresh with no manual step.
- A `content_hash` per chunk in the store payload so a sync pass skips unchanged
  files instead of re-embedding every cycle.
- `README.md` at the repo root (FR-050): what/why/how-to-run.
- Confirm `AGENTS.md` + `CLAUDE.md` are the agent operating rules (FR-051) —
  authored during the loop install and kept accurate to the stack.

## Impact

- Affected specs (ADDED): new `sync` capability; new `project-docs` capability.
- Affected code: `askdocs/sync.py` (new), `askdocs/store.py` (`content_hash` in
  payload + helper), `docker-compose.yaml` (app command → the watcher),
  `README.md` (new), `tests/test_sync.py`, `tests/test_docs.py`.
- Dependencies: slices 1–2 (chunking + store + idempotent replace). No new
  packages.
