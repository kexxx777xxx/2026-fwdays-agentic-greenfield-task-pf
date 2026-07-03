# Current State — askdocs (rag-hw-pf)

- **Date and time:** 2026-07-03 (Europe/Kyiv)
- **Phase:** Slice delivery (Phase 4). Slice 1 archived; slice 2 in progress.

## Where we are

The Project Factory loop is installed and adapted to the Python/Docker stack
(ADR-0001). Requirements are in `docs/requirements.md`; the reordered 4-slice
build order is in `docs/mvp-capability-plan.md`.

| Slice | Capability | FRs | State |
|---|---|---|---|
| 1 | `add-rag-skeleton` | 001, 003, 010, 020, 021, 030, 052 | ✅ archived |
| 2 | `add-ingest-quality` | 002, 004 | ▶ in progress |
| 3 | `add-eval-harness` | 040, 041, 042 | ⏳ planned |
| 4 | `add-sync-and-delivery` | 060, 050, 051 | ⏳ planned |

Slice 1 delivered the end-to-end pipe: DocSource/Retriever/LLMProvider interfaces
(+ one impl each), recursive `.md` ingest with citable metadata, Qdrant retrieval
with a relevance floor, grounded+cited answers with honest misses, the CLI, and
Docker Compose. 20 pytest green in-container, ruff clean, live smoke verified a
real cited answer + a correct honest miss. Reviewed by two independent agents
(0 critical/major; minor findings applied).

## Scope bookkeeping (important)

Requirements use a `Phase` column = the active build front. A `shipped` FR flips
`Future → MVP` when its slice starts, so the traceability chain stays complete at
every commit while specs are authored as per-slice OpenSpec deltas. On archive,
`openspec archive` merges the delta into `openspec/specs/`. Currently MVP:
slices 1 (done) + 2 (active); slices 3–4 FRs still `Future`.

## How to run / validate (everything in the container)

```bash
docker compose build
docker compose run --rm app pytest -q          # full battery (mock LLM; live gated by LLM_LIVE=1)
docker compose run --rm --no-deps app ruff check askdocs tests
docker compose run --rm app python -m askdocs.ingest   # index /corpus
docker compose run --rm app python -m askdocs.cli "<question>"
npx openspec validate --all --strict
node scripts/check-traceability.mjs && node scripts/check-trajectory.mjs
```

## Next step

Slice 2 `add-ingest-quality`: structure-aware chunking (markdown-it-py; tables/
code/lists intact — FR-002) replacing the naive slice-1 chunker, and idempotent
re-index with stale-chunk removal (FR-004), tested against a clean ephemeral
Qdrant (TC-006). Flip FR-002/FR-004 to MVP at slice start.

## Known notes

- Retriever cosine floor `DEFAULT_MIN_SCORE=0.35` is a first cut; real
  calibration is scheduled for slice 3 (`add-eval-harness`).
- A live LLM endpoint (LM-Studio-style at `LLM_BASE_URL`) was available during
  slice-1 smoke; deterministic tests do not need it.
