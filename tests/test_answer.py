"""@trace FR-020, FR-021 — grounded+cited answers, honest miss without the LLM.

Unit: uses a fake Retriever and a fake LLMProvider (no Qdrant, no live model).
"""

from askdocs.answer import REFUSAL_TEXT, answer_question
from askdocs.retriever import RetrievedChunk


class FakeRetriever:
    def __init__(self, chunks):
        self._chunks = chunks

    def retrieve(self, question, k=5):
        return self._chunks


class RecordingLLM:
    def __init__(self, reply):
        self.reply = reply
        self.calls = []

    def complete(self, system, user):
        self.calls.append((system, user))
        return self.reply


def _chunk(path, text, index=0):
    return RetrievedChunk(text=text, source_path=path, heading="H", chunk_index=index, score=0.9)


def test_grounded_answer_cites_source():
    chunks = [_chunk("proekt.md", "Двигун працює на кавовій гущі.")]
    llm = RecordingLLM("Двигун працює на кавовій гущі [1].")
    answer = answer_question("З чого двигун?", FakeRetriever(chunks), llm)

    assert answer.found is True
    assert answer.sources == ["proekt.md"]
    assert "[1]" in answer.text


def test_only_retrieved_context_in_prompt():
    chunks = [_chunk("proekt.md", "СЕКРЕТНИЙ_МАРКЕР_З_КОРПУСУ")]
    llm = RecordingLLM("ok [1]")
    answer_question("питання", FakeRetriever(chunks), llm)

    system, user = llm.calls[0]
    # the retrieved chunk text is the source material handed to the model
    assert "СЕКРЕТНИЙ_МАРКЕР_З_КОРПУСУ" in user
    # and the model is told to use only the fragments
    assert "ТІЛЬКИ" in system


def test_honest_miss_without_calling_the_model():
    llm = RecordingLLM("should not be called")
    answer = answer_question("поза корпусом", FakeRetriever([]), llm)

    assert answer.found is False
    assert answer.text == REFUSAL_TEXT
    assert answer.sources == []
    assert llm.calls == []  # no fabrication: the model was never invoked


def test_no_answer_marker_becomes_refusal():
    chunks = [_chunk("proekt.md", "нерелевантний текст")]
    llm = RecordingLLM("NO_ANSWER")
    answer = answer_question("щось інше", FakeRetriever(chunks), llm)

    assert answer.found is False
    assert answer.text == REFUSAL_TEXT
    assert answer.sources == []
