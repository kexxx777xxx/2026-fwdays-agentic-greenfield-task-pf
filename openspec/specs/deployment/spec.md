# deployment Specification

## Purpose
TBD - created by archiving change add-rag-skeleton. Update Purpose after archive.
## Requirements
### Requirement: One command brings the whole system up in Docker
The entire application SHALL run in Docker Compose with an `app` service and a separate vector-store service. `docker compose up` SHALL bring the system up with no extra manual steps — the vector store starts, and the app image already contains its embedding model so no runtime download is required. Nothing SHALL be installed into the host's system Python; every run (`ingest`, `cli`, `pytest`) happens in the container. (FR-052, TC-004)

#### Scenario: Compose brings up app and vector store
- **WHEN** a user runs `docker compose up` on a clean checkout after building the image
- **THEN** the vector-store service and the `app` service start successfully with no manual setup steps

#### Scenario: Runs happen in the container
- **WHEN** a user runs `docker compose run --rm app python -m askdocs.cli "<question>"`
- **THEN** the command executes inside the container against the compose vector-store service and prints an answer

#### Scenario: No host Python usage
- **WHEN** the application or its tests are run
- **THEN** they run only inside the container, and nothing is installed into the host's system Python

