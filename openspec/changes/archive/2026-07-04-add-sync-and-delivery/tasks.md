## 1. Failing tests first (red) — written from the spec, before implementation
- [x] 1.1 `tests/test_sync.py`: new/edited/deleted/no-op passes (integration); watcher survives a failing pass + interval parsing (unit). `@trace FR-060`.
- [x] 1.2 `tests/test_docs.py`: README exists with purpose + run commands (`@trace FR-050`); AGENTS.md + CLAUDE.md present and wired (`@trace FR-051`).
- [x] 1.3 Run them — confirm RED.

## 2. Sync (green) — FR-060
- [x] 2.1 `askdocs/store.py`: add `content_hash` helper + store it in the chunk payload.
- [x] 2.2 `askdocs/sync.py`: `sync_once` (diff disk vs store by content_hash: add/update/delete), `watch` (timed loop, survives failures, bounded for tests), `_parse_interval` (validate), `main` (wait for Qdrant, watch).
- [x] 2.3 `docker-compose.yaml`: app `command: python -m askdocs.sync` so `up` self-populates.

## 3. Delivery docs (green) — FR-050, FR-051
- [x] 3.1 `README.md`: what/why/how-to-run (build, ingest/sync, ask), corpus drop-point, dev/validation commands.
- [x] 3.2 Confirm `AGENTS.md` + `CLAUDE.md` are accurate to the stack (already authored in the loop install).

## 4. Validation and archive prep
- [x] 4.1 `docker compose run --rm app pytest -q` — all green.
- [x] 4.2 `docker compose run --rm --no-deps app ruff check askdocs tests`.
- [x] 4.3 `npx openspec validate add-sync-and-delivery --strict` and `--all --strict`.
- [x] 4.4 `node scripts/check-traceability.mjs` — FR-050/051/060 in the chain (all 15 FRs now MVP).
- [x] 4.5 Review-gate (code-reviewer + spec-compliance-auditor); fix confirmed findings; re-run.
- [x] 4.6 Manual smoke: `docker compose up` self-populates; add/edit/delete a corpus file and observe reconciliation.
- [x] 4.7 Archive after passing: `npx openspec archive add-sync-and-delivery --yes`; record review-findings.json.
