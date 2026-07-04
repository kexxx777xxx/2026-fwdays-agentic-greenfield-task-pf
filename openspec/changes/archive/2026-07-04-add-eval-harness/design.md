# Design — add-eval-harness

## Goals / Non-goals

**Goals:** an executable, deterministic retrieval gate and an LLM-backed
anti-hallucination gate over a golden set; a documented threshold calibration.

**Non-goals:** changing retrieval/answer behavior; a graded LLM-judge rubric
system (the PRD's eval is retrieval-hit + anti-hallucination, not copy quality).

## Key decisions

- **Golden set as data (`tests/golden.yaml`).** Each entry: `question`,
  `in_corpus` (bool), `source` (file path for in-corpus, null otherwise).
  In-corpus questions target facts that live in exactly one file so hit-rate is
  unambiguous.
- **Two reports, two gates.** `retrieval_report` (deterministic — embeddings +
  Qdrant only) computes hit-rate@k; `hallucination_report` (needs the LLM)
  computes refusal-rate. Pytest asserts each meets a threshold; the
  anti-hallucination test is `LLM_LIVE`-gated so CI stays green without a model.
- **Threshold calibration (measured on this corpus + model).** Retrieval
  hit-rate@5 with the shipped `min_score=0.35` floor is **21/22 = 95%**; the gate
  is set at **0.9** (headroom for one more miss). The single miss is a lexical-
  mismatch question that even raw tops at 0.21. Out-of-corpus questions overlap
  with that band (e.g. an unrelated cooking question tops 0.365), so a pure floor
  cannot separate them — the LLM `NO_ANSWER` guard is the precision layer, which
  is exactly what the anti-hallucination gate measures. Refusal-rate gate: 0.8.

## Data model

No store changes. `GoldenEntry`, `QuestionResult`, `Report` are in-memory
dataclasses; `Report.rate` is the pass fraction, `Report.misses` lists failures
for actionable output.

## Error handling

`load_golden` fails loudly on a malformed entry (missing question/source). The
retrieval report needs no LLM; the honesty report surfaces the LLM's answer text
in the miss detail for debugging.

## Risks & mitigations

- **Embedding nondeterminism** could nudge hit-rate → gate has headroom (0.9 vs
  measured 0.95) and the model runs at a fixed version baked in the image.
- **A live model's refusal quality** varies by model → gate at 0.8, not 1.0, and
  keep it skip-gated so a flaky/absent endpoint never fails deterministic CI.
