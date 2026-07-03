# rag-hw-pf — Agent Rules

# Stack (decided — ADR-0001)

Python 3.12 · Qdrant (separate, **ephemeral** Compose service) ·
`sentence-transformers` (`paraphrase-multilingual-MiniLM-L12-v2`, baked into the
image) · one OpenAI-compatible LLM over `httpx` · `markdown-it-py` chunking ·
`pytest`. Everything runs in Docker Compose — nothing in the host's Python.
Package versions in `requirements.txt` may differ from training data; read a
library's own docs before using an unfamiliar API.

Use `docs/requirements.md` for scope and `docs/mvp-capability-plan.md` for the
build order.

## Project Factory (works in any tool)

This project is delivered with **Project Factory**, a spec-driven multi-agent
framework that runs under any AI coding tool:

- **Claude Code:** the `project-factory` plugin — `/project-factory:init` (new)
  or `/project-factory:onboard` (existing).
- **Cursor:** the `project-factory` plugin / `.cursor/rules/` — same commands.
- **GitHub Copilot:** `.github/copilot-instructions.md` + the
  `/project-factory-init` / `-onboard` prompts.
- **Codex / others:** this `AGENTS.md` (read natively) + `.codex/prompts/`.

The deterministic loop — `scripts/check-*` (traceability, coverage, eval,
trajectory), git hooks, CI, OpenSpec specs, and the gates — is **identical in
every tool** (pure Node + git). Only orchestration differs: Claude Code fans out
subagents in parallel; elsewhere run review / eval / spec passes sequentially
with fresh context (maker ≠ checker). See `.project-factory/docs/portability.md`.

## Project Handoff Protocol

Before planning or implementing any substantive change, read:

1. `docs/current-state.md` for the latest persistent handoff and next-step guidance.
2. `docs/mvp-capability-plan.md` for the change sequence and capability scope.
3. `openspec/project.md` and the relevant files under `openspec/specs/`.
4. `docs/adr/` for accepted architecture decisions.

Keep `docs/current-state.md` current when a meaningful milestone happens:
an OpenSpec change is created/implemented/validated/archived; a capability
moves from planned to implemented; setup or validation expectations change;
an ADR is accepted. Write last update date/time (timezone: Europe/Kyiv) and
the current phase. `docs/current-state.md` is a handoff aid, not the source
of truth — if it conflicts with code/specs/tests, verify and update it.

## Context architecture (static vs dynamic)

This file is **static context** — paid for on every agent turn — so keep it to
durable cross-cutting rules. Per-domain detail, procedures, and large references
are **dynamic**: loaded on demand from the code, the spec, an on-demand skill, or
the framework's bundled docs. See `docs/context-architecture.md` for the split,
the token budget, and what to demote when this file grows past it.

## Module conventions

Single Python package `askdocs/`, one module per responsibility; the three
interfaces are ABCs and the logic above them never imports a concrete impl
(TC-002):

```text
askdocs/
  sources.py     # DocSource + LocalMarkdownSource        (FR-001)
  chunking.py    # structure-aware markdown split          (FR-002)
  embeddings.py  # EmbeddingProvider + SentenceTransformers (single source of the model name)
  store.py       # VectorStore + QdrantStore               (FR-003, FR-004)
  retriever.py   # Retriever + VectorRetriever             (FR-010)
  llm.py         # LLMProvider + OpenAICompatibleProvider  (FR-020/021)
  answer.py      # answer pipeline: cite source / honest miss
  cli.py         # terminal interface                      (FR-030)
  sync.py        # continuous corpus sync                  (FR-060)
  eval.py        # golden set + metrics                    (FR-040/041/042)
tests/           # pytest; tests/corpus = fixture ГущоЛіт; tests/golden.yaml
corpus/          # user corpus, mounted at /corpus on `docker compose up`
```

- One embedding provider, one vector store, one LLM in v1 (TC-003). The model
  name lives ONLY in `embeddings.py`.
- Every run is in a container (TC-004): `docker compose run --rm app <cmd>`.
  Qdrant is a separate, ephemeral service (TC-005/006).

## Correctness rules (this domain)

- **Answer without a source citation = bug** (NFR-001). Every answer names the
  file(s) it drew from.
- **"Not in the corpus" is a valid answer, not an error** (NFR-002). Honest miss
  over a confident wrong answer.
- **Never answer from the model's general knowledge** (NFR-004) — only from
  retrieved chunks. The synthetic ГущоЛіт domain exists to catch violations.
- Ingest is **idempotent** (FR-004): re-indexing identical files adds no
  vectors. Idempotency tests run against a clean store (`clean_store` fixture
  drops the collection first) (TC-006).
- Chunking never splits a structural block (table/code/section) mid-way (FR-002).
- External calls (Qdrant, the LLM endpoint) never fail silently: raise a typed
  error with cause; the CLI surfaces it, never swallows it.
- Retrieval and answer are validated by the eval harness (`eval.py` +
  `golden.yaml`), not just unit assertions — retrieval-hit + anti-hallucination
  are executable gates.

## Test-first (per slice)

Write the slice's pytest cases from the spec FIRST and confirm they FAIL (red);
then implement to green. Deterministic layers use a **mock `LLMProvider`**;
live-LLM tests are skip-gated (`LLM_LIVE=1`) so CI is green without a running
model. Never weaken a test to pass it — if a test contradicts the spec, change
it deliberately, not silently.

## Validation cadence

Run before and after substantial changes (everything in the container):

```bash
docker compose run --rm app pytest          # the whole battery (NFR-003)
docker compose run --rm app python -m askdocs.eval   # once evals exist
npx openspec validate --all --strict
node scripts/check-traceability.mjs
node scripts/check-eval-ratchet.mjs         # once evals exist — graded-quality bar
```

Do not archive an OpenSpec change before implementation AND a green pytest run
in the container. Keep `.env`/secrets private; never commit or print them.

## Evals (graded quality, not just correctness)

Tests assert exact results; evals grade *quality* a unit test can't — error
clarity, empty-state usability, copy tone — scored 0-100 against a rubric.

- Cases live in `evals/cases/*.eval.ts` (scenario + `produce()` + rubric +
  `@trace` ids). Group cases by `dimension`; the ratchet guards each dimension.
- The `eval-suite` workflow grades them with a fresh `eval-judge` agent
  (maker≠checker), writing `docs/qa/eval-report.md` + `evals/results/*.json`.
- `node scripts/check-eval-ratchet.mjs` guards the committed score in CI (no
  API key). Quality may ratchet up, never silently drop. Wire `check:eval`.
- **Recordings are kept** — they *illustrate* a case for humans; the eval is
  the *bar* that decides pass/fail. See `evals/README.md`.

## Environment notes

- macOS (Darwin 25.5), zsh. Docker Compose is the only supported runtime.
- Vector store: Qdrant, separate ephemeral Compose service (ADR-0001).
- LLM: an OpenAI-compatible endpoint at `LLM_BASE_URL` (default a local
  LM-Studio-style server). Not required for the deterministic pytest suite
  (mocked); set `LLM_LIVE=1` to exercise the live provider.
