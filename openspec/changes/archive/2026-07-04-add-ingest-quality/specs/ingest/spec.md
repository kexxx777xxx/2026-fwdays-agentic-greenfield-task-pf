## ADDED Requirements

### Requirement: Chunking preserves structural block integrity
The system SHALL split documents along markdown structure (headings, paragraphs, tables, fenced code blocks, lists) and MUST NOT split blindly by character count. A table, fenced code block, or list group SHALL never be cut in the middle: when a section exceeds the size budget it SHALL be split only on block boundaries, and an atomic block larger than the budget SHALL remain whole as a single chunk. (FR-002)

#### Scenario: Table stays intact
- **WHEN** a document containing a markdown table is ingested
- **THEN** the entire table appears within exactly one chunk, never split across chunks

#### Scenario: Code block stays intact
- **WHEN** a document containing a fenced code block is ingested
- **THEN** the entire fenced code block appears within exactly one chunk

#### Scenario: Oversized section splits on block boundaries
- **WHEN** a section's blocks together exceed the size budget
- **THEN** it is stored as multiple chunks whose boundaries fall between whole blocks, and no single block is cut in the middle

### Requirement: Ingest is idempotent
Re-running ingest over an unchanged corpus SHALL leave the vector store with the same set of chunks: no duplicates, same count, same content. When a source file changes, its chunks SHALL be replaced; chunks of sections that no longer exist SHALL NOT remain in the store. (FR-004)

#### Scenario: Re-ingest of unchanged corpus
- **WHEN** ingest runs twice in a row over the same corpus, starting from a clean vector store
- **THEN** the chunk count and chunk contents in the store after the second run equal those after the first run

#### Scenario: Shrunk file leaves no stale chunks
- **WHEN** a file is ingested, then edited so it produces fewer chunks, then ingest runs again
- **THEN** the store contains only the chunks of the new version of the file
