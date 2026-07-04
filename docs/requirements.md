# Requirements — askdocs

> Source of truth for scope. Derived from [`../../rag-hw/docs/prd.md`](../rag-hw/docs/prd.md)
> (the product PRD). Numbered FR/NFR/TC are preserved verbatim from the PRD.

## Scope rule (this delivery)

- **Delivery scope = every FR with status `shipped`** (the 15 FRs). These are
  exactly the requirements to implement here.
- **`accepted` NFR/TC = binding constraints** that every slice must honor.
- **`proposed` / `dropped` = out of scope**; recorded for the map, not
  implemented until the owner promotes them.

**`Phase` column = the active build front, not final scope.** A `shipped` FR is
`MVP` once its capability slice is in progress (spec authored → traced →
implemented); until then it is `Future`. This keeps the traceability chain
complete at every commit (no MVP FR without a spec/test) while specs are authored
as per-slice OpenSpec deltas. The full 15-FR scope and slice ownership live in
[`mvp-capability-plan.md`](mvp-capability-plan.md); FRs flip `Future → MVP` as
each slice activates. Currently active: **slice 4 (`add-sync-and-delivery`)**
(slices 1–3 archived) — the final slice; all 15 FRs become MVP.

## Product

**askdocs** — a local RAG "chat with your docs" tool. Input is a corpus of local
`.md` files. The user asks a question in the CLI and gets an answer grounded
ONLY in the corpus, citing the source file. If the corpus has no answer, the
system says so honestly instead of inventing one.

**Test domain — ГущоЛіт** (a fictional flying-cars-on-coffee-grounds project):
deliberately synthetic so a correct answer can only come from the corpus, never
from the model's own knowledge. Answering from "general knowledge" is a bug.

## Stack (from the shipped implementation)

Python · Qdrant (separate, ephemeral compose service) · sentence-transformers
embeddings · markdown-it-py structure-aware chunking · a single local
OpenAI-compatible LLM · pytest · everything in Docker Compose.

## Functional requirements (FR)

| ID | Phase | Requirement | Status |
|---|---|---|---|
| FR-001 | MVP | Ingest reads local `.md` files from the corpus directory (recursively). | shipped |
| FR-002 | MVP | Chunking preserves structural blocks (tables, code, sections) — no blind cut every N chars. | shipped |
| FR-003 | MVP | Chunks are written to the vector store with source metadata (file path, section) sufficient to cite. | shipped |
| FR-004 | MVP | Re-indexing the same files creates NO duplicates (idempotency). | shipped |
| FR-010 | MVP | Given a user question, the system finds relevant chunks in the vector store. | shipped |
| FR-020 | MVP | The answer is generated ONLY from the provided chunks, citing the source file. | shipped |
| FR-021 | MVP | If the corpus has no answer, the system replies honestly ("this is not in the docs") — no fabrication. | shipped |
| FR-030 | MVP | CLI: the user asks a question and gets an answer + a list of sources. | shipped |
| FR-040 | MVP | Golden set: 20–30 questions with known answers over the ГущоЛіт corpus. | shipped |
| FR-041 | MVP | Retrieval metric: verify the correct chunk is found for a question. | shipped |
| FR-042 | MVP | Anti-hallucination: for out-of-corpus questions the system answers "don't know", not a hallucination. | shipped |
| FR-050 | MVP | `README.md` at the repo root: what askdocs is, why it exists, how to run it. | shipped |
| FR-051 | MVP | `AGENTS.md` (and `CLAUDE.md`) with instructions for agents working in the repo. | shipped |
| FR-052 | MVP | Simple start: `docker compose up` brings the whole system up with no extra manual steps. | shipped |
| FR-060 | MVP | Continuous sync of the mounted directory: added/changed/deleted `.md` files are automatically re-indexed. | shipped |
| FR-100 | Future | Sources beyond local `.md` (Confluence, Jira, Google Drive) — future `DocSource` impls. | proposed |
| FR-101 | Future | Graph retrieval instead of vector — future `Retriever` impl. | proposed |
| FR-102 | Future | Multiple LLMs: external/cloud (Claude, GPT, Gemini) + local models — future `LLMProvider` impls. | proposed |
| FR-103 | Future | Web interface (v1 is CLI-only). | proposed |
| FR-104 | Future | Realtime re-indexing / background jobs — superseded by FR-060. | dropped |
| FR-105 | Future | Separate projects: multiple isolated corpora/collections, per-project vector-store namespace. | proposed |
| FR-106 | Future | Citations show the concrete source (file/section) next to the quote, not just an ordinal `[N]` rank marker. | proposed |

## Non-functional requirements (NFR)

Cross-cutting — every MVP slice must honor these.

| ID | Phase | Requirement | Status |
|---|---|---|---|
| NFR-001 | MVP | An answer without a source citation is a bug. | accepted |
| NFR-002 | MVP | "Not in the corpus" is a valid answer, not an error. | accepted |
| NFR-003 | MVP | Capability done-ness = green tests (pytest), not "seems to work". | accepted |
| NFR-004 | MVP | The system never answers from the model's "general knowledge" outside the corpus; the synthetic ГущоЛіт domain exists to prove this. | accepted |
| NFR-005 | Future | Offline embedding: drop `sentence-transformers`/`huggingface_hub` network calls to HF Hub (`HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`) — model is baked into the image. | proposed |

## Technical constraints (TC)

| ID | Phase | Constraint | Status |
|---|---|---|---|
| TC-001 | MVP | Implementation language — Python. | accepted |
| TC-002 | MVP | Three mandatory interfaces: `DocSource`, `Retriever`, `LLMProvider`. Logic above them is independent of the concrete impl. | accepted |
| TC-003 | MVP | v1 — one embedding provider, one vector store, one LLM. | accepted |
| TC-004 | MVP | Whole app in Docker (docker-compose): `app` service + vector-store service. Nothing in the host's system Python; every run (`ingest`, `cli`, `pytest`) is in a container. | accepted |
| TC-005 | MVP | Vector store is a separate compose service (not embedded). | accepted |
| TC-006 | MVP | Ingest idempotency tests run against a clean vector store (ephemeral volume or teardown before the run). | accepted |

## Glossary

- **Chunk** — a document fragment; the unit of storage and search in the vector store.
- **Golden set** — a fixed set of questions with known correct answers over the corpus; the basis for eval.
- **DocSource / Retriever / LLMProvider** — the three architectural interfaces: "give me documents" / "find what's relevant to the question" / "generate an answer from context".
