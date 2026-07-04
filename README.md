# askdocs

**askdocs** is a local RAG tool — "chat with your documentation". Point it at a
folder of Markdown files, ask a question in the terminal, and get an answer that
is grounded **only** in your corpus and **cites the source file** it came from.
If the answer isn't in your docs, askdocs says so honestly instead of making
something up.

## Why it exists

General-purpose chatbots answer from their own training data — confidently, and
sometimes wrongly. askdocs answers **only from your files**, always names its
sources, and treats *"this isn't in the documentation"* as a valid answer rather
than a failure. A synthetic test domain (ГущоЛіт — flying cars that run on coffee
grounds) exists precisely to catch any answer that leaks from the model's general
knowledge.

## Stack

Python 3.12 · [Qdrant](https://qdrant.tech) vector store (separate, ephemeral
Compose service) · `sentence-transformers` embeddings
(`paraphrase-multilingual-MiniLM-L12-v2`, baked into the image) · one
OpenAI-compatible LLM · `markdown-it-py` structure-aware chunking · `pytest`.
Everything runs in Docker — nothing touches your host Python.

## Run it

Everything runs in the container. First build the image (bakes the embedding
model, so it runs offline afterwards):

```bash
docker compose build
```

Put your `.md` files in `./corpus/` (mounted at `/corpus`). Then bring the whole
system up — Qdrant starts and the sync watcher continuously indexes the corpus:

```bash
docker compose up                # self-populating, self-freshening index
```

Ask a question (in another terminal):

```bash
docker compose run --rm app python -m askdocs.cli "З чого зроблений двигун ГущоЛіт?"
```

You get an answer plus the list of source files it drew from — or an honest
"Цього в документації немає." for anything outside the corpus.

### Configure the LLM

askdocs talks to any OpenAI-compatible endpoint. Defaults target a local
LM-Studio-style server; override via environment:

```bash
LLM_BASE_URL=http://host.docker.internal:1234/v1 LLM_MODEL=your-model docker compose up
```

### Other commands

```bash
docker compose run --rm app python -m askdocs.ingest /corpus   # one-shot index
docker compose run --rm app python -m askdocs.eval             # quality report
docker compose run --rm app pytest                             # the test battery
```

## How it works

`DocSource` → structure-aware chunking → `sentence-transformers` embeddings →
Qdrant → `Retriever` (top-k with a relevance floor) → answer built **only** from
the retrieved chunks via the `LLMProvider`, with source citations. The three
interfaces (`DocSource`, `Retriever`, `LLMProvider`) are the stable seam, so the
store, embedder, or model can be swapped without touching the pipeline.

## Quality gates

Retrieval and honesty are measured, not assumed: a golden set of questions gates
retrieval hit-rate, and an anti-hallucination check confirms out-of-corpus
questions are refused (`docker compose run --rm app python -m askdocs.eval`).

## For contributors / agents

See [`AGENTS.md`](AGENTS.md) for the operating rules (module conventions,
correctness rules, validation cadence). The project is delivered spec-first: see
`docs/requirements.md`, `docs/mvp-capability-plan.md`, and `openspec/`.
