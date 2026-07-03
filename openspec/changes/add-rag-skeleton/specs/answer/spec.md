## ADDED Requirements

### Requirement: Answers are grounded only in retrieved chunks and cite their source
The system SHALL generate answers through the `LLMProvider` interface using ONLY the chunks returned by the retriever as context. The answer MUST cite the source file(s) of the chunks it used. The system SHALL NOT answer from the model's general knowledge outside the provided chunks. (FR-020, NFR-001, NFR-004)

#### Scenario: Grounded answer cites its source
- **WHEN** a question is asked whose answer exists in the corpus
- **THEN** the answer is produced from the retrieved chunks and names the source file(s) it drew from

#### Scenario: Only retrieved context is passed to the model
- **WHEN** the answer pipeline builds the model prompt
- **THEN** the prompt contains only the retrieved chunks as source material and instructs the model to answer solely from them

### Requirement: Honest miss when the corpus has no answer
When retrieval yields no chunk relevant to the question, the system SHALL respond with an honest "this is not in the documentation" answer and SHALL NOT fabricate content or call the model to invent one. This honest miss is a valid answer, not an error. (FR-021, NFR-002)

#### Scenario: Out-of-corpus question
- **WHEN** a question is asked whose answer is not in the corpus
- **THEN** the system replies that it does not have this in the documentation, with no fabricated facts and no source citation

#### Scenario: Honest miss is not an error
- **WHEN** the system returns an honest miss
- **THEN** the command exits successfully (the miss is a normal outcome, not a failure)
