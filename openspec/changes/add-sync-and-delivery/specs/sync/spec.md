## ADDED Requirements

### Requirement: Continuous corpus synchronization
The system SHALL provide a continuous sync process, started by `docker compose up`, that reconciles a mounted `.md` directory with the vector store on a timer. A new `.md` file SHALL be indexed, an edited file SHALL be re-indexed with no stale chunks left behind, and a deleted file SHALL have its chunks removed from the store. An unchanged file SHALL NOT be re-embedded. (FR-060)

#### Scenario: New file is indexed
- **WHEN** a `.md` file is added to the watched directory and a sync pass runs
- **THEN** that file's chunks are present in the store and the pass reports it as added

#### Scenario: Edited file is re-indexed without stale chunks
- **WHEN** an already-indexed file is edited and a sync pass runs
- **THEN** the store contains only the new version's chunks (no content from the old version) and the pass reports it as updated

#### Scenario: Deleted file is removed
- **WHEN** an indexed file is deleted from the watched directory and a sync pass runs
- **THEN** that file's chunks are removed from the store and the pass reports it as deleted

#### Scenario: Unchanged corpus is a no-op
- **WHEN** a sync pass runs over a corpus with no changes since the last pass
- **THEN** nothing is re-embedded and the store is unchanged

### Requirement: The sync watcher survives transient failures
The sync loop SHALL NOT terminate on a single failed pass (e.g. a transient vector-store error): the failure SHALL be logged and the loop SHALL continue on the next tick, so synchronization stays continuous. The poll interval SHALL be validated so invalid configuration cannot hang the loop. (FR-060)

#### Scenario: A failing pass does not kill the watcher
- **WHEN** one reconciliation pass raises an error and further passes are scheduled
- **THEN** the error is caught and logged and the next pass still runs

#### Scenario: Invalid interval falls back to the default
- **WHEN** the configured poll interval is missing, non-numeric, zero, negative, or non-finite
- **THEN** the watcher uses the safe default interval instead of failing or hanging
