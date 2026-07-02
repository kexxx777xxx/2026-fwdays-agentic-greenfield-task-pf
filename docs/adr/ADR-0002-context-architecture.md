# ADR-0002: Static/dynamic context boundary is a versioned, cost-bearing decision

- **Status:** Accepted
- **Date:** 2026-07-02
- **Deciders:** orchestrator + user

## Context

Static context (`CLAUDE.md` → `@AGENTS.md`) is paid for on every agent turn,
so it has direct TCO impact. Left ungoverned it grows without bound as
per-domain detail leaks into the always-loaded layer. The Project Factory loop
requires an explicit, enforced boundary between static context and the dynamic
context loaded on demand (code, specs, skills, framework docs).

## Decision

We will treat the static/dynamic context boundary as an architectural decision
with an enforced token budget. `AGENTS.md` holds only durable cross-cutting
rules (≤ 4k tokens); per-domain detail, procedures, and large references are
dynamic — loaded from `lib/<domain>/`, `openspec/specs/`, on-demand skills, or
bundled framework docs. See `docs/context-architecture.md`.

## Alternatives considered

| Option | Pros | Cons |
|---|---|---|
| Governed static budget (chosen) | Bounded per-turn cost; forces demotion | Requires periodic review |
| Put everything in AGENTS.md | Simple; one file | Unbounded token cost every turn |
| No shared rules file | Zero static cost | Agents re-derive conventions; drift |

## Consequences

- Per-turn context cost stays bounded and predictable.
- When `AGENTS.md` exceeds the budget, detail must be demoted to a skill/doc —
  a review cadence is required.
- Any change to the boundary or budget is recorded as a new ADR.
