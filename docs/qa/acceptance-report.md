# Acceptance Report — askdocs (rag-hw-pf)

- **Date:** 2026-07-04 (Europe/Kyiv)
- **Scope:** all 15 `shipped` FRs from `docs/prd.md`, delivered across 4 capability
  slices under the Project Factory loop.
- **Result:** all slices implemented, independently reviewed (maker≠checker), and
  archived. Deterministic gates green.

## Requirement coverage

| FR | Requirement | Slice | Evidence |
|---|---|---|---|
| FR-001 | Recursive `.md` ingest via DocSource | add-rag-skeleton | `test_sources.py` |
| FR-002 | Structure-aware chunking (tables/code/lists intact) | add-ingest-quality | `test_chunking.py` (8 cases) |
| FR-003 | Chunks stored with citable source metadata | add-rag-skeleton | `test_ingest.py` |
| FR-004 | Idempotent re-index (no dupes, no stale) | add-ingest-quality | `test_ingest_idempotency.py` |
| FR-010 | Retrieve relevant chunks | add-rag-skeleton | `test_retriever.py` |
| FR-020 | Grounded answer, cites source | add-rag-skeleton | `test_answer.py`; live smoke |
| FR-021 | Honest miss when not in corpus | add-rag-skeleton | `test_answer.py`; live smoke |
| FR-030 | CLI: question → answer + sources | add-rag-skeleton | `test_cli.py` |
| FR-040 | Golden set (20–30 Q) | add-eval-harness | `tests/golden.yaml` (28) |
| FR-041 | Retrieval hit-rate metric | add-eval-harness | `test_eval.py` — measured 95% |
| FR-042 | Anti-hallucination refusal metric | add-eval-harness | `test_eval.py` — measured 100% live |
| FR-050 | README (what/why/how-to-run) | add-sync-and-delivery | `README.md`, `test_docs.py` |
| FR-051 | AGENTS.md / CLAUDE.md | add-sync-and-delivery | `test_docs.py` |
| FR-052 | `docker compose up` runs the system | add-rag-skeleton | `test_deployment.py`; compose |
| FR-060 | Continuous sync (add/change/delete) | add-sync-and-delivery | `test_sync.py` |

Constraints: TC-001..006 honored (Python; DocSource/Retriever/LLMProvider ABCs;
one embedder/store/LLM; all in Docker; Qdrant a separate ephemeral service;
idempotency tests vs clean store). NFR-001/002/004 enforced by the answer layer +
the eval gates; NFR-003 (green pytest) is the done-criterion for every slice.

## Test & quality evidence

- **Battery:** 44 passed, 1 skipped (anti-hallucination, LLM-gated) in-container.
- **Eval (measured):** retrieval hit-rate@5 = 95% (21/22); anti-hallucination
  refusal-rate = 100% (6/6) against a live LLM.
- **Coverage:** lines 74%, statements 75%, branches 70% (ratchet baseline in
  `quality/coverage-baseline.json`). Uncovered code is the `main()`/live-LLM glue
  the deterministic suite intentionally does not exercise.
- **Lint:** ruff clean.
- **Deterministic gates:** traceability PASS (15 MVP FRs, 0 failures),
  trajectory PASS (4 slices audited, 0 failures), openspec validate --all --strict
  PASS (8 specs), coverage ratchet PASS.

## Review (maker≠checker)

Every slice reviewed by independent agents (code-reviewer + spec-compliance-
auditor); evidence in each `openspec/changes/archive/*/review-findings.json`.
Real defects caught and fixed before archive, notably:

- slice 2: setext-heading corruption of the citation trail (major) → fixed.
- slice 4: empty-file perpetual re-add + set-vs-multiset change miss (2 major) → fixed.

All confirmed findings resolved or explicitly accepted with rationale; 0
critical/major left open.

## Out of scope (per PRD)

FR-100..106 and NFR-005 remain `proposed`/`dropped` — not implemented.
