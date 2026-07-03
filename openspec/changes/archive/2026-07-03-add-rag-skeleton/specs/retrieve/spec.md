## ADDED Requirements

### Requirement: Retrieve finds relevant chunks for a question
The system SHALL provide a `Retriever` that, given a natural-language question, returns the most relevant stored chunks with their source metadata and a relevance score, ordered most-relevant first. Retrieval SHALL go through the `Retriever` interface so the concrete vector implementation can be swapped without changing callers. (FR-010, TC-002)

#### Scenario: Relevant chunk is retrieved
- **WHEN** the corpus contains a chunk answering a question and a query is issued for that question
- **THEN** that chunk is returned among the top results with its source metadata

#### Scenario: Results are ordered by relevance
- **WHEN** a query matches several chunks to differing degrees
- **THEN** the returned chunks are ordered from most to least relevant, each carrying a score

#### Scenario: No relevant chunks
- **WHEN** a query has no semantically relevant chunk in the corpus above the relevance threshold
- **THEN** the retriever returns an empty result set (not an error)
