# Project: rag-hw-pf

> OpenSpec project context. Kept lean; per-capability detail lives in
> `openspec/specs/<capability>/` and per-change folders under `openspec/changes/`.

## Purpose

TBD — captured at intake (Phase 1) by the requirements-analyst into
`docs/requirements.md`. This repository is governed by **Project Factory**: a
spec-driven, multi-agent delivery loop with deterministic gates.

## Stack

TBD — the application stack (framework, database, auth) is chosen at the stack
decision (Phase 3) and recorded as an ADR under `docs/adr/`. `init` is
stack-agnostic and installs only the loop.

## Conventions

- Requirements are numbered (FR/NFR/TC/BC) and traced through commits
  (`Refs:` / `Slice:` trailers) into specs, tests, and QA evidence.
- Each capability is delivered as an OpenSpec change (proposal → design → tasks),
  tests-first, then implemented to green, then adversarially reviewed.
- No change is archived before implementation AND a real-DB smoke test pass.

## Gates

The deterministic loop lives in `scripts/check-*.mjs`, the git hooks
(`.githooks/`), CI (`.github/workflows/ci.yml`), and the quality gates. See
`AGENTS.md` for the operating rules.
