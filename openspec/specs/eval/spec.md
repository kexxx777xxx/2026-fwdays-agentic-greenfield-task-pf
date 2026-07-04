# eval Specification

## Purpose
TBD - created by archiving change add-eval-harness. Update Purpose after archive.
## Requirements
### Requirement: Golden set of known questions over the corpus
The system SHALL provide a golden set of 20–30 questions over the ГущоЛіт corpus (FR-040). Each entry SHALL declare whether its answer is in the corpus; in-corpus entries SHALL name the single source file that answers them, and out-of-corpus entries SHALL name no source. The golden set SHALL be validated for well-formedness (counts, referenced files exist).

#### Scenario: Golden set is well-formed
- **WHEN** the golden set is loaded
- **THEN** it has 20–30 entries, every in-corpus entry names an existing source file, and every out-of-corpus entry names no source

### Requirement: Retrieval hit-rate metric
The system SHALL provide a retrieval metric that, for every in-corpus golden question, checks whether the expected source file appears among the top-k retrieved chunks, and reports the hit-rate. A test SHALL gate the hit-rate against a committed threshold so a retrieval regression fails the build (FR-041, NFR-003).

#### Scenario: Retrieval hit-rate meets the threshold
- **WHEN** the retrieval metric runs over the in-corpus golden questions against the ingested corpus
- **THEN** the fraction whose expected source is in the top-k results is at least the committed threshold, and any miss is named in the report

### Requirement: Anti-hallucination refusal-rate metric
The system SHALL provide an anti-hallucination metric that, for every out-of-corpus golden question, checks that the system refuses with an honest miss rather than fabricating an answer, and reports the refusal-rate. A test SHALL gate the refusal-rate against a committed threshold. Because it exercises the live LLM, the test MAY be skipped when no LLM endpoint is configured, so deterministic CI stays green (FR-042, NFR-002, NFR-004).

#### Scenario: Out-of-corpus questions are refused
- **WHEN** the anti-hallucination metric runs over the out-of-corpus golden questions with a live LLM
- **THEN** the fraction that produce an honest miss (no fabricated answer) is at least the committed threshold, and any question that was answered instead of refused is named in the report

#### Scenario: Deterministic CI without a model
- **WHEN** the test suite runs with no reachable LLM endpoint
- **THEN** the anti-hallucination test is skipped (not failed) while the deterministic retrieval gate still runs

