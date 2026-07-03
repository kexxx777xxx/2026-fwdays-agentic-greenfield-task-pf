"""Answer pipeline: question -> Retriever -> LLMProvider -> grounded Answer.

Depends only on the interfaces. The model is fed ONLY the retrieved chunks and
told to answer solely from them, citing sources as [N]; if the chunks do not
contain the answer it emits NO_ANSWER, which becomes an honest refusal. When the
retriever returns nothing, we short-circuit to the refusal WITHOUT calling the
model (FR-021, NFR-002).
"""

import re
from dataclasses import dataclass

from askdocs.llm import LLMProvider
from askdocs.retriever import RetrievedChunk, Retriever

NO_ANSWER_MARKER = "NO_ANSWER"
REFUSAL_TEXT = "Цього в документації немає."

SYSTEM_PROMPT = (
    "Ти — асистент по документації проєкту. Відповідай українською.\n"
    "Використовуй ТІЛЬКИ надані фрагменти документації — жодних власних знань.\n"
    "Після кожного факту вказуй номер фрагмента-джерела у форматі [N].\n"
    f"Якщо відповіді на питання немає у фрагментах — виведи рівно {NO_ANSWER_MARKER} "
    "і більше нічого."
)

_CITATION_RE = re.compile(r"\[(\d+)\]")


@dataclass(frozen=True)
class Answer:
    text: str
    sources: list[str]
    found: bool


def _build_context(chunks: list[RetrievedChunk]) -> str:
    return "\n\n".join(
        f"[{i}] джерело: {chunk.source_path} ({chunk.heading})\n{chunk.text}"
        for i, chunk in enumerate(chunks, start=1)
    )


def _cited_sources(reply: str, chunks: list[RetrievedChunk]) -> list[str]:
    cited: list[str] = []
    for marker in _CITATION_RE.findall(reply):
        index = int(marker) - 1
        if 0 <= index < len(chunks) and chunks[index].source_path not in cited:
            cited.append(chunks[index].source_path)
    if cited:
        return cited
    # Model answered from context but cited nothing: the context files are still
    # the only possible sources (NFR-001 — an answer without a source is a bug).
    seen: list[str] = []
    for chunk in chunks:
        if chunk.source_path not in seen:
            seen.append(chunk.source_path)
    return seen


def answer_question(
    question: str, retriever: Retriever, llm: LLMProvider, k: int = 5
) -> Answer:
    chunks = retriever.retrieve(question, k=k)
    if not chunks:
        return Answer(text=REFUSAL_TEXT, sources=[], found=False)

    user_prompt = f"Фрагменти документації:\n\n{_build_context(chunks)}\n\nПитання: {question}"
    reply = llm.complete(SYSTEM_PROMPT, user_prompt)

    if NO_ANSWER_MARKER in reply:
        return Answer(text=REFUSAL_TEXT, sources=[], found=False)
    return Answer(text=reply, sources=_cited_sources(reply, chunks), found=True)
