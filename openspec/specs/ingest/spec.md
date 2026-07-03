# ingest Specification

## Purpose
TBD - created by archiving change add-rag-skeleton. Update Purpose after archive.
## Requirements
### Requirement: Ingest loads local markdown corpus through DocSource
The system SHALL provide an ingest command, runnable inside the app container, that loads documents exclusively through the `DocSource` interface. The v1 implementation SHALL read all `.md` files under a given corpus directory recursively. Files that are not `.md` SHALL be ignored. (FR-001)

#### Scenario: Markdown files are discovered recursively
- **WHEN** ingest runs against a corpus directory containing `.md` files in nested subdirectories
- **THEN** every `.md` file under the directory is ingested and every non-`.md` file is skipped

#### Scenario: Empty corpus
- **WHEN** ingest runs against a directory with no `.md` files
- **THEN** the command completes successfully and the vector store contains zero chunks for that corpus

### Requirement: Chunks are stored with source metadata
The system SHALL split each document into chunks, embed them, and store each chunk in the vector store with an embedding vector and metadata containing at minimum the source file path relative to the corpus root, the nearest heading trail, and the chunk index within the file. This metadata MUST be sufficient for a later answer to cite its source. (FR-003)

#### Scenario: Chunk carries source path and heading
- **WHEN** a `.md` file with headings is ingested
- **THEN** every stored chunk's metadata contains the file's relative path, a heading trail for the section the chunk came from, and the chunk's index

### Requirement: Vector store runs as a separate service
The vector store SHALL run as its own docker-compose service, separate from the `app` service. The application SHALL access it only through the `VectorStore` interface over the network; no embedded or in-process vector store is permitted. (TC-005)

#### Scenario: Ingest against the compose vector store service
- **WHEN** `docker compose run --rm app` executes ingest
- **THEN** chunks are persisted in the vector store service's collection and are readable through the store's API

### Requirement: Ingest tests run in the container against clean store state
Ingest tests SHALL be runnable via `docker compose run --rm app pytest` and SHALL execute against a clean vector store state, resetting the test collection before each test so results do not depend on prior runs. (TC-004, TC-006)

#### Scenario: Ingest test starts clean
- **WHEN** an ingest test runs after a previous test left data in the store
- **THEN** it resets its collection first and asserts only against the chunks it ingested

