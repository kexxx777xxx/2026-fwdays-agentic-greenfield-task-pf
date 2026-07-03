# ADR-0001: askdocs technology stack

- **Status:** Accepted
- **Date:** 2026-07-03
- **Deciders:** orchestrator + user

## Context

askdocs is a local, corpus-grounded RAG CLI (see `docs/requirements.md`). The
constraints TC-001..TC-006 already fix most of the stack: Python (TC-001); three
interfaces `DocSource`/`Retriever`/`LLMProvider` (TC-002); exactly one embedding
provider, one vector store, one LLM in v1 (TC-003); everything in Docker Compose
with a separate vector-store service and nothing in the host Python
(TC-004/005); idempotency tests against a clean store (TC-006). A working
reference implementation exists at `../rag-hw`, so the concrete picks are proven,
not speculative.

## Decision

We will use:

- **Language/runtime:** Python 3.12 (slim Docker image), non-root container user.
- **Vector store:** **Qdrant** (`qdrant/qdrant`) as a separate Compose service,
  **ephemeral** (no named volume) so ingest idempotency tests always start clean
  (TC-006).
- **Embeddings:** `sentence-transformers` model
  `paraphrase-multilingual-MiniLM-L12-v2` (multilingual — the corpus is
  Ukrainian), baked into the image so containers run without a runtime download.
- **LLM:** one OpenAI-compatible provider over `httpx`
  (`LLM_BASE_URL` default `http://host.docker.internal:1234/v1`,
  `LLM_MODEL` default `google/gemma-4-e4b`); reasoning `<think>` blocks stripped.
- **Chunking:** `markdown-it-py` (structure-aware, tables/code/sections intact).
- **Tests:** `pytest`, run only in the container
  (`docker compose run --rm app pytest`). Deterministic layers use a mock
  `LLMProvider`; live-LLM tests are skip-gated on an env flag.
- **Packaging:** `requirements.txt`, Docker Compose (`app` + `qdrant`).

## Alternatives considered

| Option | Pros | Cons |
|---|---|---|
| Qdrant, separate service (chosen) | Satisfies TC-005; ephemeral = clean idempotency tests | Extra container |
| Embedded store (Chroma in-proc) | Simpler | Violates TC-005 (must be a separate service) |
| Cloud LLM (Claude/GPT) in v1 | Higher answer quality | Out of scope (FR-102, `proposed`); v1 is one local LLM (TC-003) |
| English MiniLM embeddings | Smaller | Corpus is Ukrainian → worse retrieval |

## Consequences

- The three interfaces are the stable seam; concrete impls (Qdrant, ST, OpenAI)
  are swappable behind them, enabling the `proposed` FR-100/101/102 later.
- Baking the model inflates image build time and size, but buys offline,
  reproducible runs (NFR-005 tightens this further, later).
- CI and the git hooks must run Python/Docker, not the Node/Next defaults the
  factory ships with — adapted in this same change.
- A live LLM endpoint is an external dependency; deterministic CI must not need
  it, so grounding/format is tested with a mock and live answers are opt-in.
