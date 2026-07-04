# Current State — askdocs (rag-hw-pf)

- **Date and time:** 2026-07-04 (Europe/Kyiv)
- **Phase:** MVP delivered. All 4 capability slices archived; deterministic gates green.

## Where we are

All 15 `shipped` FRs from the PRD are implemented, reviewed (maker≠checker), and
archived under the Project Factory loop. See `docs/qa/acceptance-report.md` for
the full FR→evidence matrix.

| Slice | Capability | FRs | State |
|---|---|---|---|
| 1 | `add-rag-skeleton` | 001, 003, 010, 020, 021, 030, 052 | ✅ archived |
| 2 | `add-ingest-quality` | 002, 004 | ✅ archived |
| 3 | `add-eval-harness` | 040, 041, 042 | ✅ archived |
| 4 | `add-sync-and-delivery` | 060, 050, 051 | ✅ archived |

## Quality snapshot

- pytest: 44 passed, 1 skipped (anti-hallucination is LLM-gated) in-container.
- eval (measured): retrieval hit-rate 95%, anti-hallucination refusal 100% (live).
- coverage: lines 74% / branches 70% (ratchet baseline committed).
- gates: traceability, trajectory, openspec --all --strict, coverage — all PASS.

## How to run / validate (everything in the container)

```bash
docker compose build
docker compose up                                   # sync watcher self-populates /corpus
docker compose run --rm app python -m askdocs.cli "<question>"
docker compose run --rm app python -m askdocs.eval  # quality report
docker compose run --rm app pytest -q               # battery (LLM_LIVE=1 to include the live gate)
npx openspec validate --all --strict
node scripts/check-traceability.mjs && node scripts/check-trajectory.mjs
npm run test:coverage && node scripts/check-coverage-ratchet.mjs
```

## Next steps (post-MVP, all `proposed`)

- FR-105 multi-corpus projects; FR-106 richer per-quote citations; NFR-005
  fully-offline embeddings (`HF_HUB_OFFLINE=1`). FR-100/101/102/103 add new
  DocSource/Retriever/LLMProvider/UI behind the existing interfaces.
- Retrieval floor (`DEFAULT_MIN_SCORE=0.35`) can be revisited against a larger
  golden set if hit-rate needs to rise past 95%.

## Notes

- G1 (requirements sign-off) and G3 (capability-plan sign-off) are human
  judgment gates — confirm in review before calling the release final.
- The factory's separate TS eval-judge system is intentionally unused; the PRD's
  eval (FR-040/041/042) is delivered as the pytest gate + `askdocs/eval.py`.
