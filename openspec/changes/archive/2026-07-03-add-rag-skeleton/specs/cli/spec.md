## ADDED Requirements

### Requirement: CLI answers a question with its sources
The system SHALL provide a command-line interface, runnable in the container, that takes a user question as input and prints the grounded answer followed by the list of source files the answer drew from. For an out-of-corpus question it SHALL print the honest-miss answer. (FR-030)

#### Scenario: Question returns answer and sources
- **WHEN** the user runs the CLI with an in-corpus question
- **THEN** the CLI prints the answer and a list of the source file(s) it cited, and exits successfully

#### Scenario: Out-of-corpus question in the CLI
- **WHEN** the user runs the CLI with a question not covered by the corpus
- **THEN** the CLI prints the honest "not in the documentation" answer and exits successfully

#### Scenario: Missing question argument
- **WHEN** the user runs the CLI with no question
- **THEN** the CLI prints a usage message and exits with a non-zero status
