## 1. Failing tests first (red) — written from the spec, before implementation
- [ ] 1.1 `tests/golden.yaml`: 20–30 ГущоЛіт questions (in-corpus with source, out-of-corpus without). `@trace FR-040`.
- [ ] 1.2 `tests/test_eval.py`: golden well-formedness (`@trace FR-040`); retrieval hit-rate ≥ threshold (`@trace FR-041`); anti-hallucination refusal-rate ≥ threshold, LLM_LIVE-gated (`@trace FR-042`).
- [ ] 1.3 Run them — confirm RED (eval module missing).

## 2. Eval harness (green)
- [ ] 2.1 `askdocs/eval.py`: `load_golden`, `retrieval_report` (hit-rate@k), `hallucination_report` (refusal-rate via answer pipeline), `Report` with rate + misses.
- [ ] 2.2 `python -m askdocs.eval` prints both reports (ingests the corpus, wires the pipeline).
- [ ] 2.3 Set committed thresholds from measured numbers (retrieval 0.9, refusal 0.8) — documented in design.md.

## 3. Validation and archive prep
- [ ] 3.1 `docker compose run --rm app pytest -q` — green (anti-hallucination skipped without LLM).
- [ ] 3.2 `docker compose run --rm --no-deps app ruff check askdocs tests`.
- [ ] 3.3 `LLM_LIVE=1 docker compose run --rm -e LLM_LIVE=1 app pytest -q -k eval` — confirm the anti-hallucination gate passes with a live model.
- [ ] 3.4 `npx openspec validate add-eval-harness --strict` and `--all --strict`.
- [ ] 3.5 `node scripts/check-traceability.mjs` — FR-040/041/042 in the chain.
- [ ] 3.6 Review-gate (code-reviewer + spec-compliance-auditor); fix confirmed findings; re-run.
- [ ] 3.7 Manual: `docker compose run --rm app python -m askdocs.eval` shows the report.
- [ ] 3.8 Archive after passing: `npx openspec archive add-eval-harness --yes`; record review-findings.json.
