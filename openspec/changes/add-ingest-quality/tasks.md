## 1. Failing tests first (red) — written from the spec, before implementation
- [ ] 1.1 `tests/test_chunking.py`: table intact, fenced code intact, oversized section splits on block boundaries, heading trail present. Unit (markdown-it only). `@trace FR-002`.
- [ ] 1.2 `tests/test_ingest_idempotency.py`: re-ingest unchanged corpus → identical count + contents; shrunk file → no stale chunks. Integration, `clean_store`. `@trace FR-004, TC-006`.
- [ ] 1.3 Run them — confirm RED.

## 2. Structure-aware chunking (green) — FR-002
- [ ] 2.1 Rewrite `askdocs/chunking.py` with markdown-it-py: parse top-level blocks, keep tables/code/lists atomic, pack to a soft budget on block boundaries, build the heading trail.
- [ ] 2.2 Keep the `Chunk` payload fields stable (source_path, heading, chunk_index, text) so store/retriever are unchanged.

## 3. Idempotent ingest (green) — FR-004
- [ ] 3.1 Add `VectorStore.delete_by_source` + `QdrantStore.delete_by_source` (filter on the indexed source_path).
- [ ] 3.2 Update `askdocs/ingest.py`: for each file, delete-then-upsert its fresh chunks.

## 4. Validation and archive prep
- [ ] 4.1 `docker compose run --rm app pytest -q` — all green.
- [ ] 4.2 `docker compose run --rm --no-deps app ruff check askdocs tests`.
- [ ] 4.3 `npx openspec validate add-ingest-quality --strict` and `--all --strict`.
- [ ] 4.4 `node scripts/check-traceability.mjs` — FR-002/FR-004 in the chain.
- [ ] 4.5 Review-gate (code-reviewer + spec-compliance-auditor); fix confirmed findings; re-run 4.1–4.4.
- [ ] 4.6 Manual container smoke: ingest twice, confirm stable count; edit a file shorter, re-ingest, confirm no stale chunks.
- [ ] 4.7 Archive after 4.1–4.6 pass: `npx openspec archive add-ingest-quality --yes`; record review-findings.json.
