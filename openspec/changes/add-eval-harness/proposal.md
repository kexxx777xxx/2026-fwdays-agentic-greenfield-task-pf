# Add eval-harness

## Why

Unit tests assert individual behaviors, but "does retrieval actually find the
right chunk?" and "does the system refuse out-of-corpus questions instead of
hallucinating?" are quality properties that need a graded, corpus-wide gate.
This slice adds an executable eval harness over a golden set (FR-040), a
retrieval hit-rate metric (FR-041), and an anti-hallucination refusal-rate metric
(FR-042). It also fixes the retrieval threshold calibration deferred from earlier
slices, with real measured numbers.

## What Changes

- A golden set of 20–30 questions over ГущоЛіт (FR-040): in-corpus questions with
  their expected source file, and out-of-corpus questions expecting an honest
  miss. Lives in `tests/golden.yaml`.
- A retrieval metric (FR-041): for each in-corpus question, assert the expected
  source appears among the top-k retrieved chunks; report a hit-rate and gate on
  a threshold.
- An anti-hallucination metric (FR-042): for each out-of-corpus question, assert
  the system refuses (`found=False`); report a refusal-rate and gate on a
  threshold. This exercises the real LLM, so it is skip-gated on `LLM_LIVE=1`.
- `askdocs/eval.py` runnable as `python -m askdocs.eval` for a human-readable
  report; pytest gates enforce the thresholds (NFR-003).

## Impact

- Affected specs (ADDED): new `eval` capability.
- Affected code: `askdocs/eval.py`, `tests/golden.yaml`, `tests/test_eval.py`.
- Dependencies: slices 1–2 (retrieval + quality ingest). No new packages.
