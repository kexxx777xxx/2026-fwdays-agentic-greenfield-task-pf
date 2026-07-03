## 1. Project scaffold + Docker (TC-001, TC-004, TC-005, FR-052)
- [x] 1.1 `requirements.txt`: sentence-transformers, qdrant-client, markdown-it-py, httpx, pytest, pytest-cov, ruff.
- [x] 1.2 `Dockerfile` (python:3.12-slim, non-root, bake the embedding model).
- [x] 1.3 `docker-compose.yaml`: `app` + separate ephemeral `qdrant` service (no named volume).
- [x] 1.4 `askdocs/__init__.py`; `pyproject.toml`/`pytest.ini` for pytest + markers.

## 2. Failing tests first (red) — written from the spec, before implementation
- [x] 2.1 `tests/corpus/` fixture (ГущоЛіт) + `conftest.py` with a `clean_store` fixture. `@trace TC-006`.
- [x] 2.2 `test_sources.py`: recursive `.md` discovery, non-`.md` ignored, empty corpus. `@trace FR-001`.
- [x] 2.3 `test_ingest.py`: chunks stored with `{path, heading, index}` metadata. `@trace FR-003`.
- [x] 2.4 `test_retriever.py` (integration): relevant chunk retrieved, ordered by score, empty on no-match. `@trace FR-010`.
- [x] 2.5 `test_answer.py`: grounded answer cites source; only retrieved chunks in prompt; honest miss without LLM call. Fake `LLMProvider`. `@trace FR-020, FR-021`.
- [x] 2.6 `test_cli.py`: question → answer + sources; out-of-corpus → honest miss; missing arg → usage + non-zero. `@trace FR-030`.
- [x] 2.7 `test_deployment.py`: compose config has `app` + separate `qdrant`, qdrant has no named volume. `@trace FR-052`.
- [x] 2.8 Run them — confirm RED (failing on assertions, not import errors).

## 3. Interfaces + concrete impls (green)
- [x] 3.1 `sources.py`: `DocSource` ABC + `LocalMarkdownSource` (FR-001).
- [x] 3.2 `chunking.py`: naive paragraph/size-budget chunker with heading trail (throwaway; replaced in add-ingest-quality).
- [x] 3.3 `embeddings.py`: `EmbeddingProvider` ABC + `SentenceTransformersProvider` (model name single-sourced here).
- [x] 3.4 `store.py`: `VectorStore` ABC + `QdrantStore` (upsert chunks + metadata, search) (FR-003, TC-005).
- [x] 3.5 `retriever.py`: `Retriever` ABC + `VectorRetriever` with a relevance threshold (FR-010).

## 4. Answer pipeline + CLI (green)
- [x] 4.1 `llm.py`: `LLMProvider` ABC + `OpenAICompatibleProvider` (httpx, `<think>` stripped) (FR-020).
- [x] 4.2 `answer.py`: build grounded prompt from retrieved chunks only; short-circuit to honest miss when retrieval is empty; return answer + cited sources (FR-020, FR-021).
- [x] 4.3 `cli.py`: parse question arg, wire the pipeline, print answer + sources; usage/non-zero on missing arg (FR-030).

## 5. Validation and archive prep
- [x] 5.1 `docker compose build`.
- [x] 5.2 `docker compose run --rm app pytest -q` — all green (mock LLM; live gated).
- [x] 5.3 `docker compose run --rm app ruff check askdocs tests`.
- [x] 5.4 `npx openspec validate add-rag-skeleton --strict` and `npx openspec validate --all --strict`.
- [x] 5.5 `node scripts/check-traceability.mjs` — FR-001/003/010/020/021/030/052 in the chain.
- [x] 5.6 Review-gate (code-reviewer + spec-compliance-auditor + security-reviewer); fix confirmed findings; re-run 5.2–5.5.
- [x] 5.7 Manual container smoke: ingest `tests/corpus`, ask an in-corpus and an out-of-corpus question via the CLI.
- [x] 5.8 Archive only after 5.1–5.7 pass: `npx openspec archive add-rag-skeleton --yes`.
