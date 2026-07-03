# Design — add-rag-skeleton

## Goals / Non-goals

**Goals:** a working, container-run, end-to-end RAG pipe on a small corpus with
grounded + cited answers and honest misses; the three interfaces as the stable
seam.

**Non-goals (deferred):** structure-aware chunking and idempotent re-index
(→ `add-ingest-quality`); the eval harness (→ `add-eval-harness`); continuous
directory sync and delivery docs (→ `add-sync-and-delivery`).

## Key decisions

- **Interfaces are ABCs; logic never imports a concrete impl** (TC-002). The
  concrete classes (`LocalMarkdownSource`, `VectorRetriever` over `QdrantStore`,
  `OpenAICompatibleProvider`) are wired at the composition edge (CLI / factory
  helpers), so FR-100/101/102 can add impls later without touching the pipeline.
- **Naive chunking now** (split on blank-line/paragraph with a size budget). It
  is explicitly throwaway — `add-ingest-quality` replaces it. Keeping it dumb
  avoids over-building before retrieval/answer are proven.
- **Grounding is prompt- + code-enforced.** The answer prompt is fed only the
  retrieved chunks and instructed to answer solely from them and to say it does
  not know otherwise; when retrieval returns nothing above threshold, the code
  short-circuits to the honest-miss answer without calling the LLM.
- **Determinism for tests.** The answer pipeline takes an injected
  `LLMProvider`; unit tests pass a fake that echoes/asserts the prompt, so
  grounding + citation + honest-miss are tested without a live model. A live
  test is `LLM_LIVE`-gated.
- **Citation source of truth** is chunk metadata (relative path + heading trail
  + index), stored at ingest (FR-003) and surfaced by the answer.

## Data model

Qdrant collection `askdocs` (configurable). Each point: `id` (stable per
file+chunk-index), `vector` (embedding), `payload` = `{ path, heading, index,
text }`. No named volume on the Qdrant service → ephemeral (TC-006).

## Error handling

- Qdrant unreachable / LLM endpoint error → typed error (`StoreError`,
  `LLMError`) with cause; the CLI prints a clear message and exits non-zero,
  never a raw traceback swallowed silently.
- Empty corpus → ingest succeeds, store has zero chunks; a question then yields
  the honest-miss answer (FR-021), not a crash.

## Risks & mitigations

- **Interface shape is load-bearing** for every later slice → keep methods
  minimal and documented; revisit only via ADR.
- **Retrieval threshold** for "nothing relevant" is a judgement call → make it a
  named constant, exercised by the honest-miss test; tune in `add-eval-harness`.
- **Model download at build** inflates image build → baked once in the image
  layer; CI caches the layer.
