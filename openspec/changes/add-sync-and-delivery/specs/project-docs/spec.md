## ADDED Requirements

### Requirement: README explains and runs the project
The repository SHALL contain a `README.md` at its root that states what askdocs is, why it exists, and how to run it (the Docker Compose commands to build, ingest/sync, and ask a question). (FR-050)

#### Scenario: README covers purpose and how to run
- **WHEN** a new user opens `README.md`
- **THEN** it describes askdocs (a local, corpus-grounded RAG CLI), why it exists (grounded, cited answers; honest misses), and the `docker compose` commands to run it

### Requirement: Agent operating rules are present
The repository SHALL contain `AGENTS.md` (with `CLAUDE.md` pointing to it) giving agents the operating rules for working in the repo: the stack, module conventions, correctness rules, and the validation cadence. (FR-051)

#### Scenario: Agent rules exist and are wired
- **WHEN** an agent starts work in the repo
- **THEN** `AGENTS.md` states the stack and rules, and `CLAUDE.md` references it so tool-specific entry points resolve to the same rules
