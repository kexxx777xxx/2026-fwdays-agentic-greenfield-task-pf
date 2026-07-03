# Add rag-skeleton

## Why

Nothing runs end-to-end yet. Before hardening any single part we want a thin but
real pipe — ingest → retrieve → answer → CLI — so that "ask a question, get a
cited answer (or an honest miss)" works on a small corpus inside Docker, and
every later slice has something concrete to improve and measure. Covers FR-001,
FR-003, FR-010, FR-020, FR-021, FR-030, FR-052.

## What Changes

- The three interfaces `DocSource`, `Retriever`, `LLMProvider` (TC-002) with one
  concrete impl each (TC-003): local-markdown source, Qdrant-backed retriever,
  OpenAI-compatible LLM; embeddings via sentence-transformers.
- Recursive `.md` ingest (FR-001) that stores chunks with source metadata
  sufficient to cite (FR-003). Chunking is deliberately naive here; structure-
  aware chunking and idempotency come in `add-ingest-quality`.
- Retrieve relevant chunks for a question (FR-010).
- Answer generated ONLY from retrieved chunks, citing the source file (FR-020);
  honest "not in the corpus" when nothing relevant is found (FR-021).
- A CLI: question in → answer + source list out (FR-030).
- `docker compose up` brings up `app` + a separate Qdrant service with no manual
  steps (FR-052, TC-004, TC-005); every run happens in the container.

## Impact

- Affected specs (ADDED): `ingest`, `retrieve`, `answer`, `cli`, `deployment`.
- Affected code: new `askdocs/` package (`sources`, `chunking`, `embeddings`,
  `store`, `retriever`, `llm`, `answer`, `cli`), `Dockerfile`,
  `docker-compose.yaml`, `requirements.txt`, `tests/`.
- Dependencies: none (first slice). New packages: sentence-transformers,
  qdrant-client, markdown-it-py, httpx, pytest (+ pytest-cov, ruff).
